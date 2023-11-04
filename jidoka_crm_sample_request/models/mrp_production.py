# -*- coding: utf-8 -*-
from odoo import models, fields, _


class MrpProductionInherit(models.Model):
    _inherit = 'mrp.production'

    sample_request_id = fields.Many2one(comodel_name='crm.sample.request', string='Sample Request', copy=False)
    is_sample_request = fields.Boolean('Is Sample Request', readonly=True, default=False)
