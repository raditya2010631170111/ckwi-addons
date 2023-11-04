from odoo import models, fields, api, _


class SawmillStockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    material_process = fields.Selection([
        ('sawmill', 'Sawmill'),
        ('vacuum', 'Vacuum'),
        ('oven', 'Oven'),
    ], string='Material Process', default=False)