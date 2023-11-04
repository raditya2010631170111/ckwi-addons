from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare

TYPE_SELECTION = [
    ('out_invoice','Penerimaan'),
    ('in_invoice','Pengeluaran'),
    ('out_refund','Kontra Bon - Customer'),
    ('in_refund','Kontra Bon - Vendor'),
]

class PaymentRegisterCustom(models.TransientModel):
    _name = 'payment.register.custom'
    _description = 'Register Payment Custom'

    payment_date = fields.Date(string="Payment Date", required=True,
        default=fields.Date.context_today)
    amount = fields.Monetary(currency_field='currency_id', store=True, readonly=False,
        )
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        compute='_compute_currency_id',
        help="The payment's currency.")
    journal_id = fields.Many2one('account.journal', store=True, readonly=False,
        domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method',
        readonly=False, store=True)
    company_id = fields.Many2one('res.company', store=True, copy=False,
        compute='_compute_from_lines',  default=lambda s: s.env.company)
    multi_inv_id = fields.Many2one(
        'voucher.multi.invoice',
        string='Voucher Multi Invoice',ondelete="cascade"
    )
    amt_curr_outstanding = fields.Monetary('Current Outstanding')
    payment_difference = fields.Monetary('Payment Difference',compute="_compute_payment_difference")
    payment_difference_handling = fields.Selection(string='Payment Difference Handling', selection=[('open', 'Keep open'), ('reconcile', 'Mark as fully paid'),],default="open")
    writeoff_account_id = fields.Many2one(comodel_name='account.account', string='Post Difference In',domain="[('deprecated','=',False),('company_id','=',company_id)]")
    writeoff_label = fields.Char(string='Label',default="Write-Off")
    type = fields.Selection(
        TYPE_SELECTION, "Tipe", default='out_invoice',)
    payment_type = fields.Selection([
        ('Manual', "Manual"), ('Invoice', "Invoice/Bill"),
        ('Check', "Check/Bank")],
        default='Manual',)
    
    

    @api.depends('amt_curr_outstanding','amount')
    def _compute_payment_difference(self):
        for i in self:
            i.payment_difference = i.amt_curr_outstanding - i.amount

    @api.depends('journal_id')
    def _compute_currency_id(self):
        for wizard in self:
            wizard.currency_id = wizard.journal_id.currency_id or wizard.company_id.currency_id

    def pay(self):
        for rec in self:
            inv = self.env['voucher.multi.invoice'].with_context(active_id=False).search([('id', '=', self.env.context.get('active_id'))])
            inv.write({'state':'done', 'register_payment_id': self.journal_id.id})
            # amount_total_signed = sum(self.env['account.move'].search([('multi_inv_id','=', inv.id)]).mapped('amount_total_signed'))
            for invoice in inv:
                invoice.ensure_one()
                invoice._check_total()
                amount = 0
            if inv.payment_type != 'Invoice':
                print("================================Ini manual", )
                line_ids = []
                amount=rec.amount
                if inv.type == 'in_invoice':
                    for line in inv.line_ids:
                        vals2 = {
                        'partner_id': inv.partner_id.id,
                        'name': "Vendor Payment Rp {} - {}".format(str(line.amount), inv.partner_id.name),
                        'account_id': line.account_id.id,
                        'currency_id': inv.currency_id.id,
                        'analytic_account_id':inv.analytic_account_id.id,
                        'debit':line.amount,
                        'credit':0,
                        'amount_currency':  line.amount - 0}
                        line_ids.append((0,0,vals2))

                    vals1 = {
                        'partner_id': inv.partner_id.id,
                        'name': "Vendor Payment Rp {} - {}".format(str(amount), inv.partner_id.name),
                        'account_id': rec.journal_id.payment_credit_account_id.id,
                        'currency_id': inv.currency_id.id,
                        'analytic_account_id':inv.analytic_account_id.id,
                        'debit':0,
                        'credit':amount,
                        'amount_currency' :0 - amount}
                    line_ids.append((0,0,vals1))

                elif inv.type == 'out_invoice':
                    for line in inv.line_ids:
                        vals2 = {
                        'partner_id': inv.partner_id.id,
                        'name': "Vendor Payment Rp {} - {}".format(str(line.amount), inv.partner_id.name),
                        'account_id': line.account_id.id,
                        'currency_id': inv.currency_id.id,
                        'analytic_account_id':inv.analytic_account_id.id,
                        'credit':line.amount,
                        'debit':0,
                        'amount_currency': 0 - line.amount}
                        line_ids.append((0,0,vals2))

                    vals1 = {
                        'partner_id': inv.partner_id.id,
                        'name': "Vendor Payment Rp {} - {}".format(str(amount), inv.partner_id.name),
                        'account_id': rec.journal_id.payment_debit_account_id.id,
                        'currency_id': inv.currency_id.id,
                        'analytic_account_id':inv.analytic_account_id.id,
                        'credit':0,
                        'debit':amount,
                        'amount_currency' :amount}
                    line_ids.append((0,0,vals1))
                    

                data = {
                    'multi_inv_id' : inv.id,
                    'name' : '{}/{}'.format(inv.name,self.env['ir.sequence'].next_by_code('account.voucher.journal')),
                    # 'ref': line.invoice_id.name,
                    'partner_id': inv.partner_id.id,
                    'move_type' : 'entry',
                    'date': inv.date,
                    'journal_id' : inv.journal_id.id,
                    'line_ids': line_ids,
                    }
                
                prec = self.env['decimal.precision'].precision_get('Account')
                new_move = self.env['account.move'].create(data)
                new_move.sudo()._post()
            
            else: 
                if inv.type == 'in_invoice':
                    amount = rec.amount
                    vals1 = {
                        'partner_id': inv.partner_id.id,
                        'name': "Vendor Payment Rp {} - {}".format(str(amount), inv.partner_id.name),
                        'account_id': rec.journal_id.payment_credit_account_id.id,
                        'currency_id': inv.currency_id.id,
                        'analytic_account_id':inv.analytic_account_id.id,
                        'debit':0,
                        'credit':amount,
                        'amount_currency' :0 - amount}
                    vals2 = {
                        'partner_id': inv.partner_id.id,
                        'name': "Vendor Payment Rp {} - {}".format(str(amount), inv.partner_id.name),
                        'account_id': inv.invoice_ids and inv.invoice_ids[0].account_id.id or False,
                        'currency_id': inv.currency_id.id,
                        'analytic_account_id':inv.analytic_account_id.id,
                        'debit':amount+rec.payment_difference,
                        'credit':0,
                        'amount_currency':  amount+rec.payment_difference - 0}

                    data = {
                        'multi_inv_id' : inv.id,
                        'name' : '{}/{}'.format(inv.name,self.env['ir.sequence'].next_by_code('account.voucher.journal')),
                        'ref': inv.name,
                        'partner_id': inv.partner_id.id,
                        'move_type' : 'entry',
                        'date': inv.date,
                        'journal_id' : inv.journal_id.id,
                        'line_ids': [(0, 0,  vals2), (0, 0, vals1)],
                        }

                    if rec.payment_difference:
                        if rec.payment_difference_handling == 'reconcile':                    
                            vals3 = {
                                'partner_id': inv.partner_id.id,
                                'name': rec.writeoff_label,
                                'account_id': rec.writeoff_account_id.id,
                                'currency_id': inv.currency_id.id,
                                'analytic_account_id':inv.analytic_account_id.id,
                                }   
                            if rec.payment_difference <0:
                                vals3['credit'] = 0
                                vals3['debit'] = abs(rec.payment_difference)
                                vals3['amount_currency'] = abs(rec.payment_difference)
                            else:
                                vals3['credit'] = abs(rec.payment_difference)
                                vals3['debit'] = 0
                                vals3['amount_currency'] = abs(rec.payment_difference)
                            data['line_ids'] += [(0,0,vals3)] 
                            inv.write({'mark_as_fully_paid':True})
                            inv.write({'reconcile_account_id':rec.writeoff_account_id.id})
                            inv.write({'reconcile_amount': rec.payment_difference})
                            inv.write({'reconcile_writeoff_label': rec.writeoff_label})
                        else:
                            vals1['credit'] = amount
                            vals1['debit'] = 0
                            vals1['amount_currency'] = 0 - amount
                            vals2['credit'] = 0
                            vals2['debit'] = amount
                            vals2['amount_currency'] = amount
                            data['line_ids'] = [(5,0,0), (0, 0,  vals2), (0, 0, vals1)]

                    prec = self.env['decimal.precision'].precision_get('Account')
                    new_move = self.env['account.move'].create(data)
                    new_move.sudo()._post()
                    for line in inv.invoice_ids:                
                        payment_move_line_id = False
                        for pl in new_move.line_ids:
                            if not payment_move_line_id:
                                if pl.account_id.user_type_id.type in ('receivable', 'payable') and not pl.reconciled:
                                    payment_move_line_id = pl


                        payment_move_line_id = payment_move_line_id and payment_move_line_id[0].id or False
                        if payment_move_line_id and line.invoice_id.amount_residual > 0 and (rec.payment_difference <= 0 or rec.payment_difference > 0 and rec.payment_difference_handling == 'reconcile'):
                            line.invoice_id.js_assign_outstanding_line(
                                line_id=payment_move_line_id)

                if inv.type == 'out_invoice':
                        # print("================================================================", line.invoice_id.name)
                    amount = rec.amount
                    vals1 = {
                        'partner_id': inv.partner_id.id,
                        'name': "Vendor Payment Rp {} - {}".format(str(amount), inv.partner_id.name),
                        'account_id': rec.journal_id.payment_debit_account_id.id,
                        'currency_id': inv.currency_id.id,
                        'analytic_account_id':inv.analytic_account_id.id,
                        'debit':amount,
                        'credit':0,
                        'amount_currency': amount - 0}
                    vals2 = {
                        'partner_id': inv.partner_id.id,
                        'name': "Vendor Payment Rp {} - {}".format(str(amount), inv.partner_id.name),
                        'account_id': inv.invoice_ids and inv.invoice_ids[0].account_id.id or False,
                        'currency_id': inv.currency_id.id,
                        'analytic_account_id':inv.analytic_account_id.id,
                        'debit':0,
                        'credit':amount+rec.payment_difference,
                        'amount_currency': 0 - (amount-rec.payment_difference)}
                                        
                    prec = self.env['decimal.precision'].precision_get('Account')

                    # Ini jika nyicil
                    data = {
                            'multi_inv_id' : inv.id,
                            'name' : '{}/{}'.format(inv.name,self.env['ir.sequence'].next_by_code('account.voucher.journal')),
                            'ref': inv.name,
                            'partner_id': inv.partner_id.id,
                            'move_type' : 'entry',
                            'date': inv.date,
                            'journal_id' : rec.journal_id.id,
                            'line_ids': [(0, 0,  vals2), (0, 0, vals1)],
                        }
                    if rec.payment_difference:
                        if rec.payment_difference_handling == 'reconcile':                    
                            vals3 = {
                                'partner_id': inv.partner_id.id,
                                'name': rec.writeoff_label,
                                'account_id': rec.writeoff_account_id.id,
                                'currency_id': inv.currency_id.id,
                                'analytic_account_id':inv.analytic_account_id.id,
                                }   
                            if rec.payment_difference <0:
                                vals3['debit'] = 0
                                vals3['credit'] = abs(rec.payment_difference)
                                vals3['amount_currency'] = 0 - abs(rec.payment_difference)
                            else:
                                vals3['debit'] = abs(rec.payment_difference)
                                vals3['credit'] = 0
                                vals3['amount_currency'] = abs(rec.payment_difference)
                            data['line_ids'] += [(0,0,vals3)]
                            inv.write({'mark_as_fully_paid':True})
                            inv.write({'reconcile_account_id':rec.writeoff_account_id.id})
                            inv.write({'reconcile_amount': rec.payment_difference})
                            inv.write({'reconcile_writeoff_label': rec.writeoff_label})
                        else:
                            vals1['debit'] = amount
                            vals1['credit'] = 0
                            vals1['amount_currency'] = amount
                            vals2['debit'] = 0
                            vals2['credit'] = amount
                            vals2['amount_currency'] = 0 - amount
                            data['line_ids'] = [(5,0,0), (0, 0,  vals2), (0, 0, vals1)]

                    new_move = self.env['account.move'].create(data)
                    new_move.sudo()._post()
                    for line in inv.invoice_ids:                
                        payment_move_line_id = False
                        for pl in new_move.line_ids:
                            if not payment_move_line_id:
                                if pl.account_id.user_type_id.type in ('receivable', 'payable') and not pl.reconciled:
                                    payment_move_line_id = pl


                        payment_move_line_id = payment_move_line_id and payment_move_line_id[0].id or False
                        # menghapus kondisi (rec.payment_difference <= 0 or rec.payment_difference > 0 and rec.payment_difference_handling == 'reconcile') karena pengen auto reconsile walaupun register payment nya kurang dan keep open
                        if payment_move_line_id and line.invoice_id.amount_residual > 0:
                            line.invoice_id.js_assign_outstanding_line(
                                line_id=payment_move_line_id)

