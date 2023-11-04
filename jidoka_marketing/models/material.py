# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class JidokaDesignMaterial(models.Model):
    _name = 'design.material'
    _description = 'Design Material'
    _rec_name = "name"



    name = fields.Char("Name")