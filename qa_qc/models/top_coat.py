from odoo import _,fields,api,models

class TopCoat(models.Model):

    _name = 'top.coat'
    _description = ''
    
    name = fields.Char(required=True)
