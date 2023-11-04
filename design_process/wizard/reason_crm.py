# © 2013 Guewen Baconnier, Camptocamp SA
# Copyright 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class CRMrevisi(models.TransientModel):

    """Ask a reason for the purchase order cancellation."""

    _name = "crm.lead.reason"
    _description = __doc__

    reason = fields.Text(string="Reason Revisi", required=True)

    def confirm_revisi(self):
        self.ensure_one()
        act_close = {"type": "ir.actions.act_window_close"}
        lead = self._context.get("active_id")
        if lead is None:
            return act_close
        lead = self.env["crm.lead"].browse(lead)
        stage_revisi = self.env['design.process.stage'].search([('code','=','revisi')])
        rnd = self.env['design.process'].search([('crm_id','=', lead.id)])
        for nw in rnd:
            nw.update({
                'stage_id': stage_revisi.id,
                'is_asigned': False
                })
        lead.reason = self.reason
        stage_draft = lead.stage_id.search([('code','=','draft')])
        lead.is_revisi = True
        lead.stage_id = stage_draft.id
        for line in lead.spec_design_ids:
            line.process_state = 'draft'
        lead.is_asigned = False
        lead.is_waiting = False
        lead.revisi_date = fields.Datetime.now()
        lead.count_rev = lead.count_rev + 1
        lead.request_no = str(lead.origin_req) + '-Rev.' + str(lead.count_rev)
        user = self.env.user
        mstr = [(0,0,{
            'stage_id' : "Revisi",
            'comment' : self.reason,
            'user_id' : user.id,
            })]
        lead.approval_history_ids = mstr
        return act_close