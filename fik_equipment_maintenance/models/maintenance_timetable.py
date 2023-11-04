
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MaintenanceTimetable(models.Model):
    _name = "maintenance.timetable"
    _description = "Maintenance Timetable"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Description")
    active = fields.Boolean(default=True)
    create_date = fields.Date('Date', tracking=True, default=fields.Date.context_today,)
    equipment_id = fields.Many2one(string="Equipment", comodel_name="maintenance.equipment", ondelete="cascade")
    nama_mesin = fields.Char(related='equipment_id.name', string='Nama Mesin')
    no_mesin = fields.Char(related='equipment_id.serial_no', string='No Mesin')
    category_id = fields.Many2one('maintenance.equipment.category', related='equipment_id.category_id', string='Category', store=True, readonly=True)
    user_id = fields.Many2one('res.users', string='Technician', tracking=True)
    color = fields.Integer('Color Index')
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', index=True, track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string='Department', store=True, readonly=True)

    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
    )
    maintenance_plan_id = fields.Many2one(
        string="Maintenance Plan", comodel_name="maintenance.plan", ondelete="restrict"
    )
    interval = fields.Integer(
        string="Frequency", default=1, help="Interval between each maintenance"
    )
    interval_step = fields.Selection(
        [
            ("day", "Day(s)"),
            ("week", "Week(s)"),
            ("month", "Month(s)"),
            ("year", "Year(s)"),
        ],
        string="Recurrence",
        default="year",
        help="Let the event automatically repeat at that interval step",
    )
    duration = fields.Float(
        string="Duration (hours)", help="Maintenance duration in hours"
    )
    start_maintenance_date = fields.Date(
        string="Start maintenance date",
        default=fields.Date.context_today,
        help="Date from which the maintenance will we active",
    )
    next_maintenance_date = fields.Date(
        "Next maintenance date", compute="_compute_next_maintenance", store=True
    )
    maintenance_timetable_horizon = fields.Integer(
        string="timetable Horizon period",
        default=1,
        help="Maintenance timetable horizon. Only the maintenance requests "
        "inside the horizon will be created.",
    )
    timetable_step = fields.Selection(
        [
            ("day", "Day(s)"),
            ("week", "Week(s)"),
            ("month", "Month(s)"),
            ("year", "Year(s)"),
        ],
        string="timetable Horizon step",
        default="year",
        help="Let the event automatically repeat at that interval",
    )
    note = fields.Html("Note")
    maintenance_ids = fields.One2many(
        "maintenance.request", "maintenance_timetable_id", string="Maintenance requests"
    )
    maintenance_count = fields.Integer(
        compute="_compute_maintenance_count", string="Maintenance", store=True
    )
    maintenance_open_count = fields.Integer(
        compute="_compute_maintenance_count", string="Current Maintenance", store=True
    )
    maintenance_team_id = fields.Many2one("maintenance.team")
    # maintenance_type = fields.One2many("maintenance.request.maintenance_type", string='Maintenance Type')
    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        if self.equipment_id:
            self.user_id = self.equipment_id.technician_user_id if self.equipment_id.technician_user_id else self.equipment_id.category_id.technician_user_id
            self.category_id = self.equipment_id.category_id

    @api.onchange('employee_id')
    def get_department(self):
        for line in self:
            line.department_id = line.employee_id.department_id.id

    def name_get(self):
        result = []
        for timetable in self:
            result.append(
                (
                    timetable.id,
                    timetable.name
                    or _("Unnamed %s timetable (%s)")
                    % (timetable.maintenance_plan_id.name or "", timetable.equipment_id.name),
                )
            )
        return result

    @api.depends("maintenance_ids.stage_id.done")
    def _compute_maintenance_count(self):
        for equipment in self:
            equipment.maintenance_count = len(equipment.maintenance_ids)
            equipment.maintenance_open_count = len(
                equipment.maintenance_ids.filtered(lambda x: not x.stage_id.done)
            )

