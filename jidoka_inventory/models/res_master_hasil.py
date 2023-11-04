# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResMasterHasil(models.Model):
    _name = 'res.master.hasil'
    _description = 'Res Master Hasil'

    name = fields.Char('Hasil')