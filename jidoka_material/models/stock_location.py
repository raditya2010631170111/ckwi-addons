from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class StockLocation(models.Model):
    _inherit = 'stock.location'

    material_process = fields.Selection([
        ('sawmill', 'Sawmill'),
        ('vacuum', 'Vacuum'),
        ('oven', 'Oven'),
    ], string='Material Process')
    code_gudang = fields.Char('Code Gudang', store=True)
    