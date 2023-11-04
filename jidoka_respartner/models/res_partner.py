from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    payment_term_jidoka_id = fields.Many2one('account.payment.term', string='Terms')
    is_local = fields.Boolean('Is Local')
    logo_report_qc = fields.Binary('Logo Report Tes Pengujian')



# class ResCompany(models.Model):
#     _inherit = 'res.company'

#     logo_report_qc = fields.Binary('logo_report_qc')