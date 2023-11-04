from odoo import _, api, fields, models
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    shipping_ins_ids = fields.Many2many('shipping.ins', string='Shipping Ins', related='sale_id.shipping_ins_ids')
    
    is_qty_si = fields.Boolean('Is Qty SI', default= False,
        compute='_compute_is_qty_si' )
    
    @api.depends('move_ids_without_package.qty_si')
    def _compute_is_qty_si(self):
        for rec in self:
            # rec.is_qty_si = False
            jml_qty_si = sum(self.move_ids_without_package.mapped('qty_si'))
            if jml_qty_si > 0:
                rec.is_qty_si = True
            else:
                rec.is_qty_si = False

    def calculate_si(self):
        # import pdb;pdb.set_trace()
        
        # move_line = self.move_line_ids
        for r in self:
            # for move_line in r.move_line_ids:
            #     # jml_shipping = len(self.move_lines.shipping_ins_ids)
            #     move_qty_si = r.move_lines
            #     move_line
            #     move_line.qty_done = move_line.qty_si
            if r.move_ids_without_package:
                for move in r.move_ids_without_package:
                    if move.move_line_ids:
                        for move_lines in move.move_line_ids:
                            move_qty_si = move.qty_si
                            move_lines.qty_si = move_qty_si
                            move_lines.qty_done = move_lines.qty_si
                    else:
                        move_lines = self.env['stock.move.line'].search([('move_id', '=', move.id)])
                        move_line = move_lines.create({
                            'picking_id': r.id,
                            'move_id':move.id,
                            'product_id': move.product_id.id,
                            'product_uom_id': move.product_uom.id,
                            'qty_si': move.qty_si,
                            'qty_done': move.qty_si,
                            'location_id': move.location_id.id,
                            'location_dest_id': move.location_dest_id.id,
                        })
                        _logger.info('------------------------')
                        _logger.info('move_id: %s' % move.id)
                        _logger.info('product_id: %s' % move.product_id.name)
                        
          
        return True
    
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        # log
        _logger.info('------------------------')
        _logger.info('------------validated------------')
        for r in self:
            if r.shipping_ins_ids:
                for shipping_ins in r.shipping_ins_ids.filtered(lambda line: line.state == 'done'):
                    shipping_ins.write({
                        'is_do': True
                    })
            
        return res
    