from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

class StockMoveLineInherit(models.Model):
    _inherit = 'stock.move.line'
    
    qty_si = fields.Float('Qty SI', related='move_id.qty_si', store=True)   
            
    
            
    
    
    
    
    