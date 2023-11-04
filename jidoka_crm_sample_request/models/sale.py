# -*- coding: utf-8 -*-
from odoo import models, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sample_request_id = fields.Many2one(comodel_name='crm.sample.request', string='Sample Request', copy=False)
    

    
    def _prepare_product_so(self):
        sample = self.sample_request_id
        line = []
        for x in sample.line_ids:
            line.append((0,0,{
                'product_id': x.product_id.id,
                'product_uom': x.uom_id.id,
                'attachment': x.attachment,
                'product_uom_qty': x.qty,
                }))

        self.order_line = line