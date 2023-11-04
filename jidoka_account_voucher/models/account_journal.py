# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'


    invoice_sequence_id = fields.Many2one('ir.sequence', string='Invoice Sequence Format')
    bill_sequence_id = fields.Many2one('ir.sequence', string='Bill Sequence Format')


    def create_voucher_sequence(self):
        for journal in self:
            obj_ir_sequence = self.env['ir.sequence']
            sequence_invoice = obj_ir_sequence.create({
                'name' : "Voucher Invoice " + journal.name,
                'code' : "voucher.invoice" + str(journal.name).lower(),
                'prefix' : "BKM/%(year)s/%(month)s/" + str(journal.code) + "/",
                'padding' : 5,
                'company_id' :False
            })
            journal.write({'invoice_sequence_id':sequence_invoice})

            sequence_bill = obj_ir_sequence.create({
                'name' : "Voucher Bill " + journal.name,
                'code' : "voucher.bill" + str(journal.name).lower(),
                'prefix' : "BKK%(year)s%(month)s" + str(journal.code),
                'padding' : 5,
                'company_id' :False
            })
            journal.write({'bill_sequence_id':sequence_bill})