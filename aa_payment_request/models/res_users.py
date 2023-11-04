# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'


    work_locations = fields.Many2many(
        'jidoka.worklocation', 'worklocations_users_rel', 'user_id', 'work_location_id','Work Locations')