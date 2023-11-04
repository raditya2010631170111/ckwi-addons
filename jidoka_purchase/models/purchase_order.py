# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import  UserError
from dateutil.relativedelta import relativedelta


import logging
_logger = logging.getLogger(__name__)



import datetime

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    #data ttd
    n_manager = fields.Char(string='Nama Direktur/Manager')
    n_supervisor = fields.Char(string='Nama Supervisor/Kabag')
    n_pembuat = fields.Char(string='Nama Pembuat')
    ttd_manager = fields.Binary('TTD Direktur/Manager')
    ttd_supervisor = fields.Binary('TTD Supervisor/Kabag')
    ttd_pembuat= fields.Binary('TTD Pembuat')
    ttd_penjual = fields.Binary('TTD Penjual')

    # Ubah State Draft PO
    state = fields.Selection([
        ('draft', 'Draft PO'),
        ('sent', 'PO Sent'),
        ('to approve', 'To Approve'),
        ('approved_kabag', 'Approved Kabag'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    phone = fields.Char('Phone/Fax',related='partner_id.phone')
    berlaku_hingga = fields.Datetime('berlaku_hingga')
    sy_penyerahan = fields.Selection([
        ('cf', 'C&F'),
        ('lainnya', 'Lainnya')
    ], string='Sy. Penyerahan')
    po_reff = fields.Char('po_reff')
    valid_date = fields.Date('Valid Date')
    pr_date = fields.Date('Request Date')
    shipment = fields.Selection([
        ('penuh', 'Harus Penuh'),
        ('partial', 'Partial'),
        ('lainnya', 'Lainnya'),
    ], string='Pengiriman')
    mo_id = fields.Many2one('mrp.production', string='Kode MO')
    product_mo_id = fields.Many2one('product.product', string='Item')
    information = fields.Html('Information', default="""<p>(&nbsp; &nbsp; &nbsp; ) Kwalitas :&nbsp;</p><p>
        ( &nbsp;&nbsp;&nbsp;&nbsp;    )	Kadar Air (MC) :&nbsp;</p><p>(&nbsp; &nbsp; &nbsp; ) Pengiriman harus complete set baru dapat diproses pembayarannya </p><p>
        (&nbsp; &nbsp; &nbsp; )	Tagihan dibuat dalam invoice untuk satu kode produksi / #PO	</p><p>
        (&nbsp; &nbsp; &nbsp; )	Apabila PO ini sudah diterima &amp; ditanda tangani segera fax kembali.	</p><p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*&nbsp;&nbsp;&nbsp;&nbsp;No. PO dan tanggal berlaku harus dicantumkan dalam surat jalan.&nbsp;</p><p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*&nbsp; &nbsp; Uraian surat jalan harus sama dengan uraian P.O&nbsp;</p><p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*&nbsp; &nbsp; Pembayaran dengan mata uang asing menggunakan kurs negosiasi</p> &nbsp; &nbsp;&nbsp; &nbsp;<br> bank UOB Indonesia.</br>""")
    # information_default = fields.Text('Information',default="""* Surat Jalan harus dicantumkan Nomer PO, INVOICE harus dicantumkan Nomer PO dan No. Rekening Bank
    # * Uraian surat jalan harus sama dengan uraian PO, PO yang masa berlakunya habis dinyatakan tidak berlaku lagi
    # * Penagihan dapat diterima jika jumlah barang yang dikirim sudah penuh [ ] / belum penuh [ ]
    # * Pengiriman dilebihi 1% dari quantity PO (Gratis !!!)
    # * Tagihan lampirkan Faktur Pajak""")
    information_default = fields.Text('Information',default="""
    * No. PO dan tanggal berlaku harus dicantumkan dalam surat jalan dan invoice
    * Uraian surat jalan harus sama dengan uraian PO, PO yang masa berlakunya habis dinyatakan tidak berlaku lagi
    * Penagihan dapat diterima jika jumlah barang yang dikirim sudah penuh [ ] / belum penuh [ ]
    * Tagihan lampirkan Faktur Pajak""")

    warehouse_id = fields.Many2one('stock.warehouse', string='Digunakan Untuk')
    # state = fields.Selection(selection_add=[
    #     ('to approve', 'To Approve'),
    #     ('approved_kabag', 'Approved Kabag'),
    #     ('purchase', 'Purchase Order'),
    #     ('done', 'Locked'),
    #     ('cancel', 'Cancelled')
    # ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
    fee_location_id = fields.Many2one('res.location', string='Delivery Loc.')
    wood_grade_id = fields.Many2one('wood.grade', string='Grade')
    is_continuation = fields.Boolean('Is a Continuation?')
    susulan = fields.Char('susulan', compute='_compute_susulan')
    is_contract = fields.Boolean('Is a Contract?')
    contract_number = fields.Char('Contract Number')
    amount_fee = fields.Float('Amount Fee',store=True, readonly=True, compute='_amount_all')
    certification_id = fields.Many2one('res.certification', string='Sertifikasi')
    

    rekapitulasi_grading_count = fields.Integer(compute="_compute_rekapitulasi_grading_count", string='Summary Count', copy=False, default=0, store=True)
    rekapitulasi_grading_ids = fields.One2many('rekapitulasi.grading', 'purchase_id', string='Grading Summary')
    
    
    invoice_grading_ids = fields.Many2many('account.move', relation= 'invoice_grading_rel',
                                        #    compute="_compute_invoice_grading", 
                                           string='Bills', copy=False, store=True)
    
    invoice_grading_count = fields.Integer(
        # compute="_compute_invoice_grading",
                                           string='Bill Count', copy=False, default=0, store=True)
    
    # is_kayu = fields.Boolean('Is Kayu', default= False,readonly=True)
    
    # is_kayu = fields.Boolean('Is Kayu', 
        # compute='_compute_is_kayu', default= False,readonly=True, store=True)
        
    is_kayu = fields.Boolean('Is Kayu', default= False,readonly=True, store=True, related='order_type.is_kayu')
    is_qc_id = fields.Boolean('Is QC', default= False,readonly=True, store=True, related='order_type.is_qc_id')
    pembayaran_id = fields.Many2one(
        'account.payment.term',
        string='Pembayaran',
        )

    @api.depends('is_continuation')
    def _compute_susulan(self):
        for record in self:
            if record.is_continuation:
                record.susulan = 'SUSULAN'
            else:
                record.susulan = ''
    
    # @api.depends('order_type')
    # def _compute_is_kayu(self):
    #     for r in self:
    #         if r.order_type.is_kayu == True:
    #             r.is_kayu = True
    #         else:
    #             r.is_kayu = False   
                
    
    # DISPLAY VENDOR BILL INTO PO
    # @api.depends('order_line.move_ids.picking_id.grading_summary_ids.invoice_ids')
    # def _compute_invoice(self):
    #     for order in self:
    #         # invoices = order.mapped('order_line.invoice_lines.move_id')
    #         invoices = order.order_line.mapped('move_ids.picking_id.grading_summary_ids.invoice_ids')
    #         order.invoice_ids = invoices
    #         order.invoice_count = len(invoices)
            
            
    # @api.depends('picking_ids')
    # def _compute_invoice_grading(self):
    #     for order in self:
    #         # invoices = order.mapped('order_line.invoice_lines.move_id')
    #         invoices = order.picking_ids.mapped('grading_summary_ids.invoice_ids')
    #         order.invoice_ids = invoices
    #         order.invoice_count = len(invoices)
    
    def action_view_invoice_grading(self, invoices=False):
        """This function returns an action that display existing vendor bills of
        given purchase order ids. When only one found, show the vendor bill
        immediately.
        """
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the purchase order, we read them in sudo to fill the
            # cache.
            self.sudo()._read(['invoice_grading_ids'])
            invoices = self.invoice_grading_ids

        result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        # choose the view_mode accordingly
        if len(invoices) > 1:
            result['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = invoices.id
        else:
            result = {'type': 'ir.actions.act_window_close'}

        return result
        # return 


    @api.depends('rekapitulasi_grading_ids')
    def _compute_rekapitulasi_grading_count(self):
        for order in self:
            order.rekapitulasi_grading_count = len(order.rekapitulasi_grading_ids)

    def _prepare_rekapitulasi_grading(self):
        lines = []
        good_pcs = afkir_pcs = triming_pcs = grade_a_pcs = grade_b_pcs = 0
        good_cubic = afkir_cubic = triming_cubic = grade_a_cubic = grade_b_cubic = 0
        for move in self.order_line:
            good_pcs = afkir_pcs = triming_pcs = grade_a_pcs = grade_b_pcs = 0
            good_cubic = afkir_cubic = triming_cubic = grade_a_cubic = grade_b_cubic = 0
            for move_line in move.mapped('move_ids').mapped('move_line_nosuggest_ids'):
                if move_line.master_hasil == 'bagus':
                    good_cubic = good_cubic + move_line.qty_done
                    good_pcs = good_pcs + 1
                if move_line.master_hasil == 'afkir':
                    afkir_cubic = afkir_cubic + move_line.qty_done
                    afkir_pcs = afkir_pcs + 1
                if move_line.master_hasil == 'triming':
                    triming_cubic = triming_cubic + move_line.qty_done
                    triming_pcs = triming_pcs + 1
                if move_line.master_hasil == 'grade_a':
                    grade_a_cubic = grade_a_cubic + move_line.qty_done
                    grade_a_pcs = grade_a_pcs + 1
                if move_line.master_hasil == 'grade_b':
                    grade_b_cubic = grade_b_cubic + move_line.qty_done
                    grade_b_pcs = grade_b_pcs + 1
            lines.append([0,0,{
                'product_id':move.product_id.id,
                'good_pcs':good_pcs,
                'good_cubic':good_cubic,
                'afkir_pcs':afkir_pcs,
                'afkir_cubic':afkir_cubic,
                'triming_pcs':triming_pcs,
                'triming_cubic':triming_cubic,
                'grade_a_pcs':grade_a_pcs,
                'grade_a_cubic':grade_a_cubic,
                'grade_b_pcs':grade_b_pcs,
                'grade_b_cubic':grade_b_cubic
            }])
        return{
            'name':'New',
            'partner_id':self.partner_id.id,
            'purchase_id':self.id,
            # 'arrival_date':self.date_done,
            # 'nota':self.nota,
            # 'plat_no':self.plat_no,
            'line_ids':lines,
        }
        
    # TIDAK DIPAKAI
    # def _upt_prepare_rekapitulasi_grading(self):
    #     lines = []
    #     good_pcs = afkir_pcs = triming_pcs = grade_a_pcs = grade_b_pcs = 0
    #     good_cubic = afkir_cubic = triming_cubic = grade_a_cubic = grade_b_cubic = 0
    #     for move in self.order_line:
    #         good_pcs = afkir_pcs = triming_pcs = grade_a_pcs = grade_b_pcs = 0
    #         good_cubic = afkir_cubic = triming_cubic = grade_a_cubic = grade_b_cubic = 0
    #         for move_line in move.mapped('move_ids').mapped('move_line_nosuggest_ids'):
    #             if move_line.master_hasil == 'bagus':
    #                 good_cubic = good_cubic + move_line.qty_done
    #                 good_pcs = good_pcs + 1
    #             if move_line.master_hasil == 'afkir':
    #                 afkir_cubic = afkir_cubic + move_line.qty_done
    #                 afkir_pcs = afkir_pcs + 1
    #             if move_line.master_hasil == 'triming':
    #                 triming_cubic = triming_cubic + move_line.qty_done
    #                 triming_pcs = triming_pcs + 1
    #             if move_line.master_hasil == 'grade_a':
    #                 grade_a_cubic = grade_a_cubic + move_line.qty_done
    #                 grade_a_pcs = grade_a_pcs + 1
    #             if move_line.master_hasil == 'grade_b':
    #                 grade_b_cubic = grade_b_cubic + move_line.qty_done
    #                 grade_b_pcs = grade_b_pcs + 1
    #         lines.append([0,0,{
    #             'product_id':move.product_id.id,
    #             'good_pcs':good_pcs,
    #             'good_cubic':good_cubic,
    #             'afkir_pcs':afkir_pcs,
    #             'afkir_cubic':afkir_cubic,
    #             'triming_pcs':triming_pcs,
    #             'triming_cubic':triming_cubic,
    #             'grade_a_pcs':grade_a_pcs,
    #             'grade_a_cubic':grade_a_cubic,
    #             'grade_b_pcs':grade_b_pcs,
    #             'grade_b_cubic':grade_b_cubic
    #         }])
    #     return{
    #         'name':'New',
    #         'partner_id':self.partner_id.id,
    #         'purchase_id':self.id,
    #         # 'arrival_date':self.date_done,
    #         # 'nota':self.nota,
    #         # 'plat_no':self.plat_no,
    #         'line_ids':lines,
    #     }


    def _rekapitulasi_grading_action_view(self):
        views = [(self.env.ref('jidoka_purchase.rekapitulasi_grading_view_tree').id, 'tree'),
                     (self.env.ref('jidoka_purchase.rekapitulasi_grading_view_form').id, 'form')]
        action = {
            'name': _("Rekapitulasi Grading of %s"%(self.display_name)),
            'type': 'ir.actions.act_window',
            'res_model': 'rekapitulasi.grading',
            'view_mode': 'tree,form',
            'views': views,
            'context': {'create': False},
        }
        return action

    # def btn_upt_rekapitulasi_grading(self):
    #     res = self._upt_prepare_rekapitulasi_grading()
    #     rekap_id = self.env['rekapitulasi.grading'].write(res)
    #     action = self._rekapitulasi_grading_action_view()
    #     action['res_id'] = rekap_id.id
    #     action['view_mode'] = 'form'
    #     action['views'] = [(self.env.ref('jidoka_purchase.rekapitulasi_grading_view_form').id, 'form')]
    #     return action  
    
    def btn_create_rekapitulasi_grading(self):
        # import pdb;pdb.set_trace()
        
        res = self._prepare_rekapitulasi_grading()
        # _logger.info('======RES================')
        # _logger.info(res)
        
        rekap_id = self.env['rekapitulasi.grading'].sudo().search([('purchase_id','=',self.id)], limit=1)
        if rekap_id:
            res['name'] = rekap_id.name
            rekap_id.line_ids = [(5, 0, 0)]
            rekap_id.write(res)
        else:
            rekap_id = self.env['rekapitulasi.grading'].create(res)
        action = self._rekapitulasi_grading_action_view()
        action['res_id'] = rekap_id.id
        action['view_mode'] = 'form'
        action['views'] = [(self.env.ref('jidoka_purchase.rekapitulasi_grading_view_form').id, 'form')]
        return action
    

    def action_view_rekapitulasi_grading(self):
        action = self._rekapitulasi_grading_action_view()
        action['domain'] = [('id','in',self.rekapitulasi_grading_ids.ids)]
        return action
    
    # def action_view_rekapan_grading(self):
    #     action = self._rekapan_grading_action_view()
    #     action['domain'] = [('id','in',self.rekapitulasi_grading_ids.ids)]
    #     return action
    
    # def _rekapan_grading_action_view(self):
    #     views = [(self.env.ref('jidoka_purchase.rekapitulasi_grading_view_tree').id, 'tree'),
    #                  (self.env.ref('jidoka_purchase.rekapitulasi_grading_view_form').id, 'form')]
    #     action = {
    #         'name': _("Rekapitulasi Grading of %s"%(self.display_name)),
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'rekapitulasi.grading',
    #         'view_mode': 'tree,form',
    #         'views': views,
    #         'context': {'create': False},
    #     }
    #     return action
    
    
    

    def button_approve_kabag(self):
        for order in self:
            order.write({'state': 'approved_kabag'})  

    def _prepare_picking(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s", self.partner_id.name))
        # kedatangan = 1
        # if self.picking_ids:
        #     picking_id = self.env['stock.picking'].search([('depart_no','!=',False)],order="id desc", limit=1)
        #     if picking_id.depart_no:
        #         kedatangan = int(picking_id.depart_no) + 1
        # print(">>>>>>>>>>>>>>>>>>>>>>>>")
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'user_id': False,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
            'depart_no':'1',
            'fee_location_id':self.fee_location_id.id,
            'is_kayu': self.is_kayu,
            'is_qc_id': self.is_qc_id,
            # 'state': 'grading'
            
            
            
        }
    
    # Edit Sementara
    # def button_approve_manager(self):
    #     for order in self:
    #         order.write({'state': 'purchase', 'date_approve': fields.Datetime.now()})
    #         order.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
    #         order._create_picking()

    def button_approve_manager(self):
        for order in self:
            order.write({'state': 'purchase', 'date_approve': fields.Datetime.now()})
            order.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
            order._create_picking()
        #     if order.state not in ['draft', 'sent','approved_kabag']:
        #         continue
        #     order._add_supplier_to_product()
        #     # Deal with double validation process
        #     if order._approval_allowed():
        #         order.button_approve()
        #     else:
        #         order.write({'state': 'to approve'})
        #     if order.partner_id not in order.message_partner_ids:
        #         order.message_subscribe([order.partner_id.id])
        # return True

    # Edit Sementara
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            # if order._approval_allowed():
            #     order.button_approve()
            # else:
            order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
            
            # if order.is_kayu == True:
            #     if order.state not in ['draft', 'sent']:
            #         continue
            #     order._add_supplier_to_product() 
            #     order.write({'state': 'to approve'})
            #     if order.partner_id not in order.message_partner_ids:
            #         order.message_subscribe([order.partner_id.id])
            # else:
            #     if order.state not in ['draft', 'sent']:
            #         continue
            #     order._add_supplier_to_product()
            #     # Deal with double validation process
            #     if order._approval_allowed():
            #         order.button_approve()
            #     else:
            #         order.write({'state': 'to approve'})
            #     if order.partner_id not in order.message_partner_ids:
            #         order.message_subscribe([order.partner_id.id])
        return True
    
    # def button_confirm(self):
    #     self.write({'state': 'to approve'})
    #     return True


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':        
            prefix = self.env.user.branch_id.code or '' + '/'
            no_seri = self.env['ir.sequence'].next_by_code('seq.purchase.order.ckwi')
            inisial = 'XX'
            last_po = '0000'
            partner_id = False
            if vals.get('partner_id'):
                partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
            if partner_id:
                inisial = partner_id.supplier_code_id.code or 'XX'
                count = str(partner_id.purchase_order_count +1)
                last_po = '000' + count
                if partner_id.purchase_order_count > 9:
                    last_po = '00' + count
                if partner_id.purchase_order_count > 99:
                    last_po = '0' + count
                if partner_id.purchase_order_count > 999:
                    last_po = count
            vals['name'] = prefix + '/' + no_seri + '/' + inisial + '-' + last_po + '/' + str(datetime.datetime.today().month) + '/' + str(datetime.datetime.today().year)

        return super(PurchaseOrder,self).create(vals)

    def write(self, vals):
        if vals.get('partner_id'):
            prefix = self.env.user.branch_id.code or '' + '/'
            no_seri = self.env['ir.sequence'].next_by_code('seq.purchase.order.ckwi')
            inisial = 'XX'
            last_po = '0000'
            partner_id = False
            if vals.get('partner_id'):
                partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
            if partner_id:
                inisial = partner_id.exim_code or 'XX'
                count = str(partner_id.purchase_order_count +1)
                last_po = '000' + count
                if partner_id.purchase_order_count > 9:
                    last_po = '00' + count
                if partner_id.purchase_order_count > 99:
                    last_po = '0' + count
                if partner_id.purchase_order_count > 999:
                    last_po = count
            vals['name'] = prefix + no_seri + '/' + inisial + '-' + last_po + '/' + str(datetime.datetime.today().month) + '/' + str(datetime.datetime.today().year)
        return super(PurchaseOrder,self).write(vals)
   
    @api.depends('order_line.price_total','order_line.fee')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = amount_fee =0.0
            for line in order.order_line:
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
            
    # def _create_picking(self):
    #     StockPicking = self.env['stock.picking']
    #     for order in self.filtered(lambda po: po.state in ('purchase', 'done')):
    #         if any(product.type in ['product', 'consu'] for product in order.order_line.product_id):
    #             order = order.with_company(order.company_id)
    #             pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
    #             if not pickings:
    #                 res = order._prepare_picking()
    #                 picking = StockPicking.with_user(SUPERUSER_ID).create(res)
    #             else:
    #                 picking = pickings[0]
    #             moves = order.order_line._create_stock_moves(picking)
    #             moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
    #             seq = 0
    #             for move in sorted(moves, key=lambda move: move.date):
    #                 seq += 5
    #                 move.sequence = seq
    #             moves._action_assign()
    #             picking.message_post_with_view('mail.message_origin_link',
    #                 values={'self': picking, 'origin': order},
    #                 subtype_id=self.env.ref('mail.mt_note').id)
    #     return True

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    quality = fields.Selection([
        ('fair', 'Fair'),
        ('good', 'Good')
    ], string='Quality')
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    fee = fields.Float(compute='_compute_fee', inverse='_inverse_price', string='Fee',store=True)
    wood_kind_id = fields.Many2one(comodel_name='jidoka.woodkind', string='Jenis Kayu', related='product_id.wood_kind_id')
    price_fee_subtotal = fields.Monetary(compute='_compute_price_fee_subtotal', string='Subtotal Fee', default=0.00,store=True)
    
    # order_type = fields.Many2one(comodel_name="purchase.order.type", string="Order Type")
    # order_type = fields.Many2one(comodel_name="purchase.order.type", string="Order Type",related='order_id.order_type')
    
    
    # order_type = fields.Char('Order type', related='order_id.order_type')
    @api.depends('product_qty', 'price_unit', 'taxes_id', 'fee')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'] + line.fee,  # tambahkan nilai fee ke price_unit
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'],
            )
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })


    def _prepare_compute_all_values(self):
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.order_id.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
            'partner': self.order_id.partner_id,
        }

    @api.depends('order_id.fee_location_id')
    def _compute_fee(self):
        for rec in self:
            res = 0.00
            if rec.order_id.fee_location_id:
                res = rec.order_id.fee_location_id.ongkir + rec.order_id.fee_location_id.fee
            rec.fee = res
    
    def _inverse_price(self):
        pass

    @api.depends('order_id.fee_location_id','fee','product_qty')    
    def _compute_price_fee_subtotal(self):
        for rec in self:
            rec.price_fee_subtotal = rec.fee * rec.product_qty
    
       # TODO seharusnya jangan override!
    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        self.ensure_one()
        self._check_orderpoint_picking_type()
        product = self.product_id.with_context(lang=self.order_id.dest_address_id.lang or self.env.user.lang)
        description_picking = product._get_description(self.order_id.picking_type_id)
        if self.product_description_variants:
            description_picking += "\n" + self.product_description_variants
        date_planned = self.date_planned or self.order_id.date_planned
        return {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.product_id.display_name or '')[:2000],
            'product_id': self.product_id.id,
            'date': date_planned,
            'date_deadline': date_planned + relativedelta(days=self.order_id.company_id.po_lead),
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': (self.orderpoint_id and not (self.move_ids | self.move_dest_ids)) and self.orderpoint_id.location_id.id or self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'description_picking': description_picking,
            'propagate_cancel': self.propagate_cancel,
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
            'product_uom_qty': product_uom_qty,
            'product_uom': product_uom.id,
            'sequence': self.sequence,
            'wood_kind_id': self.wood_kind_id.id
        }



