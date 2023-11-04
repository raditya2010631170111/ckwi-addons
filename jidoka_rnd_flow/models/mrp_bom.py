from odoo import models, fields, api, _

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    design_detail_id = fields.Many2one('design.detail', string='Design Detail')

class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    design_detail_id = fields.Many2one('design.detail', string='Design Detail')
    active = fields.Boolean(default=True)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_code = fields.Char(string='Code', store=True)


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    product_code = fields.Char('Code',related='product_tmpl_id.product_code', store=True)
#     design_detail_bom_line_ids = fields.One2many(
#         comodel_name='mrp.bom.line',
#        inverse_name= 'product_id',
#         string='Design Detail Bom Lines')