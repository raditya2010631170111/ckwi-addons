# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare


import logging

_logger = logging.getLogger(__name__)


class AccountVoucher(models.Model):
    _name = 'account.voucher'
    _description = 'Voucher Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Number', default=lambda self: _('New'), index=True,
        tracking=True, readonly=False, copy=False)
    journal_id = fields.Many2one(
        comodel_name='account.journal', string='Journal', required=True,
        domain="[('type','in',('bank','cash'))]", check_company=True,)
    date = fields.Date(string='Date', required=True,
                       default=fields.Date.today())
    vendor_id = fields.Many2one(comodel_name='res.partner', string='Vendor')
    move_id = fields.Many2one(comodel_name='account.move', string='Invoice/Bill', copy=False, domain=[('move_type', '=', 'out_invoice')])
    user_id = fields.Many2one(comodel_name='res.users', string='Responsible',
                              default=lambda s: s.env.user, required=True)
    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'),
        ('post', 'Posted'),
        ('cancel', 'Cancelled'),
        ], default='draft', required=True, readonly=True)
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one(comodel_name='res.company', string='Company',
        index=True, default=lambda self: self.env.company.id,
        readonly=True, states={'draft': [('readonly', False)]},)
    payment_amount = fields.Monetary(string='Payment Amount', store=True, readonly=True, compute='_amount_all', tracking=True)
    amount_ppn = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency', compute="_compute_currency", store=True)
    line_ids = fields.One2many(comodel_name='account.voucher.line',
                               inverse_name='voucher_id', string='Voucher Details', copy=True)
    voucher_type = fields.Selection(string='Voucher Type', selection=[
                                    ('in', 'In'), ('out', 'Out'), ])
    total_amount = fields.Monetary(
        string='Total Amount', currency_field="currency_id", compute="_compute_total_amount", store=True)
    posted_before = fields.Boolean(string='Posted Before', default=False, copy=False)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', tracking=True)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    amount_fee = fields.Float('Amount Fee', store=True, readonly=True, compute='_amount_all')
    # fee_location_id = fields.Many2one('res.location', string='Delivery Loc.')

    @api.depends('line_ids.price_total','line_ids.fee')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = amount_fee =0.0
            for line in order.line_ids:
                line._compute_amount()
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_fee += line.price_fee_subtotal
            currency = order.currency_id or order.partner_id.property_purchase_currency_id or self.env.company.currency_id
            order.update({
                'amount_untaxed': currency.round(amount_untaxed),
                'amount_tax': currency.round(amount_tax),
                'amount_fee': currency.round(amount_fee),
                'amount_total': amount_untaxed + amount_tax
            })
            

    # Field2 untuk kebutuhan report
    # TODO remove me if unused
    signature_approver = fields.Binary('Signature Approver')
    signature_authorizer = fields.Binary('Signature Authorizer')
    signature_receiver = fields.Binary('Signature Receiver')
    signature_creator = fields.Binary('Signature Creator')
    approved_by = fields.Char(string='Approved By')
    authorized_by = fields.Char(string='Authorized By')
    received_by = fields.Char(string='Received By')
    created_by = fields.Char(string='Created By')

    received_from = fields.Char(string='Received from')
    received_for = fields.Char(string='Received for')

    paid_for = fields.Char(string='Paid for')
    payment_type = fields.Selection(string='Payment Type', selection=[
        ('bank', 'Bank Transfer'),
        ('cheque', 'Giro/Cheque'),
        ('petty_cash', 'Petty Cash'),
        ], default=False)
    
    #transfer
    bank_reference = fields.Char('Bank Reference')
    bank_account = fields.Char('Bank Account')
    struck_pembayaran = fields.Binary('Struk Pembayaran')
    date_transfer = fields.Date('Date Transfer')

    #chaque
    cheque_number = fields.Char(string='Cheque No')
    date_chaque = fields.Date('Date')

    # Smart Button Field
    count_account_invoice = fields.Integer(
        string='# of Account Invoice/Bill', compute='_compute_count_account')
    count_account_move = fields.Integer(
        string='# of Account Moves', compute='_compute_count_account')
    # count_account_payment = fields.Integer(
    #     string='# of Account Payments', compute='_compute_count_account')
    
    # currency_rate_rp = fields.Float(string='Currency Rate Rupiah')
    # currency_rate_date = fields.Date(string='Currency Rate Date')

    # add constraint number
    _sql_constraints = [
        (
            "name_uniq",
            "unique(name)",
            "Number must unique!",
        )
    ]

    many_po_ids = fields.Many2many(comodel_name='purchase.order', string='Purchase Order', copy=False)
    many_sc_ids = fields.Many2many(comodel_name='sale.order', string='Sale Confirmation', copy=False)
    many_bill_ids = fields.Many2many(comodel_name='account.move', string='Invoice/Bill', copy=False,domain=[('move_type', '=', 'in_invoice')])
    invoice_po_ids = fields.Many2many(comodel_name='purchase.order', string='Purchase Order', copy=False, compute="_compute_invoice_po_ids")
    invoice_bill_ids = fields.Many2many(comodel_name='account.move', string='Invoice/Bill', copy=False,compute="_compute_invoice_bill_ids", domain=[('move_type', '=', 'in_invoice')])
    invoice_sc_ids = fields.Many2many(comodel_name='sale.order', string='Sale Confirmation', copy=False, compute="_compute_invoice_sc_ids")
    
    @api.depends('vendor_id')
    def _compute_invoice_sc_ids(self):
        for voucher in self:
            if voucher.vendor_id:
                # Mengisi invoice_sc_ids
                sale_confirmations = self.env['sale.order'].search([('partner_id', '=', voucher.vendor_id.id)])
                voucher.invoice_sc_ids = [(6, 0, sale_confirmations.ids)]
            else:
                voucher.invoice_sc_ids = [(5, 0, 0)]
                

    @api.depends('vendor_id')
    def _compute_invoice_po_ids(self):
        for voucher in self:
            if voucher.vendor_id:
                # Mengisi invoice_po_ids
                purchase_orders = self.env['purchase.order'].search([('partner_id', '=', voucher.vendor_id.id)])
                voucher.invoice_po_ids = [(6, 0, purchase_orders.ids)]
            else:
                voucher.invoice_po_ids = [(5, 0, 0)]

    @api.depends('vendor_id')
    def _compute_invoice_bill_ids(self):
        for voucher in self:
            if voucher.vendor_id:
                invoice_bills = self.env['account.move'].search([('partner_id', '=', voucher.vendor_id.id), ('move_type', '=', 'in_invoice')])
                voucher.invoice_bill_ids = [(6, 0, invoice_bills.ids)]
            else:
                voucher.invoice_bill_ids = [(5, 0, 0)]

    # # TIDAK CONSTRAINT NUMBER
    # def _constrains_date_sequence(self):
    #     Mohon pastikan unique number tidak ada yang sama
    #     return
    
    # @api.onchange('currency_id', 'date')
    # def _get_currency_rate_rp(self):
    #     currency = self.currency_id
    #     if self.currency_id and self.date:
    #         currency_new = self.env['res.currency.rate'].sudo().search([
    #             ('name','=',self.date), ('currency_id', '=', self.currency_id.id)], limit=1)
    #         if currency_new:
    #             self.currency_rate_rp= currency_new.rate_rp or 0
    #         else:
    #             self.currency_rate_rp= currency.rate_rp or 0
            
    #         if self.currency_id.name != 'IDR':
    #             if currency_new:
    #                 self.currency_rate_date= currency_new.name or False
    #             else:
    #                 self.currency_rate_date= currency.name or False

    

    @api.depends('state')
    def _compute_count_account(self):
        for i in self:
            i.count_account_move = self.env['account.move'].search_count(
                [('voucher_id', '=', i.id), ('move_type', '=', 'entry')])
            i.count_account_invoice = self.env['account.move'].search_count(
                [('voucher_id', '=', i.id), ('move_type', 'in', ('in_invoice', 'out_invoice'))])
            # i.count_account_payment = self.env['account.payment'].search_count(
            #     [('voucher_id', '=', i.id)])

    @api.depends('line_ids', 'line_ids.amount')
    def _compute_total_amount(self):
        for i in self:
            total_amount = 0
            if i.line_ids:
                # TODO amount with extra
                total_amount = sum(i.line_ids.mapped('amount_with_extra'))
            i.total_amount = total_amount

    # @api.depends('journal_id', 'company_id')
    # def _compute_currency(self):
    #     for i in self:
    #         if i.journal_id.currency_id:
    #             currency = i.journal_id.currency_id
    #         elif i.company_id.currency_id:
    #             currency = i.company_id.currency_id
    #         else:
    #             # TODO seharusnya dari config!
    #             currency = self.env['res.currency'].sudo().search([('name', '=', 'IDR')], limit=1)
    #         i.currency_id = currency

    selected_currency_id = fields.Many2one(
        comodel_name='res.currency', string='Selected Currency', store=True)

    @api.onchange('line_ids')
    def onchange_line_ids(self):
        for line in self.line_ids:
            if line.invoice_sc_id:
                pricelist_id = line.invoice_sc_id.pricelist_id
                self.selected_currency_id = pricelist_id.currency_id
                self.write({'selected_currency_id': pricelist_id.currency_id.id})
                break
            elif line.invoice_po_id:
                currency_id = line.invoice_po_id.currency_id
                self.selected_currency_id = currency_id
                self.write({'selected_currency_id': currency_id.id})
                break

    @api.depends('journal_id', 'company_id', 'selected_currency_id')
    def _compute_currency(self):
        for voucher in self:
            if voucher.selected_currency_id:
                voucher.currency_id = voucher.selected_currency_id
            elif voucher.journal_id.currency_id:
                voucher.currency_id = voucher.journal_id.currency_id
            elif voucher.company_id.currency_id:
                voucher.currency_id = voucher.company_id.currency_id
            else:
                # TODO seharusnya dari config!
                currency = self.env['res.currency'].sudo().search([('name', '=', 'IDR')], limit=1)
                voucher.currency_id = currency

    # prepare journal items
    def _prepare_move_line(self):
        company = self.company_id
        default_account_id = self.journal_id.default_account_id.id
        # currency_id = self.currency_id.id
        val_lines = []
        for line in self.line_ids:
            if not line.account_id:
                raise ValidationError(
                    _('Account in voucher line must be filled.'))
            # apakah item akun bank hanya 1 line atau mau detail?
            # saat ini detail
            vals_journal = {
                'name': line.description,
                'account_id': default_account_id,
                'partner_id': line.partner_id and line.partner_id.id or False,
                'currency_id': line.currency_id.id,
            }
            
            vals_lawan = {
                'name': line.description,
                'account_id': line.account_id.id,
                'partner_id': line.partner_id and line.partner_id.id or False,
                # 'currency_id': line.currency_id.id,
            }

            currency = line.currency_id
            amount_currency_lawan = amount_currency = line.amount_with_extra
            if line.is_currency_exchange and line.currency_id != line.exchange_currency_id:
                currency = line.exchange_currency_id
                amount_currency_lawan = line.amount_with_extra / line.exchange_rate
            
            vals_lawan['currency_id'] = currency.id

            # balance via convert
            balance = line.currency_id._convert(
                amount_currency,
                company.currency_id,
                company,
                line.date or fields.Date.context_today(line))

            if line.voucher_type == 'out':
                # out normalnya kredit
                vals_journal['amount_currency'] = -amount_currency
                vals_journal['credit'] = balance if balance > 0 else 0.0
                vals_journal['debit'] = -balance if balance < 0 else 0.0

                vals_lawan['amount_currency'] = amount_currency_lawan
                vals_lawan['debit'] = balance if balance > 0 else 0.0
                vals_lawan['credit'] = -balance if balance < 0 else 0.0
            else:
                # in normalnya di debit
                vals_journal['amount_currency'] = amount_currency
                vals_journal['debit'] = balance if balance > 0 else 0.0
                vals_journal['credit'] = -balance if balance < 0 else 0.0

                vals_lawan['amount_currency'] = -amount_currency_lawan
                vals_lawan['credit'] = balance if balance > 0 else 0.0
                vals_lawan['debit'] = -balance if balance < 0 else 0.0
            
            val_lines += [
                        (0, 0, vals_journal),
                        (0, 0, vals_lawan),
                    ]
        return val_lines

    # prepare journal items (single bank journal item)
    def _prepare_move_line_single(self):
        company = self.company_id
        # default_account_id = self.journal_id.payment_credit_account_id.id
        val_lines = []
        val_lines_line = []
        partner = self.line_ids.mapped('partner_id')
        total_amount = 0
        total_balance = 0
        # total amount currency dari looping
        for ln in self.line_ids:
            total_amount += self.currency_id.round(ln.amount)
        if self.voucher_type == 'in':
            vals_journal = {
            'account_id': self.journal_id.payment_credit_account_id.id,
            'partner_id': partner.id,
            'currency_id': self.currency_id.id,
        }
        elif self.voucher_type == 'out':
            vals_journal = {
            'account_id': self.journal_id.payment_debit_account_id.id,
            'partner_id': partner.id,
            'currency_id': self.currency_id.id,
        }

        for line in self.line_ids:
            account_id = line.account_id.id
            if not account_id:
                if line.move_id:
                    account_id = self._get_destination_account(partner, line.move_id)
                else:
                    raise ValidationError(
                        _('Account in voucher line must be filled.'))
            # partner
            line_partner = line.partner_id or partner
            # jika non move_id gunakan commercial_partner_id khusus AR / AP account
            if not line.move_id and line.account_id.user_type_id.type in ('receivable', 'payable'):
                line_partner = line.partner_id and line.partner_id.commercial_partner_id or False
            vals_lawan = {
                'name': line.description,
                'account_id': account_id,
                'partner_id': line_partner and line_partner.id or False,
                # 'currency_id': line.currency_id.id,
            }

            currency = line.currency_id
            amount_currency_lawan = amount_currency = line.amount
            if line.is_currency_exchange and line.currency_id != line.exchange_currency_id:
                currency = line.exchange_currency_id
                amount_currency_lawan = line.amount / line.exchange_rate
            
            vals_lawan['currency_id'] = currency.id
            # balance default convert
            balance = line.currency_id._convert(
                amount_currency,
                company.currency_id,
                company,
                line.date or fields.Date.context_today(line))

            # total_balance dari looping
            total_balance += balance

            if line.voucher_type == 'out':
                vals_lawan['amount_currency'] = amount_currency_lawan
                vals_lawan['debit'] = balance if balance > 0 else 0.0
                vals_lawan['credit'] = -balance if balance < 0 else 0.0
            else:
                vals_lawan['amount_currency'] = -amount_currency_lawan
                vals_lawan['credit'] = balance if balance > 0 else 0.0
                vals_lawan['debit'] = -balance if balance < 0 else 0.0
            
            val_lines_line += [(0, 0, vals_lawan)]
        
        # set balance
        balance = total_balance
        if self.voucher_type == 'out':
            # out normalnya kredit
            vals_journal['amount_currency'] = -1 * total_amount
            vals_journal['credit'] = balance if balance > 0 else 0.0
            vals_journal['debit'] = -balance if balance < 0 else 0.0
        else:
            vals_journal['amount_currency'] = total_amount
            vals_journal['debit'] = balance if balance > 0 else 0.0
            vals_journal['credit'] = -balance if balance < 0 else 0.0
        
        vals_journal['name'] = ','.join(
            l.description for l in self.line_ids if l.description)

        val_lines += [(0, 0, vals_journal)]
        val_lines += val_lines_line

        return val_lines
    
    def _create_new_entry(self, for_payment=False):
        vals = {
            'name': self.name,
            'ref': self.notes or self.name, # dari notes atau name
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'date': self.date,
            'voucher_id': self.id,
            # 'currency_rate_rp': self.currency_rate_rp,
            'line_ids': []
        }
        if for_payment:
            val_lines = self._prepare_move_line_single()
        else:
            val_lines = self._prepare_move_line()
        if val_lines:
            vals['line_ids'] = val_lines
            move_id = self.env['account.move'].create(vals)
            move_id.action_post()
            return move_id
        else:
            # no lines
            raise ValidationError(
                _('No lines to create account move.'))
    
    def _get_destination_account(self, partner, moves):
        origin_account_id = []
        for move in moves:
            for line in move.line_ids:
                if line.account_id.user_type_id.type in ('receivable', 'payable'):
                    origin_account_id.append(line.account_id.id)
        set_origin_account_id = set(origin_account_id)
        if len(set_origin_account_id) > 1:
            raise ValidationError(
                _('Account in voucher line must be same AR/AP Account.'))
        destination_account_id = False
        if self.voucher_type == 'out':
            destination_account_id = partner.with_company(
                    self.company_id).property_account_payable_id.id
            if not destination_account_id:
                destination_account_id = self.env['account.account'].search([
                    ('company_id', '=', self.company_id.id),
                    ('internal_type', '=', 'payable'),
                ], limit=1).id
        else:
            destination_account_id = partner.with_company(
                    self.company_id).property_account_receivable_id.id
            if not destination_account_id:
                destination_account_id = self.env['account.account'].search([
                    ('company_id', '=', self.company_id.id),
                    ('internal_type', '=', 'receivable'),
                ], limit=1).id


        return origin_account_id and origin_account_id[0] or destination_account_id
    
    def action_confirm(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError(
                _('You must add at least one line.'))
        
        # payment for AR/AP acc ?
        ar_ap_accounts = self.line_ids.filtered(
            lambda l: l.account_id.user_type_id.type in ['payable', 'receivable'])
        # inv / bill ?
        inv_bills = self.line_ids.filtered(lambda l: l.move_id)
        # tidak perlu
        # # not allow mix AP/AR - inv/bill with non AP/AR acc
        # if ar_ap_accounts and non_ar_ap_accounts:
        #     raise ValidationError(
        #         _('You can not mix AP/AR acc with non AP/AR acc.'))
        # # not allow mix inv/bill with non AP/AR acc
        # if inv_bills and non_ar_ap_accounts:
        #     raise ValidationError(
        #         _('You can not mix inv/bill with non AP/AR acc.'))
                        
        if ar_ap_accounts or inv_bills:
            prec = self.env['decimal.precision'].precision_get('Account')
            partner = self.line_ids.mapped('partner_id')
            if len(partner) > 1:
                raise ValidationError(
                    _('You can only use one partner in voucher.'))
            # if not partner:
            #     raise ValidationError(
            #         _('You must select at least one partner.'))
            
            moves = self.line_ids.mapped('move_id')
            # destination_account_id untuk mengisii field Destination Account di account.payment
            # Destination account ngambil dari inputan; kalo ngga, dari partner; kalo ngga, ngambil default ambil salah satu
            # Destination account untuk yang tipe out, berarti yang payable ; kalo yang tipe in, berarti yang receivable
            destination_account_id = self._get_destination_account(partner, moves)

            if not destination_account_id:
                if self.voucher_type == 'out':
                    message = 'payable'
                else:
                    message = 'receivable'
                raise ValidationError(
                    _('No {} account choosed !!'.format(message)))

            # create new payment
            if not self.posted_before:
                move = self._create_new_entry(for_payment=True)
                
                # Jika move_id diisi, langsung alokasikan payment tadi ke move_id yang dipilih
                for line in inv_bills:
                    # hanya untuk yg full payment
                    # if (line.payment_difference_handling == 'reconcile' and line.amount != line.move_residual_amount) or (line.amount == line.move_residual_amount):
                    if True:
                        # js_assign_outstanding_line(self, line_id) -> method yang dijalankan ketika klik add di outstanding payments
                        payment_move_line_id = False
                        if self.voucher_type == 'out':
                            # payment_move_line_id = move.line_ids.filtered(
                            #     lambda l: l.debit > 0)
                            for pl in move.line_ids:
                                if not payment_move_line_id:
                                    if pl.account_id.user_type_id.type in ('receivable', 'payable') and float_compare(abs(pl.amount_currency), line.amount, precision_digits=prec) == 0 and not pl.reconciled:
                                        payment_move_line_id = pl
                                    # break
                        else:
                            # payment_move_line_id = move.line_ids.filtered(
                            #     lambda l: l.credit > 0)
                            for pl in move.line_ids:
                                if not payment_move_line_id:
                                    if pl.account_id.user_type_id.type in ('receivable', 'payable') and float_compare(abs(pl.amount_currency), line.amount, precision_digits=prec) == 0 and not pl.reconciled:
                                        payment_move_line_id = pl
                                    # break
                        payment_move_line_id = payment_move_line_id and payment_move_line_id[0].id or False
                        if payment_move_line_id:
                            line.move_id.js_assign_outstanding_line(
                                line_id=payment_move_line_id)
            
            # update journal entry payment
            else:
                move = self.env['account.move'].sudo().search(
                        [('voucher_id', '=', self.id)])
                if move:
                    move.line_ids.unlink()
                    line_ids = self._prepare_move_line_single()
                    move.write({
                        'ref': self.notes or self.name,
                        'currency_id': self.currency_id.id,
                        'date': self.date,
                        'line_ids': line_ids
                    })
                    move.action_post()

                    # REASSIGN
                    # Jika move_id diisi, langsung alokasikan payment tadi ke move_id yang dipilih
                    for line in inv_bills:
                        # hanya untuk yg full payment
                        # if (line.payment_difference_handling == 'reconcile' and line.amount != line.move_residual_amount) or (line.amount == line.move_residual_amount):
                        if True:
                            # js_assign_outstanding_line(self, line_id) -> method yang dijalankan ketika klik add di outstanding payments
                            payment_move_line_id = False
                            if self.voucher_type == 'out':
                                # payment_move_line_id = move.line_ids.filtered(
                                #     lambda l: l.debit > 0)
                                for pl in move.line_ids:
                                    if not payment_move_line_id:
                                        if pl.account_id.user_type_id.type in ('receivable', 'payable') and float_compare(abs(pl.amount_currency), line.amount, precision_digits=prec) == 0 and not pl.reconciled:
                                            payment_move_line_id = pl
                                        # break
                            else:
                                # payment_move_line_id = move.line_ids.filtered(
                                #     lambda l: l.credit > 0)
                                for pl in move.line_ids:
                                    if not payment_move_line_id:
                                        if pl.account_id.user_type_id.type in ('receivable', 'payable') and float_compare(abs(pl.amount_currency), line.amount, precision_digits=prec) == 0 and not pl.reconciled:
                                            payment_move_line_id = pl
                                        # break
                            payment_move_line_id = payment_move_line_id and payment_move_line_id[0].id or False
                            if payment_move_line_id:
                                line.move_id.js_assign_outstanding_line(
                                    line_id=payment_move_line_id)

        else:
            # journal entry
            # if create new journal entry
            if not self.posted_before:
                self._create_new_entry()
            else:
                # update journal entry
                move_id = self.env['account.move'].sudo().search(
                        [('voucher_id', '=', self.id)])
                if move_id:
                    move_id.line_ids.unlink()
                    line_ids = self._prepare_move_line()
                    move_id.write({
                        'ref': self.notes or self.name,
                        'currency_id': self.currency_id.id,
                        'date': self.date,
                        'line_ids': line_ids
                    })
                    move_id.action_post()
        
        # update state
        self.write({
            'state': 'post',
            'posted_before': True,
        })

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if vals.get('voucher_type') == 'out':
                code = 'seq.voucher.default_out'
            else:
                code = 'seq.voucher.default_in'
            # TODO code berikut tidak dipakai, nomor dg sequence tersendiri
            # if vals.get('journal_id'):
            #     journal = self.env['account.journal'].sudo().browse(
            #         int(vals.get('journal_id')))
            #     if journal and journal.seq_code_voucher:
            #         check_sequence = self.env['ir.sequence'].sudo().search(
            #             [('code', '=', journal.seq_code_voucher)])
            #         if check_sequence:
            #             code = journal.seq_code_voucher
            #     elif journal and journal.code:
            #         code_journal = 'seq.voucher.'+journal.code
            #         check_sequence = self.env['ir.sequence'].sudo().search(
            #             [('code', '=', code_journal)])
            #         if check_sequence:
            #             code = code_journal
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code(
                code) or _('New')
        result = super(AccountVoucher, self).create(vals)
        return result

    def action_reset_to_draft(self):
        for voucher in self:
            if voucher.state in ('post', 'cancel'):
                account_move = self.env['account.move'].search(
                    [('voucher_id', '=', voucher.id)])
                account_payment = self.env['account.payment'].search(
                    [('voucher_id', '=', voucher.id)])
                if account_payment:
                    account_payment.action_draft()
                if account_move:
                    account_move.button_draft()
                self.write({'state': 'draft'})

    def action_cancel(self):
        for voucher in self:
            if voucher.state == 'draft':
                account_move = self.env['account.move'].search(
                    [('voucher_id', '=', voucher.id)
                     ])
                account_payment = self.env['account.payment'].search(
                    [('voucher_id', '=', voucher.id)])
                if account_payment:
                    account_payment.action_cancel()
                if account_move:
                    account_move.button_cancel()
                self.write({'state': 'cancel'})

    def write(self, vals):
        for move in self:
            if (move.posted_before and 'journal_id' in vals \
                and move.journal_id.id != vals['journal_id']):
                raise UserError(
                    _('You cannot edit the journal of an account move if it has been posted once.'))

        return super(AccountVoucher, self).write(vals)

    def unlink(self):
        for move in self:
            if move.posted_before:
                raise UserError(
                    _("You cannot delete an entry which has been posted once."))
        self.line_ids.unlink()
        return super(AccountVoucher, self).unlink()

    def _get_marks_and_numbers(self, row_idx):
        if row_idx == 1:
            return '1-38'
        elif row_idx == 2:
            return '39-104'
        elif row_idx == 3:
            return '105-120'
        elif row_idx == 4:
            return '121-220'
        elif row_idx == 5:
            return '221-290'
        elif row_idx == 6:
            return '291-360'
        else:
            return ''
    
    def rupiah_to_euro(self, price):
        conversion_rate = self.env['res.currency'].search([('name', '=', 'EUR')], limit=1).rate
        return price * conversion_rate
    
    def get_unique_refs(self):
        if self.ref:
            refs_list = self.ref.split(", ")
            unique_refs_list = list(set(refs_list))
            unique_refs = ", ".join(unique_refs_list)
            return unique_refs
        else:
            pass

    def amount_to_words_id(self, amount):
        angka = ["","Satu","Dua","Tiga","Empat","Lima","Enam",
                 "Tujuh","Delapan","Sembilan","Sepuluh","Sebelas"]
        hasil = " "
        n = int(amount)
        if n >= 0 and n <= 11:
            hasil = angka[n]
        elif n < 20:
            hasil = self.amount_to_words_id(n - 10) + " Belas "
        elif n < 100:
            hasil = self.amount_to_words_id(n // 10) + " Puluh " + self.amount_to_words_id(n % 10)
        elif n < 200:
            hasil = "Seratus " + self.amount_to_words_id(n - 100)
        elif n < 1000:
            hasil = self.amount_to_words_id(n // 100) + " Ratus " + self.amount_to_words_id(n % 100)
        elif n < 2000:
            hasil = "Seribu " + self.amount_to_words_id(n - 1000)
        elif n < 1000000:
            hasil = self.amount_to_words_id(n // 1000) + " Ribu " + self.amount_to_words_id(n % 1000)
        elif n < 1000000000:
            hasil = self.amount_to_words_id(n // 1000000) + " Juta " + self.amount_to_words_id(n % 1000000)
        elif n < 1000000000000:
            hasil = self.amount_to_words_id(n // 1000000000) + " Milyar " + self.amount_to_words_id(n % 1000000000)
        elif n < 1000000000000000:
            hasil = self.amount_to_words_id(n // 1000000000000) + " Triliyun " + self.amount_to_words_id(n % 1000000000000)
        elif n == 1000000000000000:
            hasil = "Satu Kuadriliun"
        else:
            hasil = "Angka Hanya Sampai Satu Kuadriliun"
        
        return hasil
        
    @api.depends('line_ids.amount','line_ids.tax_amount')
    def _amount_all(self):
        for order in self:
            payment_amount = amount_ppn = 0.0
            for line in order.line_ids:
                line._compute_amount()
                payment_amount += line.amount
                amount_ppn += line.tax_amount
            currency = order.currency_id or order.partner_id.property_purchase_currency_id or self.env.company.currency_id
            order.update({
                'payment_amount': payment_amount,
                'amount_ppn': amount_ppn,
                'amount_total': payment_amount + amount_ppn
            })

class AccountVoucherLine(models.Model):
    _name = 'account.voucher.line'
    _description = 'Voucher Payment Details'

    name = fields.Char(string='Number', default=lambda self: _('New'), index=True,)
    description = fields.Char(string='Description')
    account_id = fields.Many2one(
        comodel_name='account.account', string='COA', check_company=True,)
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', related="voucher_id.company_id", store=True)
    voucher_type = fields.Selection(string='Voucher Type', selection=[
                                    ('in', 'In'),
                                    ('out', 'Out'),],
                                    related="voucher_id.voucher_type", store=True)
    date = fields.Date(string='Payment Date', required=True,
                       default=fields.Date.today())
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')
    voucher_id = fields.Many2one(
        comodel_name='account.voucher', string='Voucher')
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency', related="voucher_id.currency_id", store=True)
    amount = fields.Monetary(string='Payment Amount',
                             currency_field="currency_id", store=True, required=True)
    amount_with_extra = fields.Monetary(string='Payment Amount (With Extra)',
                                        currency_field="currency_id", compute="_compute_amount_with_extra", store=True)
    domain_account = fields.Char(
        string='Domain Account', compute="_compute_domain_account", store=True)
    move_id = fields.Many2one(comodel_name='account.move', string='Invoice/Bill', copy=False)
    # invoice_sc_id = fields.Many2one(comodel_name='sale.order', string='Invoice/Bill', copy=False)
    # invoice_po_id = fields.Many2one(comodel_name='purchase.order', string='Invoice/Bill', copy=False)
    invoice_sc_id = fields.Many2one(comodel_name='sale.order', string='Sale Confirmation', copy=False)
    invoice_po_id = fields.Many2one(comodel_name='purchase.order', string='Purchase Order', copy=False)
    code = fields.Char(string='A/C. Code')
    payment_difference_handling = fields.Selection(selection=[
        ('open','Keep Open'),
        ('reconcile','Mark as fully paid'),], default=False,
        string="Payment Difference")
    writeoff_account_id = fields.Many2one(comodel_name='account.account',
        string='Post Difference In', check_company=True,)
    writeoff_label = fields.Char(string='Label', default='Write-Off')
    selisih_amount = fields.Boolean(string='Selisih Amount', 
        compute="_compute_amount_with_extra", store=True,)
    # for currency exchange
    is_currency_exchange = fields.Boolean(string='Is Currency Exchange', default=False,
        help="Check if this line is currency exchange")
    exchange_currency_id = fields.Many2one(comodel_name='res.currency',
        string='Exchange Currency', help="Currency for exchange", default=False,)
    exchange_rate = fields.Monetary(string='Currency Exchange Rate', default=1.0,
        currency_field='currency_id', help="Currency Exchange Rate (1 `Exchange Currency` = rate * 1 `Currency in voucher`)",)
    # move residual amount
    move_residual_amount = fields.Monetary(string='Residual Amount', currency_field="currency_id",
        default=0.0,)
    is_required_handling = fields.Boolean(string='Is Required Handling', default=False,)
    taxes_ids = fields.Many2many('account.tax', string='Taxes')
    tax_amount = fields.Monetary(compute='_compute_amount', string='Tax Amount', store=True)
    coa = fields.Char('COA')
    keterangan = fields.Char('Keterangan')
    
    
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price')
    order_id = fields.Many2one('purchase.order', string='Order Reference', index=True, required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    fee = fields.Float(inverse='_inverse_price', string='Fee',store=True)
    price_fee_subtotal = fields.Monetary(compute='_compute_price_fee_subtotal',string='Subtotal Fee', default=0.00,store=True)

    # @api.depends('product_qty', 'price_unit', 'taxes_ids')
    # def _compute_amount(self):
    #     for line in self:
    #         vals = line._prepare_compute_all_values()
    #         taxes = line.taxes_ids.compute_all(
    #             vals['price_unit'],
    #             vals['currency_id'],
    #             vals['product_qty'],
    #             vals['product'],
    #             vals['partner'])
    #         line.update({
    #             'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
    #             'price_total': taxes['total_included'],
    #             'price_subtotal': taxes['total_excluded'],
    #         })

    selected_currency_id = fields.Many2one(
        comodel_name='res.currency', string='Selected Currency', store=True)

    @api.onchange('invoice_sc_id')
    def onchange_invoice_sc_id(self):
        if self.invoice_sc_id:
            pricelist_id = self.invoice_sc_id.pricelist_id
            self.selected_currency_id = pricelist_id.currency_id
            if self.voucher_id:
                self.voucher_id.write({'selected_currency_id': pricelist_id.currency_id.id})

    @api.onchange('invoice_po_id')
    def onchange_invoice_po_id(self):
        if self.invoice_po_id:
            currency_id = self.invoice_po_id.currency_id
            self.selected_currency_id = currency_id
            if self.voucher_id:
                self.voucher_id.write({'selected_currency_id': currency_id.id})
            
    @api.depends('amount', 'taxes_ids')
    def _compute_amount(self):
        for line in self:
            tax_percentage = 0
            if line.taxes_ids:
                tax = line.taxes_ids[0]
                tax_percentage = tax.amount or 0

            line.tax_amount = (line.amount * tax_percentage) / 100        

    # def _prepare_compute_all_values(self):
    #     self.ensure_one()
    #     return {
    #         'price_unit': self.price_unit,
    #         'currency_id': self.order_id.currency_id,
    #         'product_qty': self.product_qty,
    #         'product': self.product_id,
    #         'partner': self.order_id.partner_id,
    #     }

    @api.depends('order_id','fee','product_qty')    
    def _compute_price_fee_subtotal(self):
        for rec in self:
            rec.price_fee_subtotal = rec.fee * rec.product_qty

    # === On Change ===
    @api.onchange('account_id', 'is_currency_exchange')
    def _onchange_account_id_is_currency_exchange(self):
        if self.is_currency_exchange and self.account_id:
            self.exchange_currency_id = self.account_id.currency_id.id or False
            self.exchange_rate = self.account_id.currency_id.with_context(
                date=self.voucher_id.date).rate_rp
        else:
            self.exchange_currency_id = False
            self.exchange_rate = 1.0

    @api.onchange('move_id')
    def _onchange_payment_amount(self):
        if self.move_id:
            self.amount = self.move_id.amount_residual
            self.move_residual_amount = self.move_id.amount_residual
    
    @api.onchange('move_id', 'amount', 'move_residual_amount')
    def _onchange_move_amount(self):
        if self.move_id:
            if self.amount != self.move_residual_amount:
                self.is_required_handling = True
            else:
                self.is_required_handling = False
        else:
            self.is_required_handling = False

    # === Compute ===
    # TODO remove me if no needed!!!!
    @api.depends('amount')
    def _compute_amount_with_extra(self):
        for i in self:
            amount_extra = 0
            i.amount_with_extra = i.amount + amount_extra
            i.selisih_amount = i.amount != i.amount_with_extra

    @api.depends('account_id')
    def _compute_domain_account(self):
        for i in self:
            if i.account_id:
                i.domain_account = i.account_id.internal_type
            else:
                i.domain_account = False

    # === Constrains ===
    @api.constrains('is_currency_exchange', 'exchange_currency_id', 'exchange_rate', 'account_id')
    def _check_is_currency_exchange(self):
        for record in self:
            if record.is_currency_exchange:
                if not record.exchange_currency_id:
                    raise ValidationError(_("Please fill Exchange Currency"))
                if record.account_id.currency_id and record.exchange_currency_id != record.account_id.currency_id:
                    raise ValidationError(_("Exchange Currency must be same with Account Currency"))
                if not record.exchange_rate:
                    raise ValidationError(_("Please fill Exchange Rate"))
    
    
    # === Action / Model ===
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            code = 'account.voucher.line'
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code(
                code) or _('New')
        result = super(AccountVoucherLine, self).create(vals)
        return result

    @api.onchange('partner_id')
    def _partner_onchange(self):
        moves =self.env['account.move'].search([
                ('state','=','posted'),
                ('amount_residual','>',0)

            ])
        if self.partner_id:
            moves =self.env['account.move'].search([
                '|',
                ('partner_id.parent_id','=',self.partner_id.id),
                ('partner_id','=',self.partner_id.id),
                ('state','=','posted'),
                ('amount_residual','>',0)
            ])
        move_list = []
        for data in moves:
            move_list.append(data.id)

        res = {}
        res['domain'] = {'move_id': [('id', 'in', move_list)]}
        return res

# TODO remove me
# class AccountVoucherExtra(models.Model):
#     _name = 'account.voucher.extra'
#     _description = 'Voucher Payment Extra Details'

#     description = fields.Char(string='Description', required=True)
#     company_id = fields.Many2one(
#         comodel_name='res.company', string='Company', related="line_id.company_id", store=True)
#     voucher_type = fields.Selection(string='Voucher Type', selection=[
#                                     ('in', 'In'), ('out', 'Out'), ], related="line_id.voucher_type", store=True)
#     line_id = fields.Many2one(
#         comodel_name='account.voucher.line', string='Voucher')
#     currency_id = fields.Many2one(
#         comodel_name='res.currency', string='Currency', related="line_id.currency_id", store=True)
#     amount = fields.Monetary(string='Payment Amount',
#                              currency_field="currency_id", required=True)
#     code = fields.Char(string='A/C. Code')
