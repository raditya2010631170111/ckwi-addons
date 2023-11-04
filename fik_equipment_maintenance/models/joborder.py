from odoo import models, fields, api, _


class resconfig(models.TransientModel):
	_inherit = 'res.config.settings'

	email_validation = fields.Boolean(related='company_id.stock_move_email_validation', readonly=False)
	confirmation_template_id = fields.Many2one(related='company_id.confirmation_template_id', readonly=False)


class rescompany(models.Model):
	_inherit = 'res.company'

	email_validation = fields.Boolean("Email Confirmation", default=False)
	confirmation_template_id = fields.Many2one('mail.template', string="Email Template confirmation picking",
		domain="[('model', '=', 'maintenance.request')]",help="Email sent to the customer once the maintenance state is change.")