# koding awal untuk menentukan rentan waktu maintenance

    # def get_relativedelta(self, interval, step):
    #     if step == "day":
    #         return relativedelta(days=interval)
    #     elif step == "week":
    #         return relativedelta(weeks=interval)
    #     elif step == "month":
    #         return relativedelta(months=interval)
    #     elif step == "year":
    #         return relativedelta(years=interval)

    # @api.depends(
    #     "interval",
    #     "interval_step",
    #     "start_maintenance_date",
    #     "maintenance_ids.request_date",
    #     "maintenance_ids.close_date",
    # )
    # def _compute_next_maintenance(self):
    #     for timetable in self.filtered(lambda x: x.interval > 0):

    #         interval_timedelta = self.get_relativedelta(
    #             timetable.interval, timetable.interval_step
    #         )

    #         next_maintenance_todo = self.env["maintenance.request"].search(
    #             [
    #                 ("maintenance_timetable_id", "=", timetable.id),
    #                 ("stage_id.done", "!=", True),
    #                 ("close_date", "=", False),
    #                 ("request_date", ">=", timetable.start_maintenance_date),
    #             ],
    #             order="request_date asc",
    #             limit=1,
    #         )

    #         if next_maintenance_todo:
    #             timetable.next_maintenance_date = next_maintenance_todo.request_date
    #         else:
    #             last_maintenance_done = self.env["maintenance.request"].search(
    #                 [
    #                     ("maintenance_timetable_id", "=", timetable.id),
    #                     ("request_date", ">=", timetable.start_maintenance_date),
    #                 ],
    #                 order="request_date desc",
    #                 limit=1,
    #             )
    #             if last_maintenance_done:
    #                 timetable.next_maintenance_date = (
    #                     last_maintenance_done.request_date + interval_timedelta
    #                 )
    #             else:
    #                 next_date = timetable.start_maintenance_date
    #                 while next_date < fields.Date.today():
    #                     next_date = next_date + interval_timedelta
    #                 timetable.next_maintenance_date = next_date


    @api.depends('interval', 'interval_step', 'start_maintenance_date')
    def _compute_next_maintenance(self):
        for record in self:
            if record.start_maintenance_date and record.interval > 0:
                start_date = fields.Datetime.from_string(record.start_maintenance_date)
                interval_timedelta = timedelta()

                if record.interval_step == 'day':
                    interval_timedelta = timedelta(days=record.interval)
                elif record.interval_step == 'week':
                    interval_timedelta = timedelta(weeks=record.interval)
                elif record.interval_step == 'month':
                    interval_timedelta = relativedelta(months=record.interval)
                elif record.interval_step == 'year':
                    interval_timedelta = relativedelta(years=record.interval)

                next_date = start_date + interval_timedelta
                record.next_maintenance_date = fields.Date.to_string(next_date.date())
            else:
                record.next_maintenance_date = False

    @api.constrains("company_id", "equipment_id")
    def _check_company_id(self):
        for rec in self:
            if (
                rec.equipment_id.company_id
                and rec.company_id != rec.equipment_id.company_id
            ):
                raise ValidationError(
                    _("Maintenace Equipment must belong to the equipment's company")
                )

    def create_wo(self):
        for tt in self:
            wo = self.env['maintenance.request']
            wo_line = self.env['asa.wo.line']

            wo = wo.create({
                'name': tt.name,
                'maintenance_team_id': tt.commitment_date,
                'equipment_id': tt.commitment_date,
                'partner_id': tt.partner_id.id,
                'salesperson': tt.user_id.id,
                'note': tt.note,
                'work_station': [(6, 0, tt.work_station.ids)],
            })
    def unlink(self):
        """Restrict deletion of maintenance timetable should there be maintenance
        requests of this plan which are not done for its equipment"""
        for timetable in self:
            request = timetable.equipment_id.mapped("maintenance_ids").filtered(
                lambda r: (
                    r.maintenance_plan_id == timetable.maintenance_plan_id
                    and not r.stage_id.done
                    and r.maintenance_plan == "preventive"
                )
            )
            if request:
                raise UserError(
                    _(
                        "The maintenance timetable %s of equipment %s "
                        "has generated a request which is not done "
                        "yet. You should either set the request as "
                        "done, remove its maintenance plan or "
                        "delete it first."
                    )
                    % (timetable.maintenance_plan_id.name, timetable.equipment_id.name)
                )
        super().unlink()

    _sql_constraints = [
        (
            "equipment_plan_uniq",
            "unique (equipment_id, maintenance_plan_id)",
            "You cannot define multiple times the same maintenance plan on an "
            "equipment maintenance timetable.",
        )
    ]
