from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


import logging
_logger = logging.getLogger(__name__)


class StockQuantInherit(models.Model):
    _inherit = 'stock.quant'
    
    # tag card data
    name_code_gudang = fields.Char ('NAME CODE GUDANG', related='tagcard_id.name_code_gudang')
    tagcard_id = fields.Many2one('jidoka.tagcard', string='Tag Card')
    tagcard_type = fields.Selection(related='tagcard_id.tagcard_type', 
        string='TagCard Type', readonly=True, store=True)
    # field untuk jenis sawn timber
    panjang = fields.Float('Panjang', related='lot_id.panjang')
    lebar = fields.Float('Lebar', related='lot_id.lebar')
    tebal = fields.Float('Tebal', related='lot_id.tebal')
    # field untuk jenis selain sawn timber
    p_panjang = fields.Float('Size Panjang', related='product_id.size_panjang')
    p_lebar = fields.Float('Size Lebar', related='product_id.size_lebar')
    p_tebal = fields.Float('Size Tebal', related='product_id.size_tebal')
    # kayu / material data
    certification_id = fields.Many2one('res.certification', string='Certification',
        related='product_id.certification_id', store=True)
    is_material = fields.Boolean('Is Material', related='lot_id.is_material', store=True)
    wood_kind_id = fields.Many2one(comodel_name='jidoka.woodkind', string='Jenis Kayu', 
        related='lot_id.wood_kind_id', store=True)
    wood_kind_product_id = fields.Many2one(comodel_name='jidoka.woodkind', 
        string='Produk Jenis Kayu', related='product_id.wood_kind_id', store=True)
    # ADJUST digits
    quantity = fields.Float(digits='Product Unit of Measure')
    inventory_quantity = fields.Float(digits='Product Unit of Measure')
    available_quantity = fields.Float(digits='Product Unit of Measure')
    
    is_selected = fields.Boolean(string="#", default=False)
    # TODO remove me, untuk apa?
    selected_count = fields.Integer(string="Selected Count", compute='_compute_selected_count')
    
    @api.depends('is_selected')
    def _compute_selected_count(self):
        for record in self:
            selected_records = self.search([('is_selected', '=', True)])
            record.selected_count = len(selected_records)

    def check_all(self):
        records = self.env['stock.quant'].search([], limit=40, order="id asc")
        for record in records:
            record.is_selected = True

    def des_check_all(self):
        for record in self:
            record.is_selected = False
    
class StockQuantPackageInherit(models.Model):
    _inherit = 'stock.quant.package'
    _rec_name = 'name_code_gudang'
    
    tagcard_id = fields.Many2one(comodel_name='jidoka.tagcard', string='Tagcard', 
        readonly=True, store=True, copy=False)
    # Change title???
    name = fields.Char(string='Tag Card Reference', store=True, required=True)
    code_gudang = fields.Char('Code Gudang', related='location_id.code_gudang')
    name_code_gudang = fields.Char(string='No. Tag Card - Code Gudang', 
        compute='_compute_name_code_gudang', store=True, readonly=True, tracking=True)
    certification_id = fields.Many2one('res.certification',string='Certification',
        related='tagcard_id.certification_id', store=True)
    # show single product of this package
    product_id = fields.Many2one(comodel_name='product.product', string='Product',
        compute='_compute_product_id', store=True)
    
    transaction_date = fields.Datetime('Transaction Date')
    
    @api.depends('quant_ids', 'quant_ids.product_id')
    def _compute_product_id(self):
        for record in self:
            if record.quant_ids:
                record.product_id = record.quant_ids[0].product_id.id
            else:
                record.product_id = False

    @api.depends('name', 'code_gudang')
    def _compute_name_code_gudang(self):
        for record in self:
            code_gudang = record.code_gudang or ''
            name = record.name or ''
            if code_gudang and name:
                record.name_code_gudang = f"{code_gudang}{name}"
            else:
                record.name_code_gudang = None

    def action_tagcard_transfer(self):
        self.ensure_one()
        return {
            'name': _('Tag Card Transfer'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tagcard.transfer.wizard',
            'target': 'new',
            # 'context': {'default_quant_package_id': self.id},
        }

