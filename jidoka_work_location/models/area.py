from odoo import _, api, fields, models
import pytz


class JidokaArea(models.Model):
    _name = 'jidoka.area'
    _description = 'Master Area'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')
    latitude = fields.Char('Latitude')
    longitude = fields.Char('Logitude')
    location_address = fields.Char('Area Address')
    list_department_ids = fields.One2many(
        comodel_name='jidoka.list.department', inverse_name='area_id', string='List Department')


class JidokaListDepartment(models.Model):
    _name = "jidoka.list.department"

    area_id = fields.Many2one('jidoka.area', string='Area')
    department_id = fields.Many2one(
        'hr.department', string='Department', required=True)
    description = fields.Char('Description')
