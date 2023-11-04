# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_new_quotation(self):
        res = super(CrmLead,self).action_new_quotation()
        values = []
        for spec in self.spec_design_ids:
            values.append((0,0,{
                'spec_design_id':spec.id,
                'product_id':spec.item_id.id,
                'name':spec.item_id.description,
                'product_uom':spec.item_id.uom_id.id,
                'product_uom_qty':spec.quantity,
                'price_unit':spec.unit_price,
                }))
        res['context']['default_order_line']=values
        return res