from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


import logging
_logger = logging.getLogger(__name__)

class JidokaMaterial(models.Model):
    _name = 'jidoka.material'
    _description = 'Material Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', compute='_compute_name', store=True)
        
    @api.depends('product_id', 'tebal', 'panjang', 'lebar', 'product_id.tebal')
    def _compute_name(self):
        for rec in self:
            if rec.product_id and rec.product_id.name:
                if rec.tebal and rec.panjang and rec.lebar:
                    rec.name = "{} ({}x{}x{})".format(
                        rec.product_id.name,
                        rec.tebal,
                        rec.panjang,
                        rec.lebar
                    )
                else:
                    rec.name = rec.product_id.name
            else:
                rec.name = False
    
    # sawmill_id = fields.Many2one(comodel_name='jidoka.sawmill', string='Sawmill')
    product_id = fields.Many2one('product.product', string='Product', required=True,
                domain="[('categ_id.is_material','=','board'),('tebal','>',0)]")
    

    lot = fields.Char(string='Lot', readonly=True)
    tebal = fields.Float(string='T (cm)', related='product_id.tebal', store=True)
    panjang = fields.Float(string='P (cm)', default=0)
    lebar = fields.Float(string='L (cm)', default=0)
    quantity = fields.Float(string='Done', store=True, compute="_compute_done", digits='Product Unit of Measure', copy=False)
    uom_id = fields.Many2one("uom.uom","Unit Of Measure", store=True, related='product_id.uom_id')
    
    process = fields.Selection(string='', selection=[('sawmill', 'Sawmill'), ('oven', 'Oven'),])
    
    location_id = fields.Many2one('stock.location', 'Stocks Location', help="Location where the system will stock the finished products.", tracking=True)
    
    wood_kind_id = fields.Many2one(comodel_name='jidoka.woodkind', string='Jenis Kayu', tracking=True)
    # TODO tidak perlu, remove me
    # tagcard_id = fields.Many2one(comodel_name='jidoka.tagcard', string='Tag Card')
    
    lot_id = fields.Many2one('stock.production.lot', string='Lot', tracking=True, copy=False)

    # def write(self, values):
    #     remove_tagcard = self._context.get('remove_tagcard', False)
    #     if remove_tagcard:
    #         self.recalculate_tagcard_material()
    #     result = super(JidokaMaterial, self).write(values)
    #     return result
    
    # def recalculate_tagcard_material(self):
    #     obj = self.env['jidoka.tagcard.material'].sudo().search([
    #         ('tagcard_id', '=', self.tagcard_id.id),
    #         ('product_id', '=', self.product_id.id),
    #         ('')
    #     ])
    
    @api.depends('product_id','tebal','panjang','lebar', 'product_id.tebal')
    def _compute_done(self):
        for rec in self:
            if rec.tebal:
                rec.quantity = (rec.tebal * rec.panjang * rec.lebar) / 1000000
            else:
                rec.quantity = 0
                
    # def _generate_lot_name(self):
    #     seq = self.env['ir.sequence'].next_by_code('jidoka.sawmill.line.lot')
    #     self.lot = '{}x{}x{}-{}'.format(self.tebal, self.panjang, self.lebar, seq)

class JidokaMaterial(models.Model):
    _name = 'jidoka.material.sticking'
    _description = 'Material Details'
    
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_template_id = fields.Many2one('product.template', string='Product', related='product_id.product_tmpl_id', required=True)
    tebal = fields.Float(string='T (cm)', related='product_template_id.size_tebal', store=True)
    lebar = fields.Float(string='L (cm)',related='product_template_id.size_lebar', store=True)
    panjang = fields.Float(string='P (cm)',related='product_template_id.size_panjang', store=True)
    total_meter_cubic = fields.Float(string='Cubic(M3)', related='product_id.total_meter_cubic', store=True)
    quantity_done = fields.Integer(string='Quantity Done')
    total_cubic = fields.Float(string='Total Cubic (M3)', compute="_compute_done", digits=(12,7))
    uom_id = fields.Many2one("uom.uom","Unit Of Measure", store=True, related='product_id.uom_id')


    @api.depends('quantity_done','total_meter_cubic','total_cubic')
    def _compute_done(self):
        for rec in self:
            if rec.quantity_done:
                rec.total_cubic = (rec.quantity_done * rec.total_meter_cubic)
            else:
                rec.total_cubic = 0


