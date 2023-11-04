from odoo import models, fields, api,  _

class StockPickingTagcard(models.Model):
    _inherit = 'stock.picking'
    
    tagcard_id = fields.Many2one (comodel_name='jidoka.tagcard', string='Tagcard', readonly=True)
    date_done = fields.Datetime(string='Date Done')
    card = fields.Char(string='Card')
    