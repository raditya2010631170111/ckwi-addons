from odoo import models, fields, api, _

class MaintenanceChecklist(models.Model):
	_name = 'maintenance.checklist'

	name = fields.Char('Checklist Name')
	desc = fields.Char('Description')
	equipment_id = fields.Many2one('maintenance.equipment',string='Equipment')
	maintenance_id = fields.Many2one('maintenance.request', 'Maintenance Request')

