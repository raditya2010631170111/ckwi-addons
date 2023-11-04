
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MaintenanceDaily(models.Model):
    _name = "maintenance.daily"
    _description = "Maintenance Daily"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Description")
    active = fields.Boolean(default=True)
    create_date = fields.Date('Date', tracking=True, default=fields.Date.context_today,)
    equipment_id = fields.Many2one(
        string="Equipment", comodel_name="maintenance.equipment", ondelete="cascade"
    )
    category_id = fields.Many2one('maintenance.equipment.category', related='equipment_id.category_id', string='Category', store=True, readonly=True)
    user_id = fields.Many2one('res.users', string='Technician', tracking=True)
    category_id = fields.Many2one('maintenance.equipment.category', related='equipment_id.category_id',
                                  string='Category', store=True, readonly=True)
    start_maintenance_date = fields.Date(
        string="Start maintenance date",
        default=fields.Date.context_today,
        help="Date from which the maintenance will we active",
    )
    color = fields.Integer('Color Index')
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', index=True, track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string='Department', store=True, readonly=True)

    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
    )
   
    duration = fields.Float(
        string="Duration (hours)", help="Maintenance duration in hours"
    )
    note = fields.Html("Note")
    maintenance_ids = fields.One2many(
        "maintenance.request", "maintenance_daily_id", string="Maintenance requests"
    )
    maintenance_count = fields.Integer(
        compute="_compute_maintenance_count", string="Maintenance", store=True
    )
    maintenance_open_count = fields.Integer(
        compute="_compute_maintenance_count", string="Current Maintenance", store=True
    )
    maintenance_team_id = fields.Many2one("maintenance.team")
    # maintenance_type = fields.One2many("maintenance.request.maintenance_type", string='Maintenance Type')
    maintenance_daily_line_ids = fields.One2many("maintenance.daily.line", "maintenance_daily_id", string="Maintenance daily"
    )

    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        if self.equipment_id:
            self.user_id = self.equipment_id.technician_user_id if self.equipment_id.technician_user_id else self.equipment_id.category_id.technician_user_id
            self.category_id = self.equipment_id.category_id

    @api.onchange('employee_id')
    def get_department(self):
        for line in self:
            line.department_id = line.employee_id.department_id.id

    class MaintenanceDailyLine(models.Model):
        _name = "maintenance.daily.line"
        _description = "Maintenance Daily Line"

        aliran_listrik = fields.Selection([('off', 'OFF'), ('on', 'ON')], default='off', string='Aliran Listrik')
        tempat = fields.Char("Tempat")
        dasar = fields.Char("Dasar")
        cara = fields.Char("Cara")
        greas = fields.Integer("Greas")
        alat = fields.Char("Alat")
        waktu = fields.Char("Waktu")
        all_shift = fields.Boolean("All Shift")
        shift1 = fields.Boolean("Shift1")
        shift2 = fields.Boolean("Shift2")
        date = fields.Date("Tanggal")
        bagian_id = fields.Many2one('maintenance.bagian', 'Bagian')
        maintenance_daily_id = fields.Many2one('maintenance.daily', 'Maintenance Daily')

