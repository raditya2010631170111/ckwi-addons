# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from collections import defaultdict



class AccountMove(models.Model):
    _inherit = 'account.move'

    grading_summary_id = fields.Many2one('grading.summary', store=False, readonly=True,
        states={'draft': [('readonly', False)]},
        string='Grading Summary',
        help="Auto-complete from a past Grading Summary.")
    
    # no_do = fields.Char('NO Delivery', compute='_compute_no_do', store=True)
    stock_picking_id = fields.Many2one('stock.picking', string='stock_picking', store=True)
    certification_id = fields.Many2one('res.certification', string='Sertifikasi', compute='_compute_certification_id')

    def _compute_certification_id(self):
        for move in self:
            sale_order = self.env['sale.order'].search([('name', '=', move.origin)], limit=1)
            move.certification_id = sale_order.certification_id


    # @api.depends('origin')
    # def _compute_no_do(self):
    #     for move in self:
    #         picking = self.env['stock.picking'].search([('origin', '=', move.origin)], limit=1)
    #         if picking:
    #             move.no_do = picking.name
    #         else:
    #             move.no_do = False

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



class AccountMoveLine(models.Model):
    """ Override AccountInvoice_line to add the link to the Grading Summary line it is related to"""
    _inherit = 'account.move.line'

    grading_summary_line_id = fields.Many2one('grading.summary.line', 'Grading Summary Line', ondelete='set null', index=True)
    grading_summary_id = fields.Many2one('grading.summary', 'Grading Summary', related='grading_summary_line_id.grading_summary_id', readonly=True)
    master_hasil = fields.Selection(related='grading_summary_line_id.master_hasil', required=True)
    no_po_cust = fields.Char(related='sale_line_ids.no_po_cust', string='Cust Ref', store=True)
    # nopo = fields.Char('nopo', store=True,) #compute='_compute_no_po'

    
    # @api.depends('move_id.origin')
    # def _compute_no_po(self):
    #     for line in self:
    #         if line.move_id.origin:
    #             sale_order_line = self.env['sale.order.line'].search([('nopo', '=', line.move_id.origin)], limit=1)
    #             if sale_order_line:
    #                 line.no_po_cust = sale_order_line.no_po_cust
    #         else:
    #             line.no_po_cust = False

    # @api.depends('move_id.origin')
    # def _compute_no_po(self):
    #     sale_order_lines = self.env['sale.order.line'].search([])
    #     sale_order_lines_by_nopo = {}

    #     for line in sale_order_lines:
    #         if line.nopo and line.no_po_cust:
    #             sale_order_lines_by_nopo.setdefault(line.nopo, []).append(line.no_po_cust)

    #     for line in self:
    #         if line.move_id.origin:
    #             line.nopo = line.move_id.origin
    #             line.no_po_cust = sale_order_lines_by_nopo.get(line.move_id.origin, [False])[0]
    #         else:
    #             line.nopo = False
    #             line.no_po_cust = False
 

    # TODO check me, unused?
    def _copy_data_extend_business_fields(self, values):
        # OVERRIDE to copy the 'grading_summary_line_id' field as well.origin
        res = super(AccountMoveLine, self)._copy_data_extend_business_fields(values)
        values['grading_summary_line_id'] = self.grading_summary_line_id.id
        return res