from email.policy import default
from odoo import _,fields,api,models

class LevelAql(models.Model):

    _name = 'level.aql'
    _description = ''
    
    name = fields.Char(required=True)
    type = fields.Char(string='Type')
    multi = fields.Boolean(default=False)

