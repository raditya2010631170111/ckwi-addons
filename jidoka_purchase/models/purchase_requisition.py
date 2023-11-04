# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    warehouse_id = fields.Many2one('stock.warehouse', string='Digunakan Untuk',default=lambda self: self.env.with_company(self.env.company).user.property_warehouse_id)

    def action_in_progress(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("You cannot confirm agreement '%s' because there is no product line.", self.name))
        if self.type_id.quantity_copy == 'none' and self.vendor_id:
            for requisition_line in self.line_ids:
                if requisition_line.price_unit <= 0.0:
                    raise UserError(_('You cannot confirm the blanket order without price.'))
                if requisition_line.product_qty <= 0.0:
                    raise UserError(_('You cannot confirm the blanket order without quantity.'))
                requisition_line.create_supplier_info()
            self.write({'state': 'ongoing'})
        else:
            self.write({'state': 'in_progress'})
        # Set the sequence number regarding the requisition type
        if self.name == 'New':
            seq = self.env['ir.sequence'].next_by_code('seq.purchase.requisition.ckwi')
            self.name = 'PP-'+self.warehouse_id.code or ''+str(seq)

    def action_create_purchase_order(self):
        self.ensure_one()
    
        action = {
            'name': _('Request for Quotations'),
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'domain':[('requisition_id','=',self.id)],
            'context': {
                "default_requisition_id":self.id,
                "default_user_id": False,
                "default_warehouse_id":self.warehouse_id.id,
                "default_pr_date":self.ordering_date,
                "default_origin":self.origin,
                },
            'target': 'self'
        }

        return action

class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    default_code = fields.Char('Code',related='product_id.default_code')
    qty_available = fields.Float('Qty On Hand',related='product_id.qty_available')
    item = fields.Char('Item')
    note = fields.Char('Note')