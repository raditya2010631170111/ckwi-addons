from odoo import fields, models


class MaintenancePlan(models.Model):

    _name = "maintenance.plan"
    _description = "Maintenance Plan"

    name = fields.Char("Name", required=True, translate=True)
    active = fields.Boolean("Active Plan", required=True, default=True)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Maintenance plan name already exists.")
    ]

class MaintenanceBagian(models.Model):

    _name = "maintenance.bagian"
    _description = "Maintenance Bagian"

    name = fields.Char("Name", required=True, translate=True)
