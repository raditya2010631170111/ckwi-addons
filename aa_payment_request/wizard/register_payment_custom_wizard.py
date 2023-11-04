# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PaymentRegisterCustom(models.TransientModel):
    _inherit = 'payment.register.custom'


    def pay(self):
        inv = self.env['voucher.multi.invoice'].with_context(active_id=False).search([('id', '=', self.env.context.get('active_id'))])
        if inv.payment_request_id:
            inv.payment_request_id.write({'state':'paid'})

        return super(PaymentRegisterCustom, self).pay()
