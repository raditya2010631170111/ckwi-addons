# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResBranch(models.Model):
    _name = 'res.branch'

    code = fields.Char('Code')
    name = fields.Char('Name')

class ResPartner(models.Model):
    _inherit = 'res.users'

    branch_id = fields.Many2one('res.branch', string='Branch Location')
