# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
from collections import defaultdict
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.addons.stock.models.stock_rule import ProcurementException
from dateutil.relativedelta import relativedelta


class MrpProduction(models.Model):
    _inherit = "mrp.production"


    so_id = fields.Many2one('sale.order','Sale Origin',default=False,copy=False)
    custom_parent_mo_id = fields.Many2one('mrp.production','Parent MO Custom')
    mrp_production_child_count = fields.Integer("Number of generated MO", compute='_compute_mrp_production_child_count')
    custom_child_mo_ids = fields.One2many('mrp.production','custom_parent_mo_id','Custom Child MO')

    def _compute_mrp_production_child_count(self):
        for production in self:
            if production.custom_child_mo_ids:
                production.mrp_production_child_count = len(production.custom_child_mo_ids)
            else:
                production.mrp_production_child_count = len(production.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids)


    def action_view_mrp_production_childs(self):
        self.ensure_one()
        if not self.custom_child_mo_ids:
            mrp_production_ids = self.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.ids
        else:
            mrp_production_ids = self.custom_child_mo_ids.ids
        action = {
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
        }
        if len(mrp_production_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': mrp_production_ids[0],
            })
        else:
            action.update({
                'name': _("%s Child MO's") % self.name,
                'domain': [('id', 'in', mrp_production_ids)],
                'view_mode': 'tree,form',
            })
        return action


    def _get_date_planned_custom(self, product_id, company_id, values):
        format_date_planned = fields.Datetime.now()
        date_planned = format_date_planned - relativedelta(days=product_id.produce_delay)
        date_planned = date_planned - relativedelta(days=company_id.manufacturing_lead)
        if date_planned == format_date_planned:
            date_planned = date_planned - relativedelta(hours=1)
        return date_planned



    def create_child_mo_rule(self):
        for data in self:
            for line in data.bom_id.bom_line_ids:
                date_planned = data._get_date_planned_custom(line.product_id, data.company_id, {})
                date_deadline = date_planned + relativedelta(days=data.company_id.manufacturing_lead) + relativedelta(days=line.product_id.produce_delay)
                qty = data.product_qty * line.product_qty
                qty_mts = 0
                if line.product_id.reordering_min_qty:
                    qty_mts = line.product_id.reordering_min_qty
                if line.product_id.reordering_max_qty: 
                    qty_mts = line.product_id.reordering_max_qty
                qty+=qty_mts
                if line.product_id.qty_available < qty:
                    qty-= line.product_id.qty_available
                    bom = self.env['mrp.bom']._bom_find(
                        product=line.product_id,
                        company_id=data.company_id.id,
                        bom_type='normal',
                    )
                    if bom:
                        if not bom[0].picking_type_id:
                            raise ValidationError("Please set picking type on BOM")
                        if not bom[0].picking_type_id.default_location_dest_id or not bom[0].picking_type_id.default_location_dest_id:
                            raise ValidationError("Please set location on picking type BOM")
                
                        value = {
                            'origin': data.name,
                            'custom_parent_mo_id':data.id,
                            'product_id': line.product_id.id,
                            'product_qty': qty,
                            'product_uom_id': line.product_id.uom_id.id,
                            'location_src_id': bom[0].picking_type_id.default_location_src_id.id,
                            'location_dest_id': bom[0].picking_type_id.default_location_dest_id.id,
                            'bom_id': bom[0].id,
                            'date_deadline': date_deadline,
                            'date_planned_start': date_planned,
                            'picking_type_id': bom[0].picking_type_id.id,
                            'company_id': data.company_id.id,
                            'user_id': False,
                        }
                        productions = self.env['mrp.production'].with_user(SUPERUSER_ID).sudo().with_company(data.company_id.id).create(value)
                        self.env['stock.move'].sudo().create(productions._get_moves_raw_values())
                        self.env['stock.move'].sudo().create(productions._get_moves_finished_values())
                        productions._create_workorder()
                        productions.filtered(lambda p: p.move_raw_ids).action_confirm()
                        productions.create_child_mo_rule()

