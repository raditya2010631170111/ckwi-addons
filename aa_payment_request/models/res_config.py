from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    apr_amount = fields.Monetary(string="Amount Payment Request")
    aap_amount = fields.Monetary(string="Amount Advance Payment")
    journal_settlement_id = fields.Many2one('account.journal', string="Journal Settlement")
    ttd_finance_accounting = fields.Many2one(comodel_name='res.users', string='Finance & Accounting')
    dirut_id = fields.Many2one('hr.employee', string='DIREKTUR UTAMA', store=True)
    dirkeu_id = fields.Many2one('hr.employee', string='DIREKTUR KEUANGAN', store=True)
    fin_id = fields.Many2one('hr.employee', string='FINANCE', store=True)
    acc_id = fields.Many2one('hr.employee', string='ACCOUNTING', store=True)
    active = fields.Boolean(string='Active', default=True)
    
    fax = fields.Char(string='Fax')
    


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    apr_amount = fields.Monetary(string="Payment Request", related="company_id.apr_amount", readonly=False, currency_field='currency_id')
    aap_amount = fields.Monetary(string="Advance Payment", related="company_id.aap_amount", readonly=False, currency_field='currency_id')
    journal_settlement_id = fields.Many2one('account.journal', related="company_id.journal_settlement_id", string="Journal Settlement", readonly=False)
    ttd_finance_accounting = fields.Many2one(comodel_name='res.users', string='Finance & Accounting', related='company_id.ttd_finance_accounting', readonly=False)
