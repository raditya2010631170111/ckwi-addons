from odoo import _, api, fields, models
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
import json

class JidokaTagCardSticking(models.Model):
    _name = 'jidoka.sticking'
    _description = 'jidoka.sticking'

    no_tagcard_id = fields.Many2one(comodel_name='stock.quant.package',string='No. Tag Card', store=True, required=True, tracking=True) #, inverse_name='sticking_id'
    product_id = fields.Many2one('product.product', string='Product', required=True, related='lot_id.product_id')
    product_sticking_id = fields.Many2one('product.product', string='Product', required=True, related='no_tagcard_id.quant_ids.product_id')
    wood_kind_id = fields.Many2one('jidoka.woodkind',"Jenis Kayu", store=True, related='product_id.wood_kind_id')
    tgl_masuk = fields.Date('Date', required=True)
    quantity = fields.Float(string='Quantity',  store=True,related='lot_id.product_qty') 
    product_uom_id = fields.Many2one("uom.uom", store=True,related='lot_id.product_uom_id') #related='lot_id.uom_id'
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')
    ], string='State',default='draft', tracking=True)
    package_id = fields.Many2one(
        'stock.quant.package', 'Source Package', ondelete='restrict',
        check_company=True,
        domain="[('location_id', '=', location_id)]",related='no_tagcard_id.quant_ids.package_id')
    location_id = fields.Many2one('stock.location', 'Products Location', help="Location where the system will stock the finished products.", required=True, tracking=True,related='no_tagcard_id.location_id')
    lot_id = fields.Many2one('stock.production.lot', string='LOT / SN', readonly=False, store=True) #,related='no_tagcard_id.quant_ids.lot_id'
    lot_id_domain = fields.Char(compute="_compute_lot_id_domain", readonly=True, store=False) 

    # lotsn_id = fields.Many2one('stock.production.lot', string='LOT / SN', readonly=False, store=True, related='stock_quant_ids.lot_id')
    # stock_quant_ids = fields.One2many('stock.quant',string='Stock Quant',related='no_tagcard_id.quant_ids.stock_quant_id')
    location_dest_id = fields.Many2one('stock.location', 'Finished Products Location',required=True)
    product_line_ids = fields.One2many(comodel_name='jidoka.material.sticking', string='Product Detail', 
                                       inverse_name='sticking_id')
    total_pcs = fields.Integer(string='Total PCS', store=True, compute="_compute_total_pcs", digits='Product Unit of Measure', copy=False)
    total_m3 = fields.Float(string='Total M3', store=True, compute="_compute_total_m3", copy=False, digits=(12,7))


    @api.depends('product_line_ids')
    def _compute_total_pcs(self):
        for rec in self:
            total_pcs = 0
            for line in rec. product_line_ids:
                total_pcs += line.quantity_done
            rec.total_pcs = total_pcs


    @api.depends('product_line_ids')
    def _compute_total_m3(self):
        for rec in self:
            total_m3 = 0
            for line in rec. product_line_ids:
                total_m3 += line.total_cubic
            rec.total_m3 = total_m3

    @api.depends('no_tagcard_id')
    def _compute_lot_id_domain(self):
        for rec in self:
            lot_id_domain = []
            if rec.no_tagcard_id:
                lot_id_domain = [('id', 'in', rec.no_tagcard_id.quant_ids.lot_id.ids)]
            check_products = self.env['stock.production.lot'].sudo().search(lot_id_domain)
            if rec.lot_id not in check_products:
                rec.lot_id = False
            rec.lot_id_domain = json.dumps(lot_id_domain)

    # @api.depends('lot_id')
    # def _compute_lot_id(self):
    #     for rec in self:
    #         if rec.lot_id: 
    #             lot_id = rec.lot_id.id
    #             check_products = self.env['stock.quant'].sudo().search([
    #                 ('lot_id', '=', rec.lot_id.id),
    #                 ('tagcard_id', '=', rec.package_id.id),
    #                 ('product_id', '=', rec.product_id.id)])
    #             if rec.lot_id.id not in check_products.mapped('lot_id.id'):
    #                 rec.write({'lot_id': False})



    def action_validate(self):
        if self.state == 'draft':
            self.write( { 
                         'state': 'done',
                         })


class JidokaStickingMaterial(models.Model):
    _inherit = 'jidoka.material.sticking'
    
    sticking_id = fields.Many2one(comodel_name='jidoka.sticking', string='Sticking')   
    mo_sawmill_id = fields.Many2one(comodel_name='mrp.production', string='MO Sawmill')
     
# class JidokaStickingQuant(models.Model):
#     _inherit = 'stock.quant.package'

#     sticking_id = fields.Many2one(comodel_name='jidoka.sticking', string='Sticking')

