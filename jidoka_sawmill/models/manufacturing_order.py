# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tools import OrderedSet
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES

SIZE_BACK_ORDER_NUMERING = 3

class JidokaManufacturingOrderSawmill(models.Model):
    _inherit = 'mrp.production'
    
    material_process = fields.Selection([
        ('sawmill', 'Sawmill'),
        ('vacuum', 'Vacuum'),
        ('oven', 'Oven'),
    ], string='Material Process', default=False)
    
    sawmill_id = fields.Many2one(comodel_name='jidoka.sawmill', string='Sawmill')
    
    def _default_odoo_onchange_mrp(self):
        self._onchange_product_qty()
        self._onchange_bom_id()
        self._onchange_date_planned_start()
        self._onchange_move_raw()
        self._onchange_move_finished_product()
        self._onchange_move_finished()
        self._onchange_location()
        self._onchange_location_dest()
        self.onchange_picking_type()
        self._onchange_producing()
        self._onchange_lot_producing()
        self._onchange_workorder_ids()
    
    
    
class JidokaSawmillMOStockMove(models.Model):
    _inherit = 'stock.move'
    
    def action_show_details(self):
        self.ensure_one()
        action = super().action_show_details()
        if self.env.context.get('default_raw_material_production_id') or self.env.context.get('default_production_id'):
            action['context']['show_lots_m2o'] = True
        return action