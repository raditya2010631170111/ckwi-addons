# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class JidokaDesignFinish(models.Model):
    _name = 'design.finish'
    _description = 'Finish Material'
    _rec_name = "name"




    name = fields.Char("Name")