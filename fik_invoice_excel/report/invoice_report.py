# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class InvoiceReport(models.TransientModel):
    _name = 'invoice.report'

    journal_id = fields.Many2many('account.journal', string='Journal')
    start_date = fields.Date(string='From Date', required='1', help='select start date')
    end_date = fields.Date(string='To Date', required='1', help='select end date')


    def get_excel_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/account/excel_report/%s' % (self.id),
            'target': 'new',
        }