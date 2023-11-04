# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class InheritAccountMove(models.Model):
    _inherit = 'account.move'

    voucher_id = fields.Many2one(
        comodel_name='account.voucher', string='Voucher', copy=False)
    # TODO remove me?
    voucher_line_id = fields.Many2one(
        comodel_name='account.voucher.line', string='Voucher Line', copy=False)
        
    keterangan = fields.Char('Description', copy=False)
    
    def get_report_voucher_lines(self):
        voucher_move = []
        move_lines = []
        outstd_pay_line = []
        ap_ar_accounts = self.env['account.account.type'].search([('type','in',['payable','receivable'])])
        for move in self:
            if move.line_ids.filtered(lambda x: x.account_id.user_type_id.id in ap_ar_accounts.ids):
                reconciled_item = move.line_ids.filtered(lambda x: x.account_id.user_type_id.id in ap_ar_accounts.ids)[0]
                line_ids = reconciled_item._reconciled_lines()
                lines = self.env['account.move.line'].browse(line_ids)
                if lines.filtered(lambda x: x.id != reconciled_item.id):
                    voucher_move = lines.filtered(lambda x: x.id != reconciled_item.id)[0].move_id
                    move_lines = voucher_move.line_ids.filtered(lambda x: x.account_id.id not in (voucher_move.journal_id.payment_debit_account_id.id, voucher_move.journal_id.payment_credit_account_id.id))
                    outstd_pay_line = voucher_move.line_ids.filtered(lambda x: x.account_id.id in (voucher_move.journal_id.payment_debit_account_id.id, voucher_move.journal_id.payment_credit_account_id.id))
        return (voucher_move,move_lines, outstd_pay_line)
    
class InheritAccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    def get_voucher_line_balance(self):
        for line in self:
            return line.debit-line.credit