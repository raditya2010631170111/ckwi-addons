# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResSupplierCode(models.Model):
    _name = 'res.supplier.code'
    _description = 'Res Supplier Code'
    
    code = fields.Char('Code')
    is_used = fields.Boolean('Is a Used?')

    _sql_constraints = [
        ('code_company_uniq', 'unique (code)', 'The code of the account must be unique!')
    ]

    def name_get(self):
        result = []
        for rec in self:
            name = rec.code 
            result.append((rec.id, name))
        return result

class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier_code_id = fields.Many2one('res.supplier.code', string='Supplier Code')
    # is_customer = fields.Boolean(default=0)
    # customer_rank = fields.Integer(default=0, copy=False)

    # @api.onchange('is_customer')
    # def onchange_is_customer(self):
    #     if self.is_customer == True:
    #         self.customer_rank = 1
    #     else :
    #         self.customer_rank = 0 
    
    @api.model
    def create(self, vals):
        res = super(ResPartner,self).create(vals)
        if res.supplier_code_id:
            res.supplier_code_id.is_used = True
        return res

    def write(self, vals):
        res = super(ResPartner,self).write(vals)
        if vals.get('supplier_code_id'):
            supp_code = self.env['res.supplier.code'].browse(vals.get('supplier_code_id'))
            supp_code.is_used = True
        return res

    def generate_supplier_code(self):
        res = self.env['res.supplier.code'].search([('is_used','=',False)],limit=1)
        if res:
            self.supplier_code_id = res.id