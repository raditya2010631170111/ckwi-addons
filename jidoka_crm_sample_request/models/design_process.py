# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class DesignProcessInherit(models.Model):
    _inherit = 'design.process'

    sample_request_id = fields.Many2one(comodel_name='crm.sample.request', string='Request Sample', copy=False)
    
    

    @api.onchange('sample_request_id')
    def sample_request_line(self):
        smpl = self.sample_request_id
        line = []
        lines = []
        for ret in smpl.line_detail_ids:
            lines.append((0,0,{
                "product_id" : ret.product_id.id,
                "design_detail_date" : ret.design_detail_date,
                "name" : ret.name,
                "state" : ret.state,
                }))
        self.design_detail_ids = lines

        for rex in smpl.line_ids:
            line.append((0,0,{
                "item_id" : rex.product_id.id,
                "uom_id" : rex.uom_id.id,
                "description" : rex.description,
                "quantity" : rex.qty,
                'attachment': rex.attachment,
                'note': rex.remark
                }))
        
        self.spec_design_ids = line

    # @api.onchange('sample_request_id')
    # def sample_request_line1(self):
    #     # import pdb;pdb.set_trace()
    #     smpl = self.sample_request_id
    #     lines = []
    #     for ret in smpl.line_detail_ids:
    #         lines.append((0,0,{
    #             "product_id" : ret.product_id.id,
    #             "design_detail_date" : ret.design_detail_date,
    #             "name" : ret.name,
    #             "state" : ret.state,
    #             }))
    #     self.design_detail_ids = lines
        