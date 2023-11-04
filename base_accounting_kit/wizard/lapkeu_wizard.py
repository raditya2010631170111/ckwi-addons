from odoo import models, fields, api
from datetime import timedelta

class LapkeuWizard(models.TransientModel):
    _name = "lapkeu.wizard"

    filter = [
        ('neraca', 'Neraca'),
        ('perincian_neraca', 'Perincian Neraca'),
        ('laba_rugi', 'Laba Rugi'),
        ('perincian_rl', 'Perincian RL'),
    ]
    type = fields.Selection(filter, required=True, string='Type LapKeu')
    start_date = fields.Date(string = 'Start Date')
    end_date = fields.Date(string = 'End Date')

    def action_print_report_lapkeu(self):
        return self.env.ref('base_accounting_kit.report_lapkeu_xlsx').report_action(self)