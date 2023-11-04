from odoo import models, fields, api, _

class MaintenanceChecklistLine(models.Model):
    _name = 'maintenance.checklist.line'

    name = fields.Char('Checklist Name')
    desc = fields.Char('Description')
    maintenance_id = fields.Many2one('maintenance.request', 'Maintenance Request')