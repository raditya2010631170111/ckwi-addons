# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'


    user_ids = fields.Many2many('res.users', string='User')
