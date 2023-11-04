from odoo import models, fields, api, _

class ProjectTask(models.Model):
	_inherit = 'project.task'

	sequence_num = fields.Char('Sequence', readonly=True)
	is_order = fields.Boolean("Is Order From Requisition?", default=False)
	maintenance_id = fields.Many2one('maintenance.request', 'Maintenance Request')
