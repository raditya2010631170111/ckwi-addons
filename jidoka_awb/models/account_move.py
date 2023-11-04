from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountMove1(models.Model):
    _inherit = "account.move"

    ups_awb_no = fields.Many2one('awb', 'UPS AWB NO')