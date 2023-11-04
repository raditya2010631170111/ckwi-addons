# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResLocation(models.Model):
    _name = 'res.location'
    _description = 'Res Location'
    
    name = fields.Char('Name')
    ongkir = fields.Float('Ongkir')
    fee = fields.Float('Fee')