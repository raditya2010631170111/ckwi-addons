from odoo import models, fields, _

class PreventiveReport(models.TransientModel):
    _name = "preventive.report.wizard"

    category_id = fields.Many2many('maintenance.equipment.category', string='Bagian')
    date_from = fields.Date(string='From Date', required='1', help='select from date')
    date_to = fields.Date(string='To Date', required='1', help='select To date')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def action_xlsx_report (self):
        domain = []

        category_id = self.category_id
        if category_id:
            # domain += [('category_id', '=', category_id.id)]
            domain += [('category_id', '=', category_id.id), ('maintenance_type', '=', 'preventive')]
        date_from = self.date_from
        if date_from:
            domain += [('schedule_date', '>=', date_from)]
        date_to = self.date_to
        if date_to:
            domain += [('schedule_date', '<=', date_to)]

        preventive = self.env['maintenance.request'].search_read(domain)
        data = {
            'preventive': preventive,
            'from_data': self.read()[0]
        }
        return self.env.ref('fik_equipment_maintenance.report_preventive_xlsx').report_action(self, data=data)
