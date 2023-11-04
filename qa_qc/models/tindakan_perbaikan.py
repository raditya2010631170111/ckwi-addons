from email.policy import default
from odoo import _,fields,api,models

class TindakanPerbaikan(models.Model):

    _name = 'tindakan.perbaikan'
    _description = ''
    
    name = fields.Char(required=True)


