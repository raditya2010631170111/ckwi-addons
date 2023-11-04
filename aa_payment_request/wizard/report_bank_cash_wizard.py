from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ReportBankCashWizard(models.TransientModel):
    _name = 'report.bank.cash.wizard'
    _description = 'Report Bank and Cash'

    account_id = fields.Many2one(
        'account.journal', string="Kas")
    account_ids = fields.Many2many(
        'account.account', string="Account", required=True)
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    company_id = fields.Many2one(
        'res.company', string="Company")
    work_location = fields.Many2one(
        'jidoka.worklocation', string="Location")

    def action_report(self):
        if self.date_from:
            if not self.date_to:
                raise ValidationError(_("Date To harus diisi!"))
        elif self.date_to:
            if not self.date_from:
                raise ValidationError(_("Date From harus diisi!"))
        array = []
        for x in self.account_ids:
            array.append(x.id)
        if self.date_from and self.date_to and self.account_ids[0]:
            pettycash = self.env['account.move.line'].search([('account_id', 'in',
                                                             array),
                                                              ('date', '>=',
                                                             self.date_from),
                                                              ('date', '<=',
                                                             self.date_to),
                                                              ])
            if not pettycash:
                raise ValidationError(_("Petty cash not found!"))
            return self.env.ref('aa_payment_request.report_bank_cash_action').report_action(self)
        else:
            pettycash = self.env['account.move.line'].search([('account_id', 'in',
                                                             array)
                                                              ])
            if not pettycash:
                raise ValidationError(_("Petty cash not found!"))
            return self.env.ref('aa_payment_request.report_bank_cash_action').report_action(self)
