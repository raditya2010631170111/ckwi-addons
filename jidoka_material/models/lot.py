from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from collections import Counter, defaultdict


from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
# from odoo.tools import float_is_zero


import logging
_logger = logging.getLogger(__name__)


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    material_process = fields.Selection([
        ('sawmill', 'Sawmill'),
        ('vacuum', 'Vacuum'),
        ('oven', 'Oven'),
    ], string='Material Process', default=False)
    
    wood_kind_id = fields.Many2one(comodel_name='jidoka.woodkind', string='Jenis Kayu', tracking=True)
    panjang = fields.Float('Panjang')
    lebar = fields.Float('Lebar')
    tebal = fields.Float('Tebal', related='product_id.tebal')
    is_material = fields.Boolean(string='Is Material', compute="_compute_is_material", store=True)
    product_qty = fields.Float(digits='Product Unit of Measure')
    # TODO remove me, tdk ada Pcs!
    # qty_received = fields.Float('Pcs' , compute='_compute_qty_received')
    panjang_value = fields.Float('Panjang', compute='_compute_plt_value', store=True) 
    lebar_value = fields.Float('Lebar', compute='_compute_plt_value', store=True) 
    tebal_value = fields.Float('Tebal', compute='_compute_plt_value', store=True)
    size_value = fields.Char('Dimensi', compute='_compute_plt_value', digits=(12,8), store=True)
    result_quantity = fields.Float('Result Quantity', compute='_compute_plt_value', store=True)
    # TODO buat apa???
    # quantity = fields.Float('Quantity', related='product_qty')

    # NOTE karena tidak ada relasi, kita gunakan quant_ids
    @api.depends('quant_ids', 'quant_ids.quantity')
    def _compute_plt_value(self):
        for record in self:
            move_lines = self.env['stock.move.line'].search([
                ('lot_id', '=', record.id), ('state', '=', 'done')])
            record.panjang_value = sum(move_lines.mapped('panjang'))
            record.lebar_value = sum(move_lines.mapped('lebar'))
            record.tebal_value = sum(move_lines.mapped('tinggi'))
            record.size_value = str(record.panjang_value * record.lebar_value * record.tebal_value)
            if record.panjang_value and record.lebar_value and record.tebal_value:
               record.result_quantity = ((record.product_qty * 1000000) / (record.panjang_value * record.lebar_value * record.tebal_value))
            else:
                record.result_quantity = 0.0
                 
    @api.depends('product_id')
    def _compute_is_material(self):
        for rec in self:
            if rec.product_id and rec.product_id.categ_id and rec.product_id.categ_id.is_material != False:
                rec.is_material = True
            else:
                rec.is_material = False
    

class StockMoveLineLot(models.Model):
    _inherit = "stock.move.line"
    
    def _create_and_assign_production_lot(self):
            """ Creates and assign new production lots for move lines."""
            lot_vals = []
            # It is possible to have multiple time the same lot to create & assign,
            # so we handle the case with 2 dictionaries.
            key_to_index = {}  # key to index of the lot
            key_to_mls = defaultdict(lambda: self.env['stock.move.line'])  # key to all mls
            for ml in self:
                key = (ml.company_id.id, ml.product_id.id, ml.lot_name)
                key_to_mls[key] |= ml
                if ml.tracking != 'lot' or key not in key_to_index:
                    key_to_index[key] = len(lot_vals)
                    lot_vals.append({
                        'company_id': ml.company_id.id,
                        'name': ml.lot_name,
                        'product_id': ml.product_id.id,
                        'panjang': ml.panjang,
                        'lebar': ml.lebar,
                    })

            lots = self.env['stock.production.lot'].create(lot_vals)
            for key, mls in key_to_mls.items():
                mls._assign_production_lot(lots[key_to_index[key]].with_prefetch(lots._ids))  # With prefetch to reconstruct the ones broke by accessing by index