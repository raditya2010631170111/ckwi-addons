# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    mrp_sawmill_id = fields.Many2one('mrp.sawmill', string='Mrp Sawmill')
    
    # no_sc_id = fields.Many2one('mrp.production', string='No MO')
    # no_sc = fields.Char('No SC', 
    #     compute='_compute_no_sc' )
    no_sc_id = fields.Many2one('sale.order', string='No SC',
        compute='_compute_no_sc',store=True )
    
    @api.depends('origin')
    def _compute_no_sc(self):
        no_sc = ''
        for r in self:
            no_sc  = self.env['sale.order'].search([('name','=',r.origin)])
            if no_sc:
                r.no_sc_id = no_sc.id
            else:
                # r.no_sc_id = False
                mrp  = self.env['mrp.production'].search([('name','=',r.origin)])
                r.no_sc_id = mrp.no_sc_id.id
                
    
    # no_sc = fields.Char('no_sc')
    
    
    