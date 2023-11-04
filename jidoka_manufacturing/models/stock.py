# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class StockMove(models.Model):
    _inherit = 'stock.move'

    mrp_sawmill_id = fields.Many2one('mrp.sawmill', string='Mrp Sawmill')