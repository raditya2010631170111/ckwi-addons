# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def name_get(self):
        if self._context.get('show_mo_name'):
            res = []
            for order in self:
                name = order.name
                if order.no_mo:
                    name = '%s - %s' % (name, order.no_mo)
                res.append((order.id, name))
            return res
        return super(SaleOrder, self).name_get()