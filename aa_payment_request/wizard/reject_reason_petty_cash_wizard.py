# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError


class RejectPettyCashWizard(models.TransientModel):
    _name = "reject.pettycash.wizard"

    payment_request_id = fields.Many2one(
        'payment.request', string='Payment Request')
    reject_reason = fields.Text(string='Reject Reason', required=True)

    def action_reject(self):
        self.payment_request_id.write({
            'state': 'reject',
            'reject_reason': self.reject_reason,
            'approval_ke': 0,
            'message_state': 'info',
            'message': "Petty Cash rejected by {} on {}".format(self.env.user.name,
                                                                fields.date.today())
        })
