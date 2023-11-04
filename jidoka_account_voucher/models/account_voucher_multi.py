# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2022 aiksuwandra@gmail.com
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from num2words import num2words


TYPE_SELECTION = [
    ('out_invoice','Penerimaan'),
    ('in_invoice','Pengeluaran'),
    ('out_refund','Kontra Bon - Customer'),
    ('in_refund','Kontra Bon - Vendor'),
]


class AccountMove(models.Model):
    _inherit = "account.move"


    multi_inv_id = fields.Many2one(
        'voucher.multi.invoice',
        string='Voucher Multi Invoice',
    )
    multi_inv_discount = fields.Monetary(readonly=True, default=0.0)
    multi_inv_amount_tax = fields.Monetary(readonly=True, default=0.0)
    multi_inv_amount = fields.Monetary(readonly=True, default=0.0)


class VoucherMultiInvoice(models.Model):
    _name = 'voucher.multi.invoice'
    _description = 'Voucher Multi Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(
        'No. Dokumen', default=None, copy=False,
        readonly=True, states={'draft': [('readonly', False)]})
    ref = fields.Char(
        'Reference',
        readonly=True, states={'draft': [('readonly', False)]})
    note = fields.Text(
        readonly=True, states={'draft': [('readonly', False)]})
    type = fields.Selection(
        TYPE_SELECTION, "Tipe", required=True, default='out_invoice',
        change_default=True,
        readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one(
        'res.partner', string='Partner',
        readonly=True, states={'draft': [('readonly', False)]})
    commercial_partner_id = fields.Many2one('res.partner', string='Commercial Entity', compute_sudo=True,
        related='partner_id.commercial_partner_id',
        store=True, readonly=True,
        help="The commercial entity that will be used on Journal Entries for this invoice")
    vendor_partner_id = fields.Char(
        'Vendor',
        readonly=True, states={'draft': [('readonly', False)]})
    ext_no = fields.Char(
        'No.Cek/BG',
        readonly=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one(
        'account.journal', string='Journal', required=True,
        # domain=[('type', 'in', ('bank', 'cash'))],
        readonly=True, states={'draft': [('readonly', False)]})
    discount_account_id = fields.Many2one(
        'account.account', string='Akun Discount',
        readonly=True, states={'draft': [('readonly', False)]})
    payment_type = fields.Selection([
        ('Manual', "Manual"), ('Invoice', "Invoice/Bill")],
        default='Invoice',
        readonly=True, states={'draft': [('readonly', False)]})
    register_payment_id = fields.Many2one('account.journal', string='Payment',
        domain=[('type', 'in', ('bank', 'cash'))], readonly=True)
    date = fields.Date(
        'Payment Date', required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    date_effective = fields.Date(
        'Tanggal Efektif',
        readonly=True, states={'draft': [('readonly', False)]})
    date_start = fields.Date(
        'Dari',
        readonly=True, states={'draft': [('readonly', False)]})
    date_end = fields.Date(
        'Sampai',
        readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one(
        'res.company','Company', required=True,
        default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one(
        'res.currency','Currency',
        related='partner_id.property_product_pricelist.currency_id')
    invoice_ids = fields.One2many(
        'voucher.multi.invoice.line', 'voucher_id', string='Invoices',
        readonly=True, states={'draft': [('readonly', False)]})
    line_ids = fields.One2many(
        'voucher.multi.invoice.line', 'voucher_id', string='Payments',
        readonly=True, states={'draft': [('readonly', False)]})
    amount = fields.Monetary('Total Amount', compute='_compute_amount')
    amount_voucher = fields.Monetary(
        'Total Voucher', readonly='1', default=0.0)
    amt_outstanding = fields.Monetary(
        'Total Outstanding', compute='_compute_amount')
    amt_curr_outstanding = fields.Monetary(
        'Current Outstanding', compute='_compute_amount')
    amount_tax = fields.Monetary(
        'Total Pajak', compute='_compute_amount')
    move_ids = fields.One2many(
        'account.move',
        'multi_inv_id',
        string='Moves',
    )
    analytic_account_id = fields.Many2one('account.analytic.account', string='WBS / Cost Center')
    state = fields.Selection(
        [('draft', "Draft"), ('done', "Done"),('cancel','Cancel')],
        "Status", default='draft')
    keterangan = fields.Text('Description', copy=False)
    search_type = fields.Selection(
        string='Search Type', 
        selection=[('invoice_date', 'Invoice Date'), 
                   ('due_date', 'Due Date'),], 
        default='invoice_date',
        states={'draft': [('readonly', False)]},
    )
    mark_as_fully_paid = fields.Boolean(string='Mark Full Paid')
    reconcile_account_id = fields.Many2one('account.account', string='Reconcile Account')
    reconcile_amount = fields.Float(string='Reconcile Amount')
    reconcile_writeoff_label = fields.Char(string='Label')


    #Task JM-637
    @api.model
    def create(self, values):
        if values.get('type') == 'in_invoice' or values.get('type') == 'in_refund':
            journal_bill = values.get('journal_id')
            journal_bill_id = self.env['account.journal'].browse(journal_bill)
            if not journal_bill_id.bill_sequence_id:
                raise ValidationError(
                        _("You must set bill Sequence In Journal Master!")
                    )
            sequence_bill = self.env['ir.sequence'].next_by_code(journal_bill_id.bill_sequence_id.code)
            # values['name'] = sequence_bill.replace('/','')
            values['name'] = sequence_bill
        else:
            journal_invoice = values.get('journal_id')
            journal_invoice_id = self.env['account.journal'].browse(journal_invoice)
            if not journal_invoice_id.invoice_sequence_id:
                raise ValidationError(
                        _("You must set invoice Sequence In Journal Master!")
                    )
            sequence_invoice = self.env['ir.sequence'].next_by_code(journal_invoice_id.invoice_sequence_id.code)
            # values['name'] = sequence_invoice.replace('/','')
            values['name'] = sequence_invoice

        return super(VoucherMultiInvoice, self).create(values)
    #End Task JM-637

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if self.payment_type == 'Invoice' and self.type == 'in_invoice':
            self.journal_id = 2
        elif self.payment_type == 'Invoice' and self.type == 'out_invoice':
            self.journal_id = 1

    @api.onchange('invoice_ids', 'company_id')
    @api.depends('invoice_ids.subtotal', 'invoice_ids.amount_invoice', 'company_id')
    def _compute_amount(self):
        for pay in self:
            currency_id = pay.currency_id
            if not currency_id:
                pay.currency_id = pay.company_id.currency_id
            if pay.invoice_ids:
                pay.amt_outstanding = sum(pay.invoice_ids.mapped('amount_invoice'))
                pay.amt_curr_outstanding = sum(pay.invoice_ids.mapped('current_residu'))
                pay.amount = sum(pay.mapped('invoice_ids.subtotal'))
                pay.amount_tax = sum(pay.invoice_ids.mapped('amount_tax'))
            else:
                pay.amt_outstanding = 0
                pay.amt_curr_outstanding = 0
                pay.amount = 0
                pay.amount_tax = 0

    def action_register_payment_custom(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        for rec in self:
        # inv = self.env['voucher.multi.invoice'].with_context(active_id=False).search([('id', '=', self.env.context.get('active_id'))])
            amount_total_signed = sum(self.env['account.move'].search([('multi_inv_id','=', rec.id)]).mapped('amount_total_signed'))
            print("========================================", amount_total_signed)
            if rec.payment_type == 'Invoice' and rec.amt_curr_outstanding == 0 and (rec.type == 'in_invoice' or rec.type == 'out_invoice'):
                raise UserError(("Tidak bisa melakukan register payment, karena sudah paid"))
            else:
                default_journal = self.journal_id
                if self.journal_id.type not in ('bank', 'cash'):
                    default_journal = self.env['account.journal'].sudo().search([('type','in',('bank', 'cash'))], limit=1)
                if amount_total_signed <= 0:
                    return {
                            'name': _('Register Payment'),
                            'res_model': 'payment.register.custom',
                            'view_mode': 'form',
                            'view_type': 'form',
                            'context': {
                                'active_model': 'account.move',
                                'active_ids': self.ids,
                                'default_amount': self.amount,
                                'default_amt_curr_outstanding': self.amt_curr_outstanding,
                                'default_type':self.type,
                                'default_payment_type':self.payment_type,
                                'default_journal_id': default_journal.id
                            },
                            'target': 'new',
                            'type': 'ir.actions.act_window',
                        }
                else:
                    return {
                            'name': _('Register Payment'),
                            'res_model': 'payment.register.custom',
                            'view_mode': 'form',
                            'view_type': 'form',
                            'context': {
                                'active_model': 'account.move',
                                'active_ids': self.ids,
                                'default_amount': (self.payment_type == 'Invoice') and self.amt_curr_outstanding or self.amount,
                                'default_amt_curr_outstanding': self.amt_curr_outstanding,
                                'default_type':self.type,
                                'default_payment_type':self.payment_type,
                                'default_journal_id': default_journal.id
                            },
                            'target': 'new',
                            'type': 'ir.actions.act_window',
                        }

    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        return {
            'date': self.date,
            'ref': self.name or '',
            'company_id': self.company_id.id,
            'journal_id': journal.id,
            'name': self.name,
        }

    def compute_account(self, invoice_id):
        account_id = False
        if invoice_id.partner_id:
            partner = invoice_id.partner_id.with_company(self.company_id.id)
            if invoice_id.move_type in ('out_invoice', 'in_refund'):
                account_id = invoice_id.custom_account_receivable_id.id
            elif invoice_id.move_type in ('in_invoice', 'out_refund'):
                account_id = invoice_id.custom_account_payable_id.id
        return account_id

    def auto_invoice(self):

        self.ensure_one()
        domain = [
            ('state','=','posted'),
            ('amount_residual','>',0),
            ('move_type', '=', self.type),
            ('partner_id', '=', self.partner_id.id),
            ('company_id', '=', self.company_id.id),]
        if self.search_type == 'invoice_date':
            if self.date_start:
                domain.append(('date', '>=', self.date_start))
            if self.date_end:
                domain.append(('date', '<=', self.date_end))
        elif self.search_type == 'due_date':
            if self.date_start:
                domain.append(('invoice_date_due', '>=', self.date_start))
            if self.date_end:
                domain.append(('invoice_date_due', '<=', self.date_end))
        invs = self.env['account.move'].sudo().search(domain)
        if invs:
            prev_vals = dict([(i.invoice_id.id, {
                'name': i.name,
                'account_id': i.account_id and i.account_id.id,
                'amount_tax': i.amount_tax,
                'amount': i.amount,
                'discount': i.discount})
                for i in self.invoice_ids])
            if self.invoice_ids:
                self.invoice_ids.unlink()
            inv_ids = []
            for j in invs:
                account_id = self.compute_account(j)
                inv_ids.append((0, 0, dict({
                    'invoice_id': j.id, 'account_id': account_id,
                    'name': j.name, 'date_invoice':j.date, 'amount':j.amount_residual,
                    'state': j.state, 'partner_id': j.partner_id.id},
                    **prev_vals.get(j.id, {}))))
            self.invoice_ids = inv_ids

    def _check_total(self):
        total = 0.0
        for obj in self:
            total += sum(obj.invoice_ids.mapped('subtotal'))
        if total == 0.0:
            raise UserError('Pembayaran harus ada!')

    def _check_discount(self):
        discount = 0
        for obj in self:
            obj.invoice_ids._check_discount()
            obj_discount = sum(obj.invoice_ids.mapped('discount'))
            discount += obj_discount
            if obj_discount > 0.0 and not obj.discount_account_id:
                raise UserError("Isi Akun Discount!")
        return discount

    def unlink(self):
        for voucher in self:
            if voucher.state == 'done':
                raise UserError(
                    "Voucher tidak dapat dihapus ID[%s] %s" %  (
                        voucher.id, voucher.name or " ")
                )
        return super(VoucherMultiInvoice, self).unlink()

    def print_voucher(self):
        return self.env.ref('jidoka_account_voucher.report_voucher_multi_invoice_action').report_action(self)

        # report_ref = {
        #     'out_invoice': 'jidoka_account_voucher.report_voucher_multi_action',
        #     'in_invoice': 'jidoka_account_voucher.report_voucher_multi_action',
        #     'out_refund': 'jidoka_account_voucher.report_voucher_multi_action',
        #     'in_refund': 'jidoka_account_voucher.report_voucher_multi_action',
        # }
        # report_name = report_ref.get(self.type)
        # return self.env.ref(report_name).report_action(self)
    def amount_to_text(self, amount):
        words = str(float(amount)).split('.')[0]
        words = num2words(float(words), lang='id').title()
        number_to_words = words.replace("Koma Nol", "")
        number_to_words += "Rupiah"
        return number_to_words

    def reset_voucher_multi_val_once(self):
        line_obj = self.env['voucher.multi.invoice.line']
        line_ids = line_obj.sudo().search([])
        invoice_ids = line_ids.mapped('invoice_id')
        invoice_ids.write({
            'multi_inv_discount': 0,
            'multi_inv_amount_tax': 0,
        })
        line_ids.set_voucher_multi_val()

    def action_cancel(self):
        if self.move_ids:
            self.move_ids.button_draft()
            self.move_ids.button_cancel()
        # self.move_ids.unlink()
        self.write({'state':'cancel'})


class VoucherMultiInvoiceLine(models.Model):
    _name = 'voucher.multi.invoice.line'
    _description = 'Voucher Multi Invoice Detail'


    voucher_id = fields.Many2one('voucher.multi.invoice')
    payment_type = fields.Selection(related='voucher_id.payment_type')
    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice#',
        readonly=False, states={'paid': [('readonly', True)]}, copy=False
    )
    account_id = fields.Many2one(
        'account.account', string='Account', )
    name = fields.Char('Description', )
    amount_invoice = fields.Monetary(
        'Outstanding', readonly=True, default=0)
    current_residu = fields.Monetary(
        'Curent Outstanding',
        related='invoice_id.amount_residual', readonly=True, store=True)
    amount_invoice_tax = fields.Monetary(
        'Tax Outstanding',
        related='invoice_id.amount_tax', readonly=True, store=True)
    date_invoice = fields.Date(
        'Invoice Date', related='invoice_id.date', store=True)
    date_payment = fields.Date(
        'Payment Date', default=fields.Date.today(), required=True)
    invoice_date_due = fields.Date(
        'Due Date', related='invoice_id.invoice_date_due', store=True)
    partner_id = fields.Many2one(
        'res.partner', string='Partner',
        readonly=True, states={'draft': [('readonly', False)]})
    amount_tax = fields.Monetary(
        'Tax Payment', required=True, default=0.0,
        readonly=False, states={'paid': [('readonly', True)]})
    amount = fields.Monetary(
        'Payment', required=True,
        readonly=False, states={'paid': [('readonly', True)]})
    discount = fields.Monetary(
        readonly=False, states={'paid': [('readonly', True)]},
        default=0.0)
    company_id = fields.Many2one(
        'res.company','Company', related='voucher_id.company_id', store=True)
    currency_id = fields.Many2one(
        'res.currency','Currency', related='invoice_id.currency_id', store=True)
    subtotal = fields.Float(compute='_compute_subtotal' )
    state = fields.Selection([
            ('draft','Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ], "Status", readonly=True, default='draft')
    # amount_pph = fields.Monetary(string='PPH', compute='_compute_get_amount_residual', store=True)


    # @api.depends('invoice_id')
    # def _compute_get_amount_residual(self):
    #     for rec in self:
    #         rec.amount_pph = rec.invoice_id.amount_pph

    # @api.onchange('amount_tax', 'amount', 'discount')
    @api.depends('amount_tax', 'amount', 'discount')
    def _compute_subtotal(self):
        for obj in self:
            obj.subtotal = obj.amount + obj.amount_tax

    @api.onchange('voucher_id', 'invoice_id')
    # @api.depends('voucher_id', 'invoice_id')
    def onchange_residu(self):
        for obj in self:
            if obj.invoice_id and obj.voucher_id.state == 'draft':
                obj.amount_invoice = obj.invoice_id.amount_residual_signed

    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False, sign=1):
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        res = {}
        for obj in self:
            subtotal = obj.subtotal
            if subtotal == 0.0:
                continue
            if obj.invoice_id.currency_id.is_zero(subtotal):
                continue
            res[obj.id] = {
                'partner_id': obj.invoice_id and obj.invoice_id.partner_id._find_accounting_partner(obj.invoice_id.partner_id).id or False,
                'invoice_id': obj.invoice_id and obj.invoice_id.id or False,
                'move_id': move_id.id,
                'debit': subtotal if sign != 1 else 0,
                'credit': subtotal if sign == 1 else 0,
                'amount_currency': amount_currency or False,
                # 'payment_id': obj.id, set later
                'journal_id': move_id.journal_id.id,
            }
        return res

    def _get_counterpart_move_line_vals(self, name='', invoice=False):
        res = {}
        for obj in self:
            res[obj.id] = {
                'name': name,
                'account_id': obj.account_id.id,
                'currency_id': obj.currency_id != obj.company_id.currency_id and obj.currency_id.id or False,
            }
        return res

    def _get_liquidity_move_line_vals(self, move_id, sign=1):
        res = []
        voucher_info = self[0]._get_common_voucher_val()
        partner_id = voucher_info.get('partner_id')
        journal_id = voucher_info.get('journal_id')
        acc_id = voucher_info.get('acc_id')
        company_id = voucher_info.get('company_id')
        voucher_date = voucher_info.get('voucher_date')
        switch_amt = voucher_info.get('switch_amt')
        for obj in self:

            common_val = {
                'partner_id': partner_id,
                'move_id': move_id.id,
                'journal_id': journal_id.id,
            }

            liquidity_val = obj._get_aml_val(
                journal_id, acc_id, obj.subtotal, company_id,
                voucher_date, switch_amt)

            if liquidity_val:
                res.append(dict(common_val, **liquidity_val))

        return res

    def _get_common_voucher_val(self):
        voucher_id = self.voucher_id
        journal_id = voucher_id.journal_id
        partner_id = voucher_id.partner_id
        company_id = voucher_id.company_id
        tipe = voucher_id.type
        if tipe in ('out_invoice', 'in_refund'):
            acc_id = journal_id.payment_debit_account_id.id
            partner_acc_id = partner_id.property_account_receivable_id.id
            switch_amt = False
        else:
            acc_id = journal_id.payment_credit_account_id.id
            partner_acc_id = partner_id.property_account_payable_id.id
            switch_amt = True
        return {
            'voucher_name': voucher_id.name or '/',
            'voucher_date': voucher_id.date,
            'partner_id': partner_id.id,
            'journal_id': journal_id,
            'company_id': company_id,
            'switch_amt': switch_amt,
            'acc_id': acc_id,
            'partner_acc_id': partner_acc_id,
        }

    def _get_aml_disc_val(self, move_id):
        res = []
        voucher_info = self[0]._get_common_voucher_val()
        partner_id = voucher_info.get('partner_id')
        journal_id = voucher_info.get('journal_id')
        partner_acc_id = voucher_info.get('partner_acc_id')
        company_id = voucher_info.get('company_id')
        voucher_date = voucher_info.get('voucher_date')
        switch_amt = voucher_info.get('switch_amt')
        voucher_name = voucher_info.get('voucher_name')
        for obj in self:
            if obj.discount > 0.0:

                common_val = {
                    'partner_id': partner_id,
                    'move_id': move_id.id,
                    'journal_id': journal_id.id,
                }

                aml_name = "Discount:%s for Invoice:%s" % (
                    voucher_name, obj.invoice_id.name)

                disc_account_id = obj.voucher_id.discount_account_id and obj.voucher_id.discount_account_id.id
                disc_val = obj._get_aml_val(
                    journal_id, disc_account_id,
                    obj.discount, company_id,
                    voucher_date, switch_amt, aml_name)
                if disc_val:
                    res.append({
                        obj.invoice_id.id: dict(common_val, **disc_val)
                    })

                utang_piutang_val = obj._get_aml_val(
                    journal_id, partner_acc_id,
                    obj.discount, company_id,
                    voucher_date, not switch_amt, aml_name)
                if utang_piutang_val:
                    res.append({
                        obj.invoice_id.id: dict(common_val,
                        **utang_piutang_val)})

        return res

    def _get_aml_val(
            self, journal_id, account_id, amount, company_id, voucher_date,
            switch_amt, name=None):
        self.ensure_one()
        val = {}
        inv_id = self.invoice_id
        voucher_date = voucher_date or fields.Date.today()

        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if inv_id.journal_id.currency_id and inv_id.journal_id.currency_id != journal_id.currency_id:
            amount = journal_id.currency_id._convert(
                amount,
                inv_id.journal_id.currency_id,
                company_id,
                voucher_date)

        if inv_id.currency_id.is_zero(amount):
            return val

        val_aml = self.env['account.move.line']._get_fields_onchange_subtotal_model(
            amount, self.invoice_id.move_type,
            company_id.currency_id, company_id, voucher_date)
        debit = val_aml.get('debit', 0)
        credit = val_aml.get('credit', 0)
        amount_currency = val_aml.get('amount_currency', 0)
        if switch_amt:
            debit, credit =  credit, debit

        val['name'] = name or inv_id.name
        val['account_id'] = account_id
        val['amount_currency'] = amount_currency
        val['currency_id'] = journal_id.currency_id.id
        val['debit'] = debit
        val['credit'] = credit
        return val

    def _check_discount(self):
        for obj in self:
            if obj.amount <= 0.0 and obj.discount > 0.0:
                raise UserError(
                    "Discount tidak bisa untuk %s [Tanpa pembayaran]!" % obj.invoice_id.name)

    def set_voucher_multi_val(self):
        for obj in self:
            if obj.invoice_id and obj.discount > 0:
                obj.invoice_id.multi_inv_discount += obj.discount
                obj.invoice_id.multi_inv_amount_tax += obj.amount_tax
