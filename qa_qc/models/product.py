from odoo import models, fields, api, _

class BoardProductCategory(models.Model):
    _inherit = 'product.category'
    # lev_aql_id = fields.Many2one(string='Level AQL', comodel_name='level.aql',)
    lev_aql_id = fields.Selection(string='Level AQL', selection=[('bpsj', 'BPSJ'),
    ('bpc', 'BPC'),
    ('bj', 'BJ')])