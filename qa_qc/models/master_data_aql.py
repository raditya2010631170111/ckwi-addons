# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AQLData(models.Model):
    _name = 'qc.aql.data'
    _rec_name = 'name'
    _description = 'Master Data AQL'


    name = fields.Char()
    min_lot = fields.Float(string="Min Lot or Batch Size", required=True)
    max_lot = fields.Float(string="Max Lot or Batch Size", required=True)
    sample_size = fields.Integer(string="Sample Size", required=True)
    categ_id = fields.Many2one('product.category', string='Category', required=True, store=True,)
    level_id = fields.Many2one(string='Level AQL', comodel_name='level.aql')
    name_lev = fields.Char(string='nama level',invisible=True, related='level_id.name')
    ac = fields.Integer(string="AC")
    re = fields.Integer(string="RE")


    @api.model
    def create(self, vals):
        res =  super(AQLData, self).create(vals)
        name = 'AQL Range ' + str(res.min_lot) + ' - ' + str(res.max_lot)
        res.write({
            'name' : name
        })
        return res