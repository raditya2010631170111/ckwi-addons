# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
from collections import defaultdict
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.addons.stock.models.stock_rule import ProcurementException
from dateutil.relativedelta import relativedelta


class StockRule(models.Model):
    _inherit = "stock.rule"

    action = fields.Selection(
        selection_add=[("split_procurement", "Choose between MTS and MTO"),('manufacture_mto_mts','Manufacture MTS')],
        ondelete={"split_procurement": "cascade","manufacture_mto_mts": "cascade"}
    )
    mts_rule_id = fields.Many2one("stock.rule", string="MTS Rule", check_company=True)
    mto_rule_id = fields.Many2one("stock.rule", string="MTO Rule", check_company=True)

    @api.model
    def _run_manufacture_mto_mts(self, procurements):
        productions_values_by_company = defaultdict(list)
        errors = []
        
        for procurement, rule in procurements:
            bom = self._get_matching_bom(procurement.product_id, procurement.company_id, procurement.values)
            if not bom:
                raise ValidationError('There is no Bill of Material of type manufacture or kit found for the product %s. Please define a Bill of Material for this product.') % (procurement.product_id.display_name,)
            mo = rule._prepare_mo_vals(*procurement, bom)
            if not bom.picking_type_id:
                raise ValidationError("Please set picking type on BOM")
            if not bom.picking_type_id.default_location_dest_id or not bom.picking_type_id.default_location_dest_id:
                raise ValidationError("Please set location on picking type BOM")
            mo['so_id'] = procurement.values['group_id'].sale_id.id
            mo['location_src_id'] = bom.picking_type_id.default_location_src_id.id
            mo['location_dest_id'] = bom.picking_type_id.default_location_dest_id.id
            mo['picking_type_id'] = bom.picking_type_id.id
            mo['orderpoint_id'] = False
            productions_values_by_company[procurement.company_id.id].append(mo)
        
        if errors:
            raise ProcurementException(errors)


        for company_id, productions_values in productions_values_by_company.items():
            # create the MO as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
            productions = self.env['mrp.production'].with_user(SUPERUSER_ID).sudo().with_company(company_id).create(productions_values)
            # productions.picking_ids.filtered(lambda p: p.picking_type_id.code != 'outgoing').write({'sale_id':False})
            self.env['stock.move'].sudo().create(productions._get_moves_raw_values())
            self.env['stock.move'].sudo().create(productions._get_moves_finished_values())
            productions._create_workorder()
            productions.filtered(lambda p: p.move_raw_ids).action_confirm()
            productions.create_child_mo_rule()
            # for i in productions.bom_id.bom_line_ids:


            # for production in productions:
            #     origin_production = production.move_dest_ids and production.move_dest_ids[0].raw_material_production_id or False
            #     orderpoint = production.orderpoint_id
            #     if orderpoint:
            #         production.message_post_with_view('mail.message_origin_link',
            #                                           values={'self': production, 'origin': orderpoint},
            #                                           subtype_id=self.env.ref('mail.mt_note').id)
            #     if origin_production:
            #         production.message_post_with_view('mail.message_origin_link',
            #                                           values={'self': production, 'origin': origin_production},
            #                                           subtype_id=self.env.ref('mail.mt_note').id)
        return True

    @api.constrains("action", "mts_rule_id", "mto_rule_id")
    def _check_mts_mto_rule(self):
        for rule in self:
            if rule.action == "split_procurement":
                if not rule.mts_rule_id or not rule.mto_rule_id:
                    msg = _(
                        "No MTS or MTO rule configured on procurement " "rule: %s!"
                    ) % (rule.name,)
                    raise ValidationError(msg)
                if (
                    rule.mts_rule_id.location_src_id.id
                    != rule.mto_rule_id.location_src_id.id
                ):
                    msg = _(
                        "Inconsistency between the source locations of "
                        "the mts and mto rules linked to the procurement "
                        "rule: %s! It should be the same."
                    ) % (rule.name,)
                    raise ValidationError(msg)

    def get_mto_qty_to_order(self, product, product_qty, product_uom, values):
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        src_location_id = self.mts_rule_id.location_src_id.id
        product_location = product.with_context(location=src_location_id)
        virtual_available = product_location.virtual_available
        qty_available = product.uom_id._compute_quantity(virtual_available, product_uom)
        if float_compare(qty_available, 0.0, precision_digits=precision) > 0:
            if (
                float_compare(qty_available, product_qty, precision_digits=precision)
                >= 0
            ):
                return 0.0
            else:
                return product_qty - qty_available
        return product_qty

    def _run_split_procurement(self, procurements):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        moves_values_by_company = defaultdict(list)
        for procurement, rule in procurements:
            procure_method = rule.procure_method
            move_values = rule._get_stock_move_values(*procurement)
            move_values['procure_method'] = procure_method
            # domain = self.env["procurement.group"]._get_moves_to_assign_domain(
               
            # )
            domain = self.env["procurement.group"]._get_moves_to_assign_domain(
               procurement.company_id.id
            )
            needed_qty = procurement.product_qty
            qty_mts = 0
            if procurement.product_id.reordering_min_qty:
                qty_mts = procurement.product_id.reordering_min_qty
            if procurement.product_id.reordering_max_qty: 
                qty_mts = procurement.product_id.reordering_max_qty
                
            needed_qty+=qty_mts

            if procurement.product_id.qty_available < needed_qty:
                needed_qty-=procurement.product_id.qty_available
                mts_procurement = procurement._replace(product_qty=needed_qty)
                getattr(self.env["stock.rule"], "_run_%s" % rule.mts_rule_id.action)(
                    [(mts_procurement, rule.mts_rule_id)]
                )

            getattr(self.env["stock.rule"], "_run_%s" % rule.mto_rule_id.action)(
                 [(procurement, rule.mto_rule_id)]
            )

            


        return True
