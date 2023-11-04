from odoo import models, fields, api
from datetime import timedelta

class TypeSalesReportWizard(models.TransientModel):
    _name = "type.sales.report.wizard"

    filter = [
        ('penjualan_local', 'Penjualan Local'),
        ('penjualan_export', 'Penjualan Export'),
    ]
    type = fields.Selection(filter, required=True, string='Type Sales Report')
    start_date = fields.Date(string = 'Start Date')
    end_date = fields.Date(string = 'End Date')

    def action_print_invoice_local_report(self):
        return self.env.ref('base_accounting_kit.sample_costumer_invoice_local_xlsx').report_action(self)