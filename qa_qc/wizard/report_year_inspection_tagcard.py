# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ReportYearInspectionTagCard(models.TransientModel):
    _name = 'report.year.inspection.tagcard'
    _description = 'Get Lost Reason'

    # lost_reason_id = fields.Many2one('crm.lost.reason', 'Lost Reason')
    lost_reason_id = fields.Char('Lost Reason')

    def action_lost_reason_apply(self):
        # leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        # return leads.action_set_lost(lost_reason=self.lost_reason_id.id)
        return True
