from odoo import models, fields, api, _

class AWB(models.Model):
    _name = 'awb'
    _description = 'AWB'
    _rec_name = 'name'

    name = fields.Char('Name')
    batch_transfer_id = fields.Many2one('stock.picking.batch', 'Batch Transfer ID')
    transfer_ids = fields.Many2many('stock.picking', string='Transfer Ids')
