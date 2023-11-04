from email.policy import default
from odoo import _,fields,api,models

class AttachImgs(models.Model):
    _name = 'img.att'
    parent_field_name = fields.Char(string='Name ')
    attachment_img = fields.Binary()
