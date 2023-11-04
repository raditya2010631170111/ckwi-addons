from odoo import models, fields, api
from datetime import timedelta

class IndonesiaTaxWizard(models.TransientModel):
    _name = "indonesia.tax.wizard"

    filter = [
        ('out_invoice', 'Customer'),
        ('in_invoice', 'Vendor'),
        ('both', 'Both'),
    ]
    type = fields.Selection(
        filter,
        required=True,
        string='Type'
    )
    start_date = fields.Date(
        string = 'Start Date'
    )

    end_date = fields.Date(
        string = 'End Date'
    )

    def action_print_indonesia_tax_report(self):
        return self.env.ref('jidoka_indonesia_taxs.report_indonesia_tax_action').report_action(self)