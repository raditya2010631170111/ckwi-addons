# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResFabricColour(models.Model):
    _name = 'res.fabric.colour'
    _description = 'Res Fabric Colour'
    
    code = fields.Char('Code')
    name = fields.Char('Name')