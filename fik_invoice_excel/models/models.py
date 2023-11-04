# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = "account.move"

    origin_ids = fields.Many2many('stock.picking', string='Source Documents From Export')
    origin = fields.Char('Source Document', compute='_compute_origin')
    peb_no =  fields.Integer('PEB No')
    peb_date = fields.Date('PEB Date', required=False)
    # bank_name = fields.Char(string='Bank Name', related='partner_bank_id.bank_id.name', required=True)
    voucher_name = fields.Char(string='Voucher Name', related='line_ids.move_name', required=True)
    tax_invoice = fields.Float('Tax Invoice')
    bank_name = fields.Char('Bank Name',
        compute='_compute_bank_name', store=True)
    account_payment_id = fields.Many2one('account.payment', compute='_compute_payment')

    def _compute_payment(self):
        for move in self:
            account_payment = self.env['account.payment'].search([('ref', '=', move.name)])
            move.account_payment_id = account_payment.id

    def _compute_origin(self):
        for move in self:
            sale_orders = self.env['sale.order'].search([('name', '=', move.invoice_origin)])
            move.origin = sale_orders[0].name if sale_orders else ''


    @api.depends('partner_id')
    def _compute_bank_name(self):
        for r in self[0]:
            r.bank_name = self.partner_id.bank_ids.bank_id.name
    
    
    