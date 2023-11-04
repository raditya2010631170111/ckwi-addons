# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class EquipmentPartLine(models.Model):
    _name = 'equipment.part.line'


    product_id = fields.Many2one('product.product','product')
    qty = fields.Float('Quantity')
    uom_id = fields.Many2one('uom.uom','UOM')
    maintenance_equipment_id = fields.Many2one('maintenance.equipment','Equipment')
    maintenance_id = fields.Many2one('maintenance.request', 'Maintenance Request')


    @api.onchange('product_id')
    def onchange_product_data(self):
        for part_line_id in self:
            part_line_id.uom_id = part_line_id.product_id.uom_id


class MaintenanceConsumedMaterial(models.Model):
    _name = 'maintenance.consumed.material'
    _description = 'Meintenance Consumed Material'

    product_id = fields.Many2one('product.product', string='Product')
    description = fields.Char(string='Description')
    product_uom_qty = fields.Integer('Quantity', default=1.0 )
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id, string='Company', readonly=True)
    consumed_maintenance_request_id = fields.Many2one('maintenance.request', string='Consumed Materials')


    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.description = self.product_id.name

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    is_consume = fields.Boolean('Is Consume Maintenance')

class Location(models.Model):
    _inherit = "stock.location"

    consume_maintenance = fields.Boolean('Consume Maintenance')
    
class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    consume_maintenance = fields.Boolean(string="Is Consume Maintenance Operation ?")
