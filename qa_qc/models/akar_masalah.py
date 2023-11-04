from email.policy import default
from odoo import _,fields,api,models

class AkarMasalah(models.Model):

    _name = 'akar.masalah'
    _description = ''
    
    name = fields.Char(required=True)


