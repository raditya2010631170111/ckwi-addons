from odoo import models, fields, api, _
from odoo.exceptions import UserError





class ProductKubikasi(models. Model):
    _name = 'product.kubikasi'
    _description = 'Product Kubikasi'
    _rec_name = "name"

    name = fields.Char("Name Kubikasi")
    product_id = fields.Many2one("product.template", "Product Componen")
    size_tebal = fields.Float("Size Tebal", )
    size_lebar = fields.Float("Size Lebar")
    size_panjang = fields.Float("Size Panjang")
    total_meter_cubic = fields.Float("Meter Cubic (M³)", digits=(12,5), compute="get_calc")
    total_meter_persegi = fields.Float("Meter Persegi (M²)", digits=(12,5), compute="get_calc")


    @api.depends('size_panjang', 'size_lebar','size_tebal')
    def get_calc(self):
        for cal in self:
            meter = cal.size_panjang * cal.size_lebar * cal.size_tebal
            cal.total_meter_cubic = (meter) / 1000000000 if meter > 0 else 0.00
            cal.total_meter_persegi = (meter) / 1000000 if meter > 0 else 0.00