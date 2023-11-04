# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression

class ResSizeLog(models.Model):
    _name = 'res.size.log'
    _description = 'Res Size Log'
    
    name = fields.Char('Name')
    diameter = fields.Char('Diameter') #tidak dipakai
    panjang = fields.Char('Panjang') #tidak dipakai
    ujung_keliling = fields.Char('Ujung Keliling') #tidak dipakai

    diameter_log = fields.Integer('Diameter')
    panjang_log = fields.Integer('Panjang')
    ujung_keliling_log = fields.Integer('Ujung Keliling')
    
    kubikasi = fields.Float('kubikasi', digits='Product Unit of Measure')
    is_jati = fields.Boolean('Is Jati?')
    product_ids = fields.Many2many(
        string='Product ',
        comodel_name='product.product'
    )


    @api.model
    def create(self, vals):
        diameter = vals.get('diameter_log')
        panjang = vals.get('panjang_log')
        vals['name'] = "%sx%s" %(diameter,panjang)
        return super(ResSizeLog,self).create(vals)


    def write(self, vals):
        res = False
        if vals.get('diameter_log'):
            diameter = vals.get('diameter_log')
            res = "%sx%s" %(diameter,self.panjang_log)
        elif vals.get('panjang_log'):
            panjang = vals.get('panjang_log')
            res = "%sx%s" %(self.diameter_log,panjang)
        else:
            diameter = self.diameter_log
            panjang = self.panjang_log
            res = "%sx%s" %(diameter,panjang)
            
        if vals.get('diameter_log') and vals.get('panjang_log'):
            panjang = vals.get('panjang_log')
            diameter = vals.get('diameter_log')
            res = "%sx%s" %(diameter,panjang)
            
        vals['name'] = res
        return super(ResSizeLog,self).write(vals)
    
    
    def name_get(self):
        result = []
        for rec in self:
            name = "%sx%s" %(rec.diameter_log,rec.panjang_log)
            result.append((rec.id, name))
        return result
    

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('diameter_log', operator, name), ('name', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
    