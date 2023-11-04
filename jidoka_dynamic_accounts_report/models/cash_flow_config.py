# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CashFlowConfig(models.Model):
    _name = 'cash.flow.config'
    _description = 'Cash Flow Config for advance CF Report'
    _rec_name = 'report_type'
    _order = 'sequence ASC'

    sequence = fields.Integer(string='Sequence', default=10)
    report_type = fields.Selection(
        selection=[
            # Operating Activities
            ## Adjustment
            ('Depreciation Of Fixed Assets', 'Depreciation Of Fixed Assets'),
            ('Correction Retained Earnings', 'Correction Retained Earnings'),
            ## Operating Assets
            ('Account Receivable', 'Account Receivable'),
            ('Other Receivable', 'Other Receivable'),
            ('Inventory', 'Inventory'),
            ('Prepaid Tax', 'Prepaid Tax'),
            ('Advance and Prepayment', 'Advance and Prepayment'),
            ('Refundable Deposit - Non Current', 'Refundable Deposit - Non Current'),
            ('Other Assets', 'Other Assets'),
            ## Operating Liabilities
            ('Account Payable', 'Account Payable'),
            ('Taxes Payable', 'Taxes Payable'),
            ('Accrued Payable', 'Accrued Payable'),
            ('Other Payable', 'Other Payable'),
            # Investing Activities
            ('Fixed Assets', 'Fixed Assets'),
            ('Intangible Assets', 'Intangible Assets'),
            # Financing Activities
            ('Related Party Loan', 'Related Party Loan'),
            ('Additional Shared', 'Additional Shared'),
            ],
        string='Report Type',
        default='total', required=True,)
    account_ids = fields.Many2many(
        comodel_name='account.account', string='Accounts')
    description = fields.Text(string='Description',)
    calculation_type = fields.Selection([
        ('type_1','Akumulasi dari PL hingga bulan berjalan'),
        ('type_2','BS akhir tahun lalu - BS periode ini'),
        ('type_3','BS periode ini - BS akhir tahun lalu')
    ], default='type_1')

    # constraint, make sure only one record with report_type
    _sql_constraints = [
        ('report_type_unique',
            'UNIQUE(report_type)',
            'Only one record with report_type is allowed!'),
    ]