from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT



class WizMultiLineSawmill(models.TransientModel):
    _name = 'wiz.multi.line.sawmill'
    _description = 'Generate Multi Line Sawmill Wizard'
    
    line_ids = fields.One2many(comodel_name='wiz.multi.line.sawmill.master', inverse_name='wiz_id', string='Details')
    sawmill_id = fields.Many2one(comodel_name='jidoka.sawmill', string='sawmill')
    history_ids = fields.One2many(comodel_name='jidoka.material', inverse_name='wiz_ref', string='Details')
    wiz_ref = fields.Reference(selection=[('wiz.multi.line.sawmill', 'Wizard')])
    
    
    def action_generate_line(self):
        self.sawmill_id.line_ids.unlink() 
        if not self.line_ids:
            raise UserError(_("Please fill in the product details that will be generated."))
        if self.sawmill_id and self.sawmill_id.state != 'done':
            sawmill_line = self.env['jidoka.material']
            for line in self.line_ids:
                if line.total <= 0:
                    raise UserError(_("Total must be positive"))
                for i in range(line.total):
                    sawmill_line.create({
                        'sawmill_id': self.sawmill_id.id,
                        'product_id': line.product_id.id,
                        'lot': line.lot,
                        'tebal': line.tebal,
                        'lebar': line.lebar,
                        'panjang': line.panjang,
                        'quantity': line.quantity,
                        'uom_id': line.uom_id.id,
                        'source_mo_id': line.mo_to_sawmill_id.id,
                        'total': 1,
                    })
    
    
class WizMultiLineSawmillMaster(models.TransientModel):
    _name = 'wiz.multi.line.sawmill.master'
    _description = 'Generate Multi Line Sawmill Wizard'

    wiz_id = fields.Many2one(comodel_name='wiz.multi.line.sawmill', string='Wizard')
    product_id = fields.Many2one('product.product', string='Product', required=True,
        domain="[('categ_id.is_material','=','board'),('tebal','>',0)]")
    lot = fields.Char(string='Lot', readonly=True)
    tebal = fields.Float(string='T (cm)', related='product_id.tebal', store=True)
    panjang = fields.Float(string='P (cm)', default=0)
    lebar = fields.Float(string='L (cm)', default=0)
    quantity = fields.Float(string='Done', store=True, compute="_compute_done", digits='Product Unit of Measure', copy=False)
    uom_id = fields.Many2one("uom.uom","Unit Of Measure", store=True, related='product_id.uom_id')
    total = fields.Integer(string='Total', required=True, default=1, store=True)
    mo_to_sawmill_id = fields.Many2one(comodel_name='mrp.production', string='MO', 
        domain="[('state', 'in', ['confirmed', 'draft']), ('product_id.categ_id.is_material','=','board'),('product_id.tebal','>',0)]")
    mo_quantity = fields.Float(string='MO Qty', digits='Product Unit of Measure', copy=False)


    @api.depends('product_id','panjang','lebar', 'product_id.tebal')
    def _compute_done(self):
        for rec in self:
            if rec.tebal:
                rec.quantity = (rec.tebal * rec.panjang * rec.lebar) / 1000000
            else:
                rec.quantity = 0

    @api.onchange('mo_to_sawmill_id')
    def _onchange_mo_to_sawmill_id(self):
        if self.mo_to_sawmill_id:
            self.product_id = self.mo_to_sawmill_id.product_id
            self.tebal = self.mo_to_sawmill_id.product_id.tebal
            self.uom_id = self.mo_to_sawmill_id.product_uom_id
            self.mo_quantity = self.mo_to_sawmill_id.product_qty