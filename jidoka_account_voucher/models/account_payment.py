# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'

    # TODO remove me?
    voucher_id = fields.Many2one(
        comodel_name='account.voucher', string='Voucher', copy=False)
    voucher_line_id = fields.Many2one(
        comodel_name='account.voucher.line', string='Voucher Line', copy=False)