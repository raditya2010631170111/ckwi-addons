from odoo import models, fields, api, _

class BoardProductTemplate(models.Model):
    _inherit = 'product.template'

    tebal = fields.Float(string='Tebal (cm)')

    # TODO perlu?
    @api.onchange('tebal')
    def onchange_tebal(self):
        for product in self.product_variant_ids:
            product.tebal = self.tebal

    
class BoardProduct(models.Model):
    _inherit = 'product.product'
    
    tebal = fields.Float(string='Tebal (cm)', related='product_tmpl_id.tebal', store=True)
    
class BoardProductCategory(models.Model):
    _inherit = 'product.category'
    
    is_material = fields.Selection([
        ('board', 'Board'),
        ('stick', 'Stick'),
    ], string='Is Material', default=False)