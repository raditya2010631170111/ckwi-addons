# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.osv import expression

class ResMaterialDimention(models.Model):
    _name = 'res.material.dimention'
    _description = 'Res Material Dimention'
    
    name = fields.Char('Name') 
    lebar = fields.Char('Lebar') #tidak dipakai
    panjang = fields.Char('Panjang') #tidak dipakai
    
    panjang_mat = fields.Integer('Panjang')
    lebar_mat = fields.Integer('Lebar')
    kubikasi = fields.Float('kubikasi', digits='Product Unit of Measure')

    # @api.model
    # def create(self, vals):
    #     vals['name'] = vals.get('lebar') +'x'+vals.get('panjang')
    #     return super(ResMaterialDimention,self).create(vals)
    
    @api.model
    def create(self, vals):
        panjang = vals.get('panjang_mat')
        lebar = vals.get('lebar_mat')
        vals['name'] = "%sx%s" %(lebar,panjang)
        return super(ResMaterialDimention,self).create(vals)

    # def write(self, vals):
    #     res = False
    #     if vals.get('lebar'):
    #         res = vals.get('lebar') +'x'+self.panjang
    #     if vals.get('panjang'):
    #         res = self.lebar +'x'+vals.get('panjang')
    #     vals['name'] = res
    #     return super(ResMaterialDimention,self).write(vals)

    def write(self, vals):
        res = False
        if vals.get('lebar_mat'):
            panjang = self.panjang_mat
            lebar = vals.get('lebar_mat')
            res = "%sx%s" %(lebar,panjang)
        elif vals.get('panjang_mat'):
            panjang = vals.get('panjang_mat')
            lebar = self.lebar_mat
            res = "%sx%s" %(lebar,panjang)
        else:
            panjang = self.panjang_mat
            lebar = self.lebar_mat
            res = "%sx%s" %(lebar,panjang)
            
        if vals.get('lebar_mat') and vals.get('panjang_mat'):
            panjang = vals.get('panjang_mat')
            lebar = vals.get('lebar_mat')
            res = "%sx%s" %(lebar,panjang)
            
        vals['name'] = res
        return super(ResMaterialDimention,self).write(vals)
    
    # def name_get(self):
    #     result = []
    #     for rec in self:
    #         name = rec.lebar +'x'+ rec.panjang
    #         result.append((rec.id, name))
    #     return result
    
    def name_get(self):
        result = []
        for rec in self:
            panjang = rec.panjang_mat
            lebar = rec.lebar_mat
            name = "%sx%s" %(lebar,panjang)
            result.append((rec.id, name))
        return result

    # @api.model
    # def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
    #     args = args or []
    #     if operator == 'ilike' and not (name or '').strip():
    #         domain = []
    #     else:
    #         domain = ['|', ('lebar', operator, name), ('name', operator, name)]
    #     return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('lebar_mat', operator, name), ('name', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)