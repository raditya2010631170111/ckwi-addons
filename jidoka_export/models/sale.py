from odoo import _, api, fields, models


class SaleOrderExport(models.Model):
    _inherit = 'sale.order'
    
    shipping_ins_ids = fields.Many2many(string='Shipping Ins', comodel_name='shipping.ins', relation='sale_order_shipping_ins_rel', column1='order_id', column2='shipping_id', compute='_compute_shipping_ins_ids' )
    shipping_line_ids = fields.One2many('shipping.ins.line', 'order_id', string='Shipping Ins Line',store=True)
        
    @api.depends('partner_id')
    def _compute_shipping_ins_ids(self):
        for rec in self:
            shipping_ins = self.env['shipping.ins'].search([('no_sc_ids','in', rec.id),('to_partner_id','=', rec.partner_id.id)])
            # shipping_ins = self.env['shipping.ins'].search([('no_sc_ids.name','=', rec.name),('to_partner_id','=', rec.partner_id.id)])
            
            rec.shipping_ins_ids = shipping_ins.ids
            
class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'
    
    shipping_ins_ids = fields.Many2many('shipping.ins', string='shipping', related='order_id.shipping_ins_ids')
            
    shipping_ins_line_ids = fields.One2many('shipping.ins.line', 'order_line_id', string='Shipping Ins Line')