from odoo import models, fields, api, _



class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    container_line_ids = fields.One2many(comodel_name='container.operation.line', inverse_name='move_id', 
        string='Container Line')
    qty_in_container = fields.Float(string='Qty in Container', compute='_compute_qty_in_container',
        store=True)
    qty_available_container = fields.Float(string='Qty Available Container', compute='_compute_qty_in_container',
        store=True)
    
    shipping_ins_ids = fields.Many2many('shipping.ins', string='shipping_ins', related='picking_id.shipping_ins_ids',)
    state_si = fields.Char('state_si')
    
    shipping_line_ids = fields.One2many(comodel_name='shipping.ins.line', inverse_name='move_id', string='Shipping Ins' )
    
    qty_si = fields.Float(string='Qty SI',
        compute='_compute_qty_in_shiping_ins_line')

    
    # custom name get
    def name_get(self):
        if not self.env.context.get('display_for_container'):
            return super().name_get()
        res = []
        for move in self:
            res.append((move.id, '%s%s%s' % (
                move.picking_id.name and '%s / ' % move.picking_id.name or '',
                move.product_id.code and '%s : ' % move.product_id.code or '',
                move.product_id.name and '%s' % move.product_id.name or ''
                )))
        return res
    
    @api.depends('shipping_line_ids', 'shipping_line_ids.qty_si', 'state')
    def _compute_qty_in_shiping_ins_line(self):
        for rec in self:
            if rec.state != 'done':
                # qty_si = sum(rec.shipping_ins_line_ids.filtered(lambda line: line.state == 'done').mapped('qty_si'))
                qty_si = sum(rec.shipping_line_ids.filtered(lambda line: line.state == 'done').mapped('qty_si'))
                rec.qty_si = qty_si
            else:
                rec.qty_si = 0.0
    
    @api.depends(
        'container_line_ids',
        'container_line_ids.product_container_qty',
        'container_line_ids.container_operation_id'
        )
    def _compute_qty_in_container(self):
        for rec in self:
            qty_in_container = sum(rec.container_line_ids.mapped('product_container_qty'))
            rec.qty_in_container = qty_in_container
            rec.qty_available_container = rec.quantity_done - qty_in_container
    
    def action_view_containers(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Container Lines',
            'view_mode': 'list,form',
            'res_model': 'container.operation.line',
            'domain': [('id', 'in', self.container_line_ids.ids)],
        }
    
    def action_view_shipping_ins_line(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Shipping Ins Lines',
            'view_mode': 'list,form',
            'res_model': 'shipping.ins.line',
            # 'domain': [('id', 'in', self.shipping_ins_line_ids.ids)],
            'domain': [('id', 'in', self.shipping_line_ids.ids)],
        }
        
    