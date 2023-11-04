from odoo import models, fields, api, _

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    check_ids = fields.Many2many('maintenance.checklist',string='Maintenance CheckList')
    line_ids = fields.One2many('equipment.part.line','maintenance_equipment_id','line')
    foto = fields.Selection([('ok', 'OK'),('bad', 'Bad')], string='FOTO', translate=False)
    manual = fields.Selection([('ok', 'OK'),('bad', 'Bad')], string='MANUAL', translate=False)
    sejarah = fields.Selection([('ok', 'OK'),('bad', 'Bad')], string='SEJARAH', translate=False)
    tpm = fields.Selection([('ok', 'OK'),('bad', 'Bad')], string='TPM', translate=False)
    mekanik = fields.Selection([('ok', 'OK'),('bad', 'Bad')], string='MEKANIK', translate=False)
    listrik = fields.Selection([('ok', 'OK'),('bad', 'Bad')], string='LISTRIK', translate=False)
    hydrolic = fields.Selection([('ok', 'OK'),('bad', 'Bad')], string='HYDROLIC', translate=False)
    pneumatic = fields.Selection([('ok', 'OK'),('bad', 'Bad')], string='PNEUMATIC', translate=False)

    maintenance_timetable_ids = fields.One2many(
        string="Maintenance Timetable",
        comodel_name="maintenance.timetable",
        inverse_name="equipment_id",
    )
    maintenance_timetable_count = fields.Integer(
        compute="_compute_maintenance_timetable_count",
        string="Maintenance Timetable Count",
        store=True,
    )
    equipment_type = fields.Selection(
        [
            ("machines", "Machines"),
            ("tools", "Tools"),
        ],
        string="Equipment Type",
        default="machines")
    maintenance_team_required = fields.Boolean(compute="_compute_team_required")
    notes = fields.Text(string="Notes")

    @api.depends("maintenance_timetable_ids", "maintenance_timetable_ids.active")
    def _compute_maintenance_timetable_count(self):
        for equipment in self:
            equipment.maintenance_timetable_count = len(
                equipment.with_context(active_test=False).maintenance_timetable_ids
            )

    @api.depends("maintenance_timetable_ids")
    def _compute_team_required(self):
        for equipment in self:
            equipment.maintenance_team_required = (
                    len(
                        equipment.maintenance_timetable_ids.filtered(
                            lambda r: not r.maintenance_team_id
                        )
                    )
                    >= 1
            )

    @api.constrains("company_id", "maintenance_timetable_ids")
    def _check_company_id(self):
        for rec in self:
            if rec.company_id and not all(
                    rec.company_id == p.company_id for p in rec.maintenance_timetable_ids
            ):
                raise ValidationError(
                    _(
                        "Some maintenance timetable's company is incompatible with "
                        "the company of this equipment."
                    )
                )

    def _prepare_request_from_timetable(self, maintenance_timetable, next_maintenance_date):
        team_id = maintenance_timetable.maintenance_team_id.id or self.maintenance_team_id.id
        if not team_id:
            team_id = self.env["maintenance.request"]._get_default_team_id()

        description = self.name if self else maintenance_timetable.name
        plan = maintenance_timetable.maintenance_plan_id.name or _("Unspecified plan")
        name = _("Preventive Maintenance (%s) - %s") % (plan, description)

        return {
            "name": name,
            "request_date": next_maintenance_date,
            "schedule_date": next_maintenance_date,
            "category_id": self.category_id.id,
            "equipment_id": self.id,
            "maintenance_type": "preventive",
            "owner_user_id": self.owner_user_id.id or self.env.user.id,
            "user_id": self.technician_user_id.id,
            "maintenance_team_id": team_id,
            "maintenance_plan_id": maintenance_timetable.maintenance_plan_id.id,
            "maintenance_timetable_id": maintenance_timetable.id,
            "duration": maintenance_timetable.duration,
            "note": maintenance_timetable.note,
            "company_id": maintenance_timetable.company_id.id or self.company_id.id,
        }

    def _create_new_request(self, mtn_timetable):
        # Compute horizon date adding to today the timetable horizon
        horizon_date = fields.Date.today() + mtn_timetable.get_relativedelta(
            mtn_timetable.maintenance_timetable_horizon, mtn_timetable.timetable_step or "year"
        )
        # We check maintenance request already created and create until
        # timetable horizon is met
        start_maintenance_date_timetable = mtn_timetable.start_maintenance_date
        furthest_maintenance_request = self.env["maintenance.request"].search(
            [
                ("maintenance_timetable_id", "=", mtn_timetable.id),
                ("request_date", ">=", start_maintenance_date_timetable),
            ],
            order="request_date desc",
            limit=1,
        )
        if furthest_maintenance_request:
            next_maintenance_date = (
                    furthest_maintenance_request.request_date
                    + mtn_timetable.get_relativedelta(
                mtn_timetable.interval, mtn_timetable.interval_step or "year"
            )
            )
        else:
            next_maintenance_date = mtn_timetable.next_maintenance_date
        requests = self.env["maintenance.request"]
        # Create maintenance request until we reach timetable horizon
        while next_maintenance_date <= horizon_date:
            if next_maintenance_date >= fields.Date.today():
                vals = self._prepare_request_from_timetable(mtn_timetable, next_maintenance_date)
                requests |= self.env["maintenance.request"].create(vals)
            next_maintenance_date = next_maintenance_date + mtn_timetable.get_relativedelta(
                mtn_timetable.interval, mtn_timetable.interval_step or "year"
            )
        return requests

    @api.model
    def _cron_generate_requests(self):
        """
        Generates maintenance request on the next_maintenance_date or
        today if none exists
        """
        for timetable in (
                self.env["maintenance.timetable"]
                        .sudo()
                        .search([("interval", ">", 0)])
                        .filtered(lambda x: True if not x.equipment_id else x.equipment_id.active)
        ):
            equipment = timetable.equipment_id
            equipment._create_new_request(timetable)

    @api.depends(
        "maintenance_timetable_ids.next_maintenance_date", "maintenance_ids.request_date"
    )
    def _compute_next_maintenance(self):
        """Redefine the function to display next_action_date in kanban view"""
        for equipment in self:
            next_timetable_dates = equipment.maintenance_timetable_ids.mapped(
                "next_maintenance_date"
            )
            next_untimetable_dates = (
                self.env["maintenance.request"]
                .search(
                    [
                        ("equipment_id", "=", equipment.id),
                        ("maintenance_plan_id", "=", None),
                        ("request_date", ">", fields.Date.context_today(self)),
                        ("stage_id.done", "!=", True),
                        ("close_date", "=", False),
                    ]
                )
                .mapped("request_date")
            )
            if len(next_timetable_dates + next_untimetable_dates) <= 0:
                equipment.next_action_date = None
            else:
                equipment.next_action_date = min(next_timetable_dates + next_untimetable_dates)
#
# class FikMaintenanceRequest(models.Model):
#     _inherit = 'maintenance.request'
#
