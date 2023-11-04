from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductProduct(models. Model):
    _inherit = 'product.product'
    _description = 'product M3'

    meter_cubic = fields.Many2one('uom.uom','UoM ㎥')
    # size_tebal = fields.Float("Size Tebal", )
    # size_lebar = fields.Float("Size Lebar")
    # size_panjang = fields.Float("Size Panjang")


class ProductTemplate(models. Model):
    _inherit = 'product.template'
    # _description = 'product M3'

    meter_cubic = fields.Many2one('uom.uom','UoM ㎥')
    is_componen = fields.Boolean('Is Componen')
    parent_id = fields.Many2one("product.template", "Product Componen")
    kubikasi_id = fields.Many2one("product.kubikasi","Kubikasi")
    size = fields.Selection([
        ('size_cm', 'cm'),
        ('size_mm', 'mm'),
    ], string='Dimensi Uom')
    rasio = fields.Integer('Rasio')
    # size_value = fields.Float('Size Value',compute="_compute_size_value", digits=(12,8))
 
    # @api.depends('size', 'size_value', 'size_tebal', 'size_lebar', 'size_panjang')
    # def _compute_size_value(self):
    #     for record in self:
    #         # size_tebal = record.size_tebal or 0
    #         size_lebar = record.size_lebar or 0
    #         size_panjang = record.size_panjang or 0
    #         if record.size == 'size_cm':
    #             record.size_value =  size_lebar * size_panjang
    #         else:
    #             record.size_value = ( size_lebar * size_panjang) / 100

    size_tebal = fields.Float("Size Tebal")
    size_lebar = fields.Float("Size Lebar")
    size_panjang = fields.Float("Size Panjang")
    total_meter_cubic = fields.Float("Meter Cubic (M³)", digits=(12,5), compute="get_calc_mcubic",
        store=True)
    total_meter_persegi = fields.Float("Meter Persegi (M²)", digits=(12,5), compute="get_calc_mpersegi", 
        store=True)
    total_meter = fields.Float('Meter (M)', digits=(12,5), compute="_compute_total_meter", store=True)

    @api.depends('rasio', 'size', 'size_panjang', 'size_lebar', 'size_tebal')
    def get_calc_mcubic(self):
        for record in self:
            if record.size == 'size_cm':
                record.total_meter_cubic = (((record.size_panjang * record.size_lebar) * record.size_tebal )/ record.rasio)  / 1000000 if record.rasio != 0 else 0.00
            else:
                record.total_meter_cubic = (((record.size_panjang * record.size_lebar) * record.size_tebal ) / record.rasio) / 1000000000 if record.rasio != 0 else 0.00


    @api.depends('rasio', 'size','size_panjang','size_lebar', 'size_tebal')
    def get_calc_mpersegi(self):
        for record in self:
            if record.size == 'size_cm':
                record.total_meter_persegi = (((record.size_panjang/record.rasio) * (record.size_lebar/record.rasio)* 2 ) + ((record.size_panjang/record.rasio) * (record.size_tebal/record.rasio) * 2 ) + ((record.size_lebar/record.rasio) * (record.size_tebal/record.rasio) * 2 ))/ 10000 if record.rasio != 0 else 0.00
            else:
                record.total_meter_persegi = (((record.size_panjang/record.rasio) * (record.size_lebar/record.rasio)* 2 ) + ((record.size_panjang/record.rasio) * (record.size_tebal/record.rasio) * 2 ) + ((record.size_lebar/record.rasio) * (record.size_tebal/record.rasio) * 2 ))/ 1000000 if record.rasio != 0 else 0.00


    @api.depends('size_panjang', 'rasio', 'size', 'qty_available')
    def _compute_total_meter(self):
        for record in self:
            if record.size == 'size_cm':
                record.total_meter = (record.size_panjang / 100) if record.rasio != 0 else 0.00
            else:
                record.total_meter = (record.size_panjang / 1000) if record.rasio != 0 else 0.00

    @api.onchange("kubikasi_id")
    def get_kubikasi(self):
        for tc in self:
            kbc = tc.kubikasi_id
            tc.size_tebal = kbc.size_tebal
            tc.size_panjang = kbc.size_panjang
            tc.size_lebar = kbc.size_lebar
            tc.total_meter_cubic = kbc.total_meter_cubic
            tc.total_meter_persegi = kbc.total_meter_persegi

    # def get_calc(self):
    #     for cal in self:
    #         # meter = cal.size_panjang * cal.size_lebar * cal.size_tebal
    #         meter = cal.size_value * cal.size_tebal
    #         # mpersegi = cal.size_panjang * cal.size_lebar
    #         mpersegi = cal.size_value
    #         cal.total_meter_cubic = (meter) / 1000000 if meter > 0 else 0.00
    #         cal.total_meter_persegi = (mpersegi) / 10000 if meter > 0 else 0.00

    # @api.depends('size_value', 'size_tebal')
    # def get_calc(self):
    #     for cal in self:
    #         meter = cal.size_value * cal.size_tebal
    #         rasio = cal.rasio
    #         mpersegi = cal.size_value
    #         total_meter_cubic_value = (meter) / 1000000 
    #         total_meter_persegi_value = (mpersegi) / 10000
    #         cal.total_meter_cubic = (total_meter_cubic_value) / (rasio) if cal.size_value > 0 and rasio != 0 else 0.00
    #         cal.total_meter_persegi = (total_meter_persegi_value) / (rasio) if cal.size_value > 0 and rasio != 0 else 0.00

    @api.onchange("is_componen")
    def ls_change(self):
        if not self.is_componen:
            self.size_tebal = 0
            self.size_panjang = 0
            self.size_lebar = 0
            self.total_meter_cubic = 0
            self.total_meter_persegi = 0
            self.kubikasi_id = False