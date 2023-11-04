from odoo import _, api, fields, models

class WorkLocationEmployee(models.Model):
    _inherit = 'hr.employee'
    
    work_location_id = fields.Many2one(
        string='Lokasi Kerja',
        comodel_name='jidoka.worklocation',
        ondelete='cascade',
        help="To select the employee's Lokasi Kerja"
    )

class WorkLocationEmployeePubic(models.Model):
    _inherit = 'hr.employee.public'
    
    work_location_id = fields.Many2one(
        string='Lokasi Kerja',
        comodel_name='jidoka.worklocation',
        ondelete='cascade',
        help="To select the employee's Lokasi Kerja"
    )

        