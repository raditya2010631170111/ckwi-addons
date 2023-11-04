# -*- coding: utf-8 -*-

from datetime import datetime, date
from email.policy import default
from odoo.tools import float_round
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.tools import pycompat
from lxml import etree


class PaymentRequest(models.Model):
    _name = 'payment.request'
    _inherit = 'mail.thread'

    @api.depends('payment_line.amount')
    def _amount_all(self):
        for o in self:
            o.update({
                'amount': sum([l.amount for l in o.payment_line])
            })

    @api.depends('work_location', 'date')
    def _count_sisa_kas(self):
        data = self.env['payment.request'].search(
            [('type', '=', 'aap'), ('work_location', '=', self.work_location.id), ('date', '=', self.date)])
        count = 0.0
        for x in data:
            count += x.amount
        for y in self:
            y.sisa_kas_pengeluaran = count - y.amount

    @api.depends('user_id', 'type')
    def _filter_pengajuan_petty_cash(self):
        for x in self:
            data = self.env['hr.employee'].search(
                [('user_id', '=', self.env.user.id)])
            # print('==============', x.work_location.id,
            #       data.work_location_id.id, self.env.user.id)
            # if x.type == 'aap':
            if x.type == 'aap' and x.work_location.id == data.work_location_id.id:
                x.is_wilayah_pengajuan = True
                x.filter_pengajuan_petty_cash = 'filter_pengajuan'
            elif x.type == 'aap':
                x.is_wilayah_pengajuan = True
                x.filter_pengajuan_petty_cash = 'filter_pengajuan'
            else:
                x.is_wilayah_pengajuan = False
                x.filter_pengajuan_petty_cash = ''

    @api.depends('user_id', 'type')
    def _filter_pengeluaran_petty_cash(self):
        for x in self:
            data = self.env['hr.employee'].search(
                [('user_id', '=', self.env.user.id)])
            print('==============', x.work_location.id,
                  data.work_location_id.id, self.env.user.id)
            # if x.type == 'aap':
            if x.type == 'aap' and x.work_location.id == data.work_location_id.id:
                x.is_wilayah_pengeluaran = True
                x.filter_pengeluaran_petty_cash = 'filter_pengeluaran'
            elif x.type == 'aap':
                x.is_wilayah_pengeluaran = True
                x.filter_pengeluaran_petty_cash = 'filter_pengeluaran'
            else:
                x.is_wilayah_pengeluaran = False
                x.filter_pengeluaran_petty_cash = ''

    def _get_kas_journal(self):
        list_kas = []
        kas = self.env['account.journal'].search([('type', '=', 'cash')])
        for journal in kas:
            if self.env.user.id in journal.user_ids.ids:
                list_kas.append(journal.id)
        return list_kas

    name = fields.Char('Reference', default='/', readonly=True)
    date = fields.Date('Date', required=True, default=fields.Date.context_today, track_visibility='onchange')
    user_id = fields.Many2one('res.users', string='Responsible', readonly=True,
                              required=True, default=lambda self: self.env.user, copy=False)
    type_m = fields.Selection([('tambah', 'Penambahan Kas'),('kurang', 'Pengurangan Kas')], string="Type", default=False)
    start_balance = fields.Float(string='Starting Balance')
    end_balance = fields.Float(string='Ending Balance' ,compute="_compute_end_balance")

    

    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount')
    @api.onchange('journal_id')
    def _onchange_type_m(self):
        last_balance_request = self.search([('end_balance', '!=', False)], order='create_date desc', limit=1)
        if last_balance_request:
            self.start_balance = last_balance_request.end_balance
        else:
            self.start_balance = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        requests = super(PaymentRequest, self).create(vals_list)

        for request in requests:
            last_balance_request = self.search([('id', '!=', request.id), ('end_balance', '!=', False)], order='create_date desc', limit=1)
            if last_balance_request:
                request.start_balance = last_balance_request.end_balance
            else:
                request.start_balance = 0.0

        return requests

    @api.depends('type_m', 'total_amount', 'end_balance')
    def _compute_start_balance(self):
        for request in self:
            last_balance_request = self.search([('id', '<', request.id), ('end_balance', '!=', False)], order='create_date desc', limit=1)
            if last_balance_request:
                request.start_balance = last_balance_request.end_balance
            else:
                request.start_balance = 0.0

    @api.depends('type_m', 'total_amount', 'start_balance')
    def _compute_end_balance(self):
        for request in self:
            if request.type_m == 'tambah':
                request.end_balance = request.total_amount + request.start_balance
            elif request.type_m == 'kurang':
                request.end_balance =  request.start_balance - request.total_amount 
            else:
                request.end_balance = 0.0

    @api.depends('payment_line.amount')
    def _compute_total_amount(self):
        for request in self:
            request.total_amount = sum(request.payment_line.mapped('amount'))

    amount = fields.Monetary(
        'Amount', store=True, compute='_amount_all', track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True, track_visibility='onchange')
    # department_id = fields.Many2one(
    #     'hr.department', string='Department', track_visibility='onchange')
    department_id = fields.Many2one(
        'hr.department', string='Analytic Department', track_visibility='onchange')
    department = fields.Char(
        string='Department', track_visibility='onchange', related='employee_id.department_id.name')
    pembayaran_id = fields.Many2one('payment.request', 'Advance',
                                    readonly=True,track_visibility='onchange')
    payment_line = fields.One2many('payment.request.line', 'payment_id',
                                   'Payment Lines')
    approved_payment_line = fields.One2many(
        'payment.request.line', 'payment_id', 'Payment Lines', )
    # description = fields.Char('Description',  track_visibility='onchange')
    # reason = fields.Text('Reason', readonly=True, track_visibility='onchange')
    type = fields.Selection([('payment', 'Payment Request'), ('aap', 'Pengajuan Petty Cash'),
                            ('settle', 'Pengeluaran Petty Cash')], string='Type', required=True)
    state = fields.Selection([
        ('reject', 'Rejected'),
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('validate', 'Validate'),
        ('approve', 'Approved'),
        ('waiting', 'Waiting Approval'),
        ('paid', 'Paid'),
        ('cancel', 'Cancel'),
    ], string='Status', readonly=True, copy=False, default='draft', track_visibility='onchange')
    project_id = fields.Many2one(comodel_name='project.project', string='Project', readonly=True,)
    cara = fields.Selection([('cash', 'Cash'), ('transfer', 'Transfer')],
                            string='Method', default='transfer', required=True)
    nama_rekening = fields.Char('Rekening Name',  readonly=True, )
    nomor_rekening = fields.Char('Rekening Number', readonly=True,)
    nama_bank = fields.Char('Bank Name', readonly=True,)
    difference_payment_id = fields.Many2one(
        comodel_name='payment.request', string='Difference Payment Request', copy=False)
    difference = fields.Float(
        string='Difference', compute="_get_difference", store=True)
    move_settlement_id = fields.Many2one(
        'account.move', string="Settlement Entry", track_visibility='onchange', copy=False)
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account')
    work_location = fields.Many2one(
        'jidoka.worklocation', string='Work Location', compute='_work_location_by_creator')
    employee_id = fields.Many2one(
        'hr.employee', string='Employee')
    company_id = fields.Many2one('res.company', string='Company')
    account_ids = fields.Many2many(
        'account.journal', string='Kas', default=_get_kas_journal)
    account_id = fields.Many2one(
        'account.journal', string='Kas', widget='selection')

    num = fields.Float('num', default="15000000")
    currency_id = fields.Many2one('res.currency', string='currency')
    nampung = fields.Monetary(
        'nampung', compute="_compute_nampung", currency_field='currency_id')
    kas = fields.Monetary(string='Balance Remaining', currency_field='currency_id')
    sisa_kas_pengeluaran = fields.Monetary(
        string='Sisa Saldo', currency_field='currency_id', compute=_count_sisa_kas)
    bukti_kas = fields.Binary(string="Proof of Cash Expenditure")
    pengajuan_kas = fields.Binary(string="Proof of Cash Submission")
    filename_bukti_kas = fields.Char(
        string="Filename Bukti Pengeluaran Kas Hasil Inputan")
    filename_pengajuan_kas = fields.Char(
        string="Filename Bukti Pengajuan Kas")
    is_wilayah_pengajuan = fields.Boolean(
        compute=_filter_pengajuan_petty_cash)
    filter_pengajuan_petty_cash = fields.Char(
        compute=_filter_pengajuan_petty_cash, store=True)
    is_wilayah_pengeluaran = fields.Boolean(
        compute=_filter_pengeluaran_petty_cash)
    filter_pengeluaran_petty_cash = fields.Char(
        compute=_filter_pengeluaran_petty_cash)
    bill_approval_ids = fields.One2many(
        'bill.approval', 'payment_request_id', string='Approval')
    invoice_approval_ids = fields.One2many(
        'invoice.approval', 'payment_request_id', string='Approval')
    journal_id = fields.Many2one('account.journal', string='Journal',domain=[('type', '=', 'cash')])
    move_id = fields.Many2one('account.move', string='Journal Entry')
    reject_reason = fields.Text(string='Reject Reason')
    approve = fields.Boolean('approve', compute="_compute_test", default=True)
    waiting = fields.Boolean('waiting', compute="_compute_test", default=True)
    code_j = fields.Char(string='Code',store=True,)
    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id:
            self.code_j = self.journal_id.code
        else:
            self.code_j = ''
    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('payment.request') or '/'
        current_month = datetime.now().strftime("%m")
        code = vals.get('code_j') or ''
        vals['name'] = f"{sequence}/{current_month}/{code}"
        return super(PaymentRequest, self).create(vals)
    # @api.depends('')
    def _compute_test(self):
        for rec in self:
            user = rec.env.user
            rec.approve = True,
            rec.waiting = True,
            for a in rec.bill_approval_ids.filtered(lambda x: x.is_approved == False):
                if a.user_id.id == user.id and rec.state == 'confirm' :
                    rec.approve = False
                if a.user_id.id == user.id and rec.state == 'waiting' :
                    rec.waiting = False
                    
                    
                

    approval_ke = fields.Integer(default=0)
    approval_confirm = fields.Many2one('res.users')
    approval_confirm_date = fields.Datetime('Tanggal Confirm')
    approval_ke_1 = fields.Many2one('res.users')
    approval_ke_1_date = fields.Datetime('Tanggal Approve')
    approval_ke_2 = fields.Many2one('res.users')
    approval_ke_2_date = fields.Datetime('Tanggal Approve')
    approval_ke_3 = fields.Many2one('res.users')
    approval_ke_3_date = fields.Datetime('Tanggal Approve')
    approval_ke_4 = fields.Many2one('res.users')
    approval_ke_4_date = fields.Datetime('Tanggal Approve')
    approval_ke_5 = fields.Many2one('res.users')
    approval_ke_5_date = fields.Datetime('Tanggal Approve')

    message = fields.Text(string="Message", track_visibility='onchange')
    _message = fields.Text(string="Message", compute="_get_message")

    def _get_message(self):
        for x in self:
            x._message = x.message

    message_state = fields.Selection(
        selection=[('default', 'Default'), ('info', 'Info'), ('danger', 'Danger')], default='default')

    @api.onchange('account_id')
    def _onchange_sisa_kas(self):
        if self.account_id:
            currency = self.company_id.currency_id
            account_balance = self.account_id._get_journal_bank_account_balance(
                domain=[('parent_state', '=', 'posted')])
            self.kas = account_balance[0]

    def update_reject(self):
        if self.type == 'aap':
            to_approve = self.bill_approval_ids.filtered(
                lambda l: not l.is_approved).sorted(key=lambda x: x.sequence)
            if self.env.uid != to_approve[0].user_id.id:
                raise ValidationError(
                    _("You do not get access to reject this document!"))

        elif self.type == 'settle':
            to_approve = self.invoice_approval_ids.filtered(
                lambda l: not l.is_approved).sorted(key=lambda x: x.sequence)
            if self.env.uid != to_approve[0].user_id.id:
                raise ValidationError(
                    _("You do not get access to reject this document!"))

        view_id = self.env.ref(
            "aa_payment_request.reject_petty_cash_wizard_form")

        return {
            'name': _('Reject Petty Cash'),
            'res_model': 'reject.pettycash.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {'default_payment_request_id': self.id},
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    @api.depends('user_id','work_location','employee_id')
    def _work_location_by_creator(self):
        for x in self:
            data = self.env['hr.employee'].search(
                [('user_id', '=', x.user_id.id)], limit=1)
            x.work_location = data.work_location_id.id

    @api.onchange('kas', 'type')
    def _onchange_kas(self):
        # for record in self:
        if self.kas == 5000000 and self.type == 'aap':
            vals = {
                'name': '[Auto Generated] Pengajuan Sisa Kas 5jt',
                'amount': 10000000
            }
            self.payment_line = [(0, 0, vals)]

    @api.onchange('work_location')
    def _onchange_employee_id(self):
        for x in self:
            return {'domain': {'employee_id': [('work_location_id', '=', x.work_location.id)]}}

    @api.constrains('nampung', 'num')
    def _constrains_amount(self):
        for a in self:
            if type == 'aap':
                if a.nampung > a.num:
                    raise ValidationError(
                        "Pengisian Kas tidak boleh lebih dari Rp. 15.000.000 ")

    @api.depends('nampung')
    def _compute_nampung(self):
        for rec in self:
            rec.nampung = rec.kas + rec.amount

    # @api.model
    # def create(self, vals):
    #     nama = '/'
    #     if self._context.get('use_apr'):
    #         nama = self.env['ir.sequence'].next_by_code('payment.request')
    #         vals['name'] = nama
    #         return super(PaymentRequest, self).create(vals)
    #     if vals['type'] == 'payment':
    #         nama = self.env['ir.sequence'].next_by_code('payment.request')
    #     elif vals['type'] == 'aap':
    #         nama = self.env['ir.sequence'].next_by_code(
    #             'approval.advance.payment')
    #     elif vals['type'] == 'settle':
    #         nama = self.env['ir.sequence'].next_by_code('approval.settlements')
    #     vals['name'] = nama
    #     return super(PaymentRequest, self).create(vals)

    def payment_draft(self):
        for rec in self:
            if rec.type == 'aap':
                rec.bill_approval_ids.unlink()
                rec.write({
                    'approval_ke': 0,
                    'message_state': 'info',
                    'message': "Pengajuan Petty Cash rejected by {} on {}".format(self.env.user.name,
                                                                                  fields.date.today())})
            elif rec.type == 'settle':
                rec.invoice_approval_ids.unlink()
            return rec.write({'state': 'draft'})

    def payment_validate(self):
        for o in self:
            return o.write({'state': 'validate'})

    def payment_confirm(self):
        for rec in self:
            job_position = ''
            type_petty = ''
            tanggal_pengajuan = self.date.strftime('%d-%B-%Y')
            doc_number = self.name
            account = str(self.account_id.default_account_id.code) + \
                ' ' + str(self.account_id.default_account_id.name)
            amount = sum(self.payment_line.mapped('amount'))
            req_by = self.user_id.name
            # note = self.description
            email_to = ''
            email_from = self.user_id.company_id.email
            if rec.type == 'aap':
                approval = rec.work_location.submission_aproval_ids
                if not approval:
                    raise ValidationError(
                        _('You have to configure data approval in the your work location!'))

                approval_list = []
                for approv in approval:
                    vals = {
                        'user_id': approv.user_id.id,
                        'sequence': approv.sequence,
                    }
                    approval_list.append((0, 0, vals))
                rec.approval_ke += 1
                rec.bill_approval_ids = approval_list
                job_position = rec.bill_approval_ids[0].user_id.employee_id.job_id.name
                type_petty = 'Pengajuan Petty Cash'
                email_to = rec.bill_approval_ids[0].user_id.employee_id.work_email
                rec.write({
                    'state': 'confirm',
                    'message_state': 'default',
                    'approval_confirm': self._uid,
                    'approval_confirm_date': fields.datetime.now(),
                    'message': "Waiting Approval "+str(rec.approval_ke)
                })

            elif rec.type == 'settle':
                approval = rec.work_location.disbursement_aproval_ids
                if not approval:
                    raise ValidationError(
                        _('You have to configure data approval in the your work location!'))

                approval_list = []
                for approv in approval:
                    vals = {
                        'user_id': approv.user_id.id,
                        'sequence': approv.sequence,
                    }
                    approval_list.append((0, 0, vals))

                rec.invoice_approval_ids = approval_list
                job_position = rec.invoice_approval_ids[0].user_id.employee_id.job_id.name
                type_petty = 'Pengeluaran Petty Cash'
                email_to = rec.invoice_approval_ids[0].user_id.employee_id.work_email

                rec.write({'state': 'confirm'})

            rec._create_email_approval(
                job_position, type_petty, tanggal_pengajuan, doc_number, account, amount, req_by, note, email_to, email_from)

    @api.depends('type', 'state', 'approval_ke')
    def set_approver(self):
        for x in self:
            if x.type == 'aap' and x.state in ['confirm', 'waiting']:
                to_approve = x.bill_approval_ids.filtered(
                    lambda l: not l.is_approved).sorted(key=lambda x: x.sequence)
                if self.env.uid != to_approve[0].user_id.id:
                    x.is_approver = False
                else:
                    x.is_approver = True
            else:
                x.is_approver = False
            #     for y in x.bill_approval_ids:
            #         if self.env.uid == y.user_id.id:
            #             if y.is_approved is False and y.sequence == x.approval_ke:
            #                 x.is_approver = True
            #             else:
            #                 x.is_approver = False
            #         else:
            #             x.is_approver = False
            # else:
            #     x.is_approver = False
    is_approver = fields.Boolean(compute=set_approver)

    @api.depends('type')
    def payment_approve(self):
        for rec in self:
            if rec.type == 'aap':
                to_approve = rec.bill_approval_ids.filtered(
                    lambda l: not l.is_approved).sorted(key=lambda x: x.sequence)
                if self.env.uid != to_approve[0].user_id.id:
                    raise ValidationError(
                        _("You are not approver this document or see the level approval!"))

                to_approve[0].write({
                    'is_approved': True,
                    'approve_date': fields.Date.today(),
                    'approver_id': self.env.uid
                })
                self._check_approver()

            elif rec.type == 'settle':
                to_approve = rec.invoice_approval_ids.filtered(
                    lambda l: not l.is_approved).sorted(key=lambda x: x.sequence)
                if self.env.uid != to_approve[0].user_id.id:
                    raise ValidationError(
                        _("You are not approver this document or see the level approval!"))

                to_approve[0].write({
                    'is_approved': True,
                    'approve_date': fields.Date.today(),
                    'approver_id': self.env.uid
                })
                self._check_approver()

    def _check_approver(self):
        for rec in self:
            job_position = ''
            type_petty = ''
            tanggal_pengajuan = self.date.strftime('%d-%B-%Y')
            doc_number = self.name
            account = str(self.account_id.default_account_id.code) + \
                ' ' + str(self.account_id.default_account_id.name)
            amount = sum(self.payment_line.mapped('amount'))
            req_by = self.user_id.name
            # note = self.description
            email_to = ''
            email_from = self.user_id.company_id.email
            if rec.type == 'aap':
                approve = rec.bill_approval_ids.filtered(
                    lambda l: not l.is_approved).sorted(key=lambda x: x.sequence)
                if not approve:
                    rec._create_vendor_bill()
                    rec.write({'state': 'approve'})
                else:
                    rec.write({
                        'state': 'waiting',
                        'message_state': 'default',
                        'approval_ke_'+str(rec.approval_ke): self._uid,
                        'approval_ke_'+str(rec.approval_ke)+'_date': fields.datetime.now()
                    })
                    rec.approval_ke += 1
                    rec.write({
                        'message': "Waiting Approval "+str(rec.approval_ke)
                    })

                    job_position = approve[0].user_id.employee_id.job_id.name
                    type_petty = 'Pengajuan Petty Cash'
                    email_to = approve[0].user_id.employee_id.work_email
                    rec._create_email_approval(
                        job_position, type_petty, tanggal_pengajuan, doc_number, account, amount, req_by, note, email_to, email_from)

            elif rec.type == 'settle':
                approve = rec.invoice_approval_ids.filtered(
                    lambda l: not l.is_approved).sorted(key=lambda x: x.sequence)
                if not approve:
                    rec.write({'state': 'paid'})
                    rec._create_journal_entry()
                else:
                    rec.write({'state': 'waiting'})
                    job_position = approve[0].user_id.employee_id.job_id.name
                    type_petty = 'Pengeluaran Petty Cash'
                    email_to = approve[0].user_id.employee_id.work_email
                    rec._create_email_approval(
                        job_position, type_petty, tanggal_pengajuan, doc_number, account, amount, req_by, note, email_to, email_from)

    @api.model
    def _create_email_approval(
            self, job_position, type_petty, tanggal_pengajuan, doc_number, account, amount, req_by, note, email_to, email_from):
        template_id = self.env.ref(
            'aa_payment_request.mail_template_email_petty_cash', False)
        render_template = template_id._render({
            'job_position': job_position,
            'type_petty': type_petty,
            'tanggal_pengajuan': tanggal_pengajuan,
            'doc_number': doc_number,
            'account': account,
            'amount': amount,
            'req_by': req_by,
            'note': note,
            'object': self,
        }, engine='ir.qweb')
        mail_body = self.env['mail.render.mixin']._replace_local_links(
            render_template)
        mail_values = {
            'body_html': mail_body,
            'subject': _('Petty Cash'),
            'email_to': email_to,
            'email_from': email_from
        }
        self.env['mail.mail'].sudo().create(mail_values).send()

    @api.model
    def _create_vendor_bill(self):
        # vendor_bill = self.env['voucher.multi.invoice'].search([])
        vals = {
            'account_id': self.account_id.default_account_id.id,
            'date_payment': self.date,
            'amount': self.amount,
            'name': self.name,
            'state': 'draft'
        }
        # vendor_bill.create({
        self.env['voucher.multi.invoice'].create({
            'payment_type': 'Manual',
            'type': 'in_invoice',
            'journal_id': self.journal_id.id,
            'name': self.name,
            'date': self.date,
            'amount': self.amount,
            'payment_request_id': self.id,
            'invoice_ids': [(0, 0, vals)],
            'state': 'draft',
        })
        # vendor_bill.invoice_ids = [(0, 0, vals)]
        # vendor_bill._onchange_invoice_line_ids()

    @api.model
    def _create_journal_entry(self):
        analytic_account_id = False
        if self.analytic_account_id:
            analytic_account_id = self.analytic_account_id.id
        move_data_value = {
            'journal_id': self.account_id.id,
            'date': fields.Date.today(),
            'ref': self.name,
            'company_id': self.env.user.company_id.id,
            'analytic_account_id': analytic_account_id
        }
        move_data = self.env['account.move'].create(move_data_value)

        move_line_vals = []
        move_data_line = {
            'move_id': move_data.id,
            'account_id': self.account_id.default_account_id.id,
            'partner_id': self.user_id.partner_id.id,
            'name': 'Pengeluaran Petty Cash',
            'analytic_tag_ids': False,
            'debit': 0,
            'credit': sum(self.payment_line.mapped('amount'))
        }
        move_line_vals.append(move_data_line)

        for line in self.payment_line:
            analytic_tag_id = False
            if line.analytic_tag_id:
                analytic_tag_id = [line.analytic_tag_id.id]
            move_data_line = {
                'move_id': move_data.id,
                'account_id': line.account_id.id,
                'partner_id': self.user_id.partner_id.id,
                'name': line.name,
                'analytic_tag_ids': analytic_tag_id,
                'debit': line.amount,
                'credit': 0
            }
            move_line_vals.append(move_data_line)

        move_data_line = self.env['account.move.line'].create(move_line_vals)

        move_data.post()
        self.write({'move_id': move_data.id})

    def terbilang_(self, n):
        n = abs(int(n))
        satuan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam",
                  "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]

        if n >= 0 and n <= 11:
            hasil = [satuan[n]]
        elif n >= 12 and n <= 19:
            hasil = self.terbilang_(n % 10) + ["Belas"]
        elif n >= 20 and n <= 99:
            hasil = self.terbilang_(
                n / 10) + ["Puluh"] + self.terbilang_(n % 10)
        elif n >= 100 and n <= 199:
            hasil = ["Seratus"] + self.terbilang_(n - 100)
        elif n >= 200 and n <= 999:
            hasil = self.terbilang_(n / 100) + \
                ["Ratus"] + self.terbilang_(n % 100)
        elif n >= 1000 and n <= 1999:
            hasil = ["seribu"] + self.terbilang_(n - 1000)
        elif n >= 2000 and n <= 999999:
            hasil = self.terbilang_(n / 1000) + \
                ["Ribu"] + self.terbilang_(n % 1000)
        elif n >= 1000000 and n <= 999999999:
            hasil = (
                self.terbilang_(n / 1000000) +
                ["Juta"] + self.terbilang_(n % 1000000)
            )
        elif n >= 1000000000 and n <= 999999999999:
            hasil = (
                self.terbilang_(n / 1000000000)
                + ["Milyar"]
                + self.terbilang_(n % 1000000000)
            )
        else:
            hasil = (
                self.terbilang_(n / 1000000000)
                + ["Triliun"]
                + self.terbilang_(n % 100000000000)
            )
        return hasil

    def terbilang(self, n):
        if n == 0:
            return "nol"
        t = self.terbilang_(n)
        while "" in t:
            t.remove("")
        return " ".join(t)

    # @api.constrains('difference')
    # def _check_amount(self):
    #     for x in self:
    #         if x.type == 'settle':
    #             if x.difference > 0:
    #                 raise ValidationError('Nilai pertanggungjawaban masih belum sesuai.')

    @api.onchange('project_id')
    def _onchange_project_id(self):
        for x in self:
            if x.project_id:
                x.analytic_account_id = x.project_id.analytic_account_id.id

    @api.depends('payment_line')
    def _get_difference(self):
        for payment in self:
            if payment.payment_line:
                payment.difference = payment.pembayaran_id.amount - \
                    sum([x.amount for x in payment.payment_line])

    def create_apr(self):
        for x in self:
            apr = x.with_context(use_apr=True).copy()
            apr.write({
                'payment_line': False,
                'type': 'payment'})
            data = {
                'name': 'Kurang Bayar %s' % (x.name),
                'amount': x.difference * -1
            }
            x.write({'difference_payment_id': apr.id})
            apr.write({'payment_line': [(0, 0, data)],
                      'difference_payment_id': x.id})

        form = self.search([('difference_payment_id', '=', self.id)], limit=1)
        for y in form:
            return {
                'name': ('Approval Payment Request'),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'payment.request',
                'type': 'ir.actions.act_window',
                'res_id': y.id,
            }

    # def unlink(self):
    #     for o in self:
    #         if o.state != 'draft':
    #             raise UserError(("Payment Request tidak bisa dihapus pada state %s !") % (o.state))
    #     return super(PaymentRequest, self).unlink()

    # def name_get(self):
    #     res = []
    #     for field in self:
    #         res.append((field.id, '%s - %s - %s' %
    #                    (field.name, field.description, field.description)))
    #     return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if operator not in ('ilike', 'like', '=', '=like', '=ilike'):
            return super(PaymentRequest, self).name_search(name, args, operator, limit)
        args = args or []
        domain = ['|', '|', ('name', operator, name), ('partner_id.name', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()

    def create_journal(self):
        move_lines = self._prepare_account_move_lines()
        if len(move_lines) > 1:
            move_data = self._prepare_account_move(move_lines)
            move = self.env['account.move'].create(move_data)
            move.post()
            self.move_settlement_id = move.id

    def _prepare_account_move(self, move_lines):
        journal = self.env.user.company_id.journal_settlement_id

        if not journal:
            raise UserError(
                'Journal Settlement di Accounting > Configuration > Settings belum diisi')

        data = {
            'journal_id': journal.id,
            'date': fields.Date.today(),
            'ref': self.name,
            'company_id': self.env.user.company_id.id,
            'line_ids': move_lines,
        }
        return data

    def _prepare_account_move_lines(self):
        data = []
        amount = 0
        for line in self.approved_payment_line:
            if line.account_id:
                data.append((0, 0, {
                            'name': line.name,
                            'partner_id': line.partner_id.id if line.partner_id else False,
                            'account_id': line.account_id.id,
                            'credit': 0,
                            'debit': line.amount,
                            }))
                amount += line.amount
                line.state = 'paid'
                if all([x.state == "paid" for x in line.payment_id.payment_line]):
                    line.payment_id.state = 'paid'
        if data:
            if not self.pembayaran_id:
                raise UserError('Advance Payment tidak boleh kosong!')
            if self.pembayaran_id.state != 'paid':
                raise UserError(
                    'Status Advance Payment %s harus Paid!' % self.pembayaran_id.name)

            credit_account = self.pembayaran_id.payment_line.mapped('statement_line').mapped('move_id').mapped(
                'line_ids').filtered(lambda x: x.account_id.id != x.journal_id.default_account_id.id).mapped('account_id')
            # credit_account = self.env.user.company_id.journal_settlement_id.default_credit_account_id.id

            if credit_account:
                data.append((0, 0, {
                            'name': "Reverse of Cash Advance %s" % self.pembayaran_id.name,
                            'partner_id': False,
                            'account_id': credit_account.id,
                            'credit': amount,
                            'debit': 0,
                            }))
        return data

    def open_journal(self):
        # account_move_ids = []
        # for o in self:
        #     for x in o.account_move_line:
        #         account_move_ids.append(x.id)

        return {
            'name': _('Settlements'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'payment.request',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('type', '=', 'settle')],
        }


class PaymentRequestLine(models.Model):
    _name = 'payment.request.line'

    # payment_request_id = fields.Many2one('payment.request', 'Payment Reference', required=True, ondelete='cascade')
    payment_id = fields.Many2one(
        'payment.request', 'STO Reference', required=True, ondelete='cascade')
    name = fields.Char('Description', required=True)
    coa_id = fields.Many2one(string='CoA', comodel_name='account.account')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')
    invoice_id = fields.Many2one('account.move', 'Vendor Bill', domain=[('move_type', '=', 'in_invoice')])
    amount = fields.Monetary('Amount', required=True,
                             digits=dp.get_precision('Product Price'))
    type = fields.Selection([('payment', 'Payment Request'), ('aap', 'Pengajuan Petty Cash'), (
        'settle', 'Pengeluaran Petty Cash')], string='Type', store=True, related='payment_id.type')
    currency_id = fields.Many2one(related='payment_id.currency_id', depends=[
                                  'payment_id'], store=True, string='Currency')
    account_id = fields.Many2one(comodel_name='account.account', string='Account', domain=[
                                 ('user_type_id.type', '!=', 'view')])
    state = fields.Selection([('open', 'Open'), ('paid', 'Paid')],
                             string='Status', readonly=True, default='open')
    kwitansi = fields.Char(string='Kwitansi')
    date = fields.Date(string="Date")
    statement_line = fields.One2many(
        'account.bank.statement.line', 'pembayaran_line_id', string="Statement Line")
    move_ids = fields.Many2many(
        'account.move', compute='_compute_move_id', string='Statement Ref.', store=True)
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Project', related="payment_id.analytic_account_id")
    analytic_tag_id = fields.Many2one(
        'account.analytic.tag', 'Analytic Tags')

    @api.depends('statement_line', 'statement_line.move_id.state')
    def _compute_move_id(self):
        for o in self:
            o.move_ids = o.statement_line.mapped(
                'move_id').filtered(lambda x: x.state == 'posted')

    @api.onchange('invoice_id')
    def onchange_invocie_id(self):
        if self.invoice_id:
            self.amount = self.invoice_id.amount_total
            self.partner_id = self.invoice_id.partner_id.id
            self.account_id = self.invoice_id.partner_id.property_account_payable_id.id
            self.name = 'Pembayaran Vendor Bill'

    def name_get(self):
        res = []
        for field in self:
            res.append((field.id, '%s - %s - %s' %
                       (field.payment_id.name, field.name,  field.amount)))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if operator not in ('ilike', 'like', '=', '=like', '=ilike'):
            return super(PaymentRequestLine, self).name_search(name, args, operator, limit)
        args = args or []
        domain = ['|', ('payment_id.name', operator, name),
                  ('name', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()


class AccountMove(models.Model):
    _inherit = 'account.move'

    pembayaran_id = fields.Many2one(
        'payment.request', 'Payment Request', readonly=True, copy=False)
    # payment_request_id = fields.Many2one('payment.request', 'Payment Request', readonly=True, copy=False)

    def name_get(self):
        res = super(AccountMove, self).name_get()
        new_res = []
        for x in res:
            for inv in self:
                if inv.id == x[0]:
                    amount = "Rp.{:0,.2f}".format(inv.amount_total)
                    if inv.partner_id.name:
                        additional = '%s [%s] %s' % (
                            x[1], inv.partner_id.name, amount)
                    else:
                        additional = '%s %s' % (x[1], amount)
                    new_res.append((inv.id, additional))
        return new_res


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    payment_id = fields.Many2one(comodel_name='payment.request',
                                 string='Payment Request')
    subtotal_amount = fields.Monetary(
        compute='_compute_subtotal_amount', string='Amount', store=True)

    @api.depends('previous_statement_id', 'previous_statement_id.balance_end_real')
    def _compute_ending_balance(self):
        for rec in self:
            rec.onchange_balance_end()

    def button_reopen(self):
        for x in self:
            for bsl in x.line_ids:
                if bsl.pembayaran_line_id:
                    bsl.pembayaran_line_id.write({'state': 'open'})
                    bsl.pembayaran_line_id.payment_id.write(
                        {'state': 'approve'})
        res = super(AccountBankStatement, self).button_reopen()
        return res

    @api.depends('line_ids')
    def _compute_subtotal_amount(self):
        for o in self:
            total = 0
            if o.line_ids:
                total = sum(o.line_ids.mapped('amount'))
                o.subtotal_amount = total
            else:
                o.subtotal_amount = total

    @api.onchange('payment_id')
    def onchange_payment(self):
        if self.payment_id:
            payment_id = self.payment_id
            n = -1
            if payment_id.type == 'settle':
                n = 1
            data_list = [(0, 0, {
                'date': payment_id.date,
                'payment_ref': x.name,
                'ref': x.invoice_id.name or False,
                'amount': (x.amount - sum([abs(l.amount) for l in x.statement_line if l.move_id])) * n,
                'partner_id': payment_id.partner_id.id or False if payment_id.type != 'aap' else x.payment_id.partner_id.id or False,
                'pembayaran_line_id': x.id,
                'analytic_account_id':payment_id.analytic_account_id.id or False,
                # 'invoices_id': x.invoice_id.id,
            }) for x in payment_id.payment_line if not x.account_id]

            return {
                'value': {
                    'line_ids': data_list
                }
            }

    @api.onchange('balance_end')
    def onchange_balance_end(self):
        if self.balance_end:
            return {'value': {'balance_end_real': self.balance_end}}

    def check_confirm_bank(self):
        for l in self.line_ids:
            if l.pembayaran_line_id.invoice_id:
                l.pembayaran_line_id.invoice_id.pembayaran_id = l.pembayaran_line_id.payment_id.id

        res = super(AccountBankStatement, self).check_confirm_bank()
        return res


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    pembayaran_line_id = fields.Many2one(
        'payment.request.line', 'Payment Request')
    kwitansi = fields.Char(string='Kwitansi')
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account')

    @api.onchange('pembayaran_line_id')
    def onchange_pembayaran_line_id(self):
        payment_id = self.pembayaran_line_id
        if payment_id:
            n = -1
            if payment_id.type == 'settle':
                n = 1

            amount_paid = sum([abs(x.amount)
                              for x in payment_id.statement_line if x.move_id])

            return {
                'value': {
                    'date': payment_id.payment_id.date,
                    'name': payment_id.name,
                    'ref': payment_id.invoice_id.name or False,
                    'kwitansi': payment_id.kwitansi,
                    'analytic_account_id': payment_id.analytic_account_id.id or False,
                    'amount': (payment_id.amount - amount_paid) * n,
                    'partner_id': payment_id.invoice_id.partner_id.id or False,
                    'invoices_id': payment_id.invoice_id.id,
                }
            }

    def button_cancel_reconciliation(self):
        res = super(AccountBankStatementLine,
                    self).button_cancel_reconciliation()
        if self.pembayaran_line_id:
            self.pembayaran_line_id.state = 'open'
            self.pembayaran_line_id.payment_id.state = 'approve'
        return res

    def process_reconciliation(self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None):
        res = super(AccountBankStatementLine, self).process_reconciliation(
            counterpart_aml_dicts, payment_aml_rec, new_aml_dicts)

        for sm_line in self:
            if sm_line.move_id:
                for x in sm_line.move_id.line_ids:
                    x.sudo().write(
                        {'analytic_account_id': sm_line.analytic_account_id.id})

        payment_line = self.pembayaran_line_id
        if self.pembayaran_line_id:
            amount_paid = sum([abs(x.amount)
                              for x in payment_line.statement_line if x.move_id])
            payment_line.state = 'paid'
            if all([line.state == "paid" for line in payment_line.payment_id.payment_line]):
                payment_line.payment_id.state = 'paid'
        return res


class BillApproval(models.Model):
    _name = "bill.approval"
    _order = 'sequence asc'

    payment_request_id = fields.Many2one(
        'payment.request', string='Payment Request', ondelete="cascade")
    user_id = fields.Many2one('res.users', string='Approver')
    is_approved = fields.Boolean(string='Is Approved')
    approve_date = fields.Date(string='Date Approved')
    approver_id = fields.Many2one('res.users', string='Approved By')
    sequence = fields.Integer(string='Level')


class InvoiceApproval(models.Model):
    _name = "invoice.approval"
    _order = 'sequence asc'

    payment_request_id = fields.Many2one(
        'payment.request', string='Payment Request', ondelete="cascade")
    user_id = fields.Many2one('res.users', string='Approver')
    is_approved = fields.Boolean(string='Is Approved')
    approve_date = fields.Date(string='Date Approved')
    approver_id = fields.Many2one('res.users', string='Approved By')
    sequence = fields.Integer(string='Level')


class VoucherMultiInvoice(models.Model):
    _inherit = 'voucher.multi.invoice'

    payment_request_id = fields.Many2one(
        'payment.request', string='Payment Request')
