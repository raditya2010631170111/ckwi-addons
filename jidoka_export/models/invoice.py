from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)




class Invoice(models.Model):
    _name = 'invoice'
    _description = 'Invoice'

    name = fields.Char(
        string='Name',
        required=True,
        copy=False,
        tracking=True,
        index=True,
        widget="button",
        on_click="show_account_move_data",
 )
    invoice_count = fields.Integer(
            compute="_compute_invoice_count", string='Invoice Count', copy=False)
    
    shipping_ins_id = fields.Many2one('shipping.ins', string='shipping_ins')
    packing_id = fields.Many2one('packing.list', string='Packing List')
   
    sail_date = fields.Date(string='Sail Date')
    bl = fields.Char(string='BL')

    # def _compute_invoice_count(self): 
    #     for record in self:
    #         invoice_domain = [('payment_reference', '=', record.name)]
    #         invoice_count = self.env['account.move'].search_count(invoice_domain)
    #         record.invoice_count = invoice_count
            
    def _compute_invoice_count(self):
        for record in self:
            invoice_count = self.env['account.move'].search_count([('payment_reference', '=', record.name)])
            record.invoice_count = invoice_count

    # def _compute_invoice_count(self):
    #     invoice_domain = [('payment_reference', 'in', self.mapped('name'))]
    #     invoice_data = self.env['account.move'].read_group(
    #         invoice_domain,
    #         ['payment_reference'],
    #         ['payment_reference']
    #     )
    #     invoice_counts = {
    #         data['payment_reference'][0]: data['payment_reference_count']
    #         for data in invoice_data
    #     }

    #     for record in self:
    #         record.invoice_count = invoice_counts.get(record.name, 0)

    # def show_invoices(self):
    #     invoice_domain = [('payment_reference', '=', self.name)]
    #     invoices = self.env['account.move'].search(invoice_domain)

    #     action = {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Invoices',
    #         'view_mode': 'tree,form',
    #         'res_model': 'account.move',
    #         # 'view_id': self.env.ref('account.view_out_invoice_tree').id,
    #         # # 'view_id': views,
    #         'domain': invoice_domain,
    #         # 'res_id':invoices.id
    #     }
    #     # if len(invoices) == 1:
    #     #     action.update({
    #     #         'view_mode': 'form',
    #     #         'res_id': invoices[0].id,
    #     #     })
    #     return action
    
    def _invoice_action_view(self):
        views = [(self.env.ref('account.view_out_invoice_tree').id, 'tree'),
        (self.env.ref('account.view_move_form').id, 'form')]
        invoice_domain = [('payment_reference', '=', self.name)]
        action = {
            'name': _("Invoice of %s" % (self.display_name)),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'views': views,
            'domain': invoice_domain,
            'context': {'create': False},
        }
        return action
    
    def show_invoices(self):
        action = self._invoice_action_view()
        action['domain'] = [('payment_reference','=',self.name)]
        self._compute_invoice_count()  # Memperbarui invoice_count sebelum mengembalikan action
        return action
    
        # views = [(self.env.ref('jidoka_export.packing_list_view_tree').id, 'tree'),
        #         (self.env.ref('jidoka_export.packing_list_view_form').id, 'form')]
        # action = {
        #     'name': _("Picking List of %s" % (self.display_name)),
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'packing.list',
        #     'view_mode': 'tree,form',
        #     'views': views,
        #     'context': {'create': False},
        #     'domain': [('id', 'in', self.packing_list_ids.ids)],
        # }
        # return action
    
  
        
    operation_container_line_ids = fields.One2many(comodel_name='invoice.container.line', string='Product Detail', 
                                       inverse_name='invoice_id')
    product_line_ids = fields.One2many(comodel_name='invoice.line', string='Product Detail', 
                                       inverse_name='invoice_id')
    # to_partner_id = fields.Many2one('res.partner', string='To', required=True)
    to_partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    to_partner_country_id = fields.Many2one('res.country', string='To')
    to_city_deliver = fields.Char('Deliver City')
    to_country_of_deliver_id = fields.Many2one('res.country', string='Country of Delivery')
    
    delivery_address_id = fields.Many2one('res.partner', string='Delivery Address')
    invoice_address_id = fields.Many2one('res.partner',string='Invoice Address')
    part_of_load = fields.Char(string='Port of Loading')
    shipper_id = fields.Many2one('res.company', string='shipper', default= lambda r: r.env.user.company_id)
    vessel = fields.Char(string='Vessel')
    peb_no = fields.Char(string='PEB NO.')
    marchandise = fields.Char(string='Merchandise')
    schedule_date = fields.Date('Schedule Date')
    booking_date = fields.Date('Booking date')
    cargo_date = fields.Date('Cargo Date')
    container = fields.Char('Container')
    container_no = fields.Char(string='Container No.')
    source_document_id = fields.Many2one('sale.order','Source Document')

    no_sc_id = fields.Many2one('sale.order', 'SC No.')
    source_document_ids = fields.Many2many('stock.picking', string='Source Documents', compute='_compute_source_documents')
    many_source_document_ids = fields.Many2many('stock.picking', string='Source Documents')
    invoice_container_operation_ids = fields.One2many('invoice.container.operation', 'invoice_id', string='Invoice Container Operation')

    @api.depends('delivery_address_id')
    def _compute_source_documents(self):
        for record in self:
            if record.delivery_address_id:
                # Ubah partner_id menjadi no_sc_id
                no_sc_id = record.no_sc_id.id
                picking_type_code = 'outgoing'
                record.source_document_ids = self.env['stock.picking'].search([
                    ('origin', '=', self.no_sc_id.name),
                    ('picking_type_id.code', '=', picking_type_code),
                    ('state', '=', 'done')
                ])
            else:
                record.source_document_ids = False

    
    freight = fields.Char('Freight')
    seal_no = fields.Char('Seal No.')
    buyer_po = fields.Char('Buyer PO')
    pricelist_id = fields.Many2one('product.pricelist', string='Currency', related='source_document_id.pricelist_id')
    currency_id = fields.Many2one(related='pricelist_id.currency_id', depends=["pricelist_id"], store=True)
    show_update_pricelist = fields.Boolean(string='Has Pricelist Changed', help="Technical Field, True if the pricelist was changed;\n"  " this will then display a recomputation button")
    state = fields.Selection([
        ('draft', 'Draft'),
        # ('waiting', 'Waiting'),
        # ('ready', 'Ready'),
        ('done', 'Done'),
    ], string='State',default='draft', tracking=True)

    city_of_deliver_id = fields.Many2one("res.country.state","Deliver State")
    city_deliver = fields.Char('Deliver City')
    country_of_deliver_id = fields.Many2one('res.country', string='Country of Delivery')
    
    uom_name_line = fields.Char('Measurement')
    total_qty = fields.Float('Total Quantity', compute="_compute_total_qty")
    total_unit_price = fields.Float('Total Unit Price', compute="_compute_total_unit_price")
    total_amount = fields.Float('Total Amount',compute="_compute_total_amount")
    
    
    onboard_date = fields.Date(string='On Board')
    invoice_date = fields.Date(string='Invoice Date')
        
    from_invoice_country_id = fields.Many2one('res.country', string='From Country')
    from_invoice_city = fields.Char('From City')
    to_invoice_country_id = fields.Many2one('res.country', string='To Country')
    to_invoice_city = fields.Char('To City')
    to_invoice_country_state_id = fields.Many2one('res.country.state', string='To Country State')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')
    fob_term_id = fields.Many2one('account.payment.term', string='Term')
    
    # Other Info
    shipping_ins_id = fields.Many2one(string='Shipping', comodel_name='shipping.ins')
    packing_list_id = fields.Many2one(string='Packing List', comodel_name='packing.list')
    partner_invoice_id = fields.Many2one('res.partner',string='Invoice Address')
    partner_shipping_id = fields.Many2one('res.partner',string='Customer')
    no_peb = fields.Integer(string='PEB No.', readonly=True)
    
    invoice_order_line_ids = fields.One2many(comodel_name='invoice.order.line',inverse_name='export_invoice_id', string='Invoice Order Line')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,index=True)
    
    
    # field_name_ids = fields.One2many(
    #     string='field_name',
    #     comodel_name='model.name',
    #     inverse_name='inverse_field',
    # )
    
    
    no_sc_ids = fields.Many2many(
        string='No SC',
        comodel_name='sale.order',
        relation='invoice_nosc_order_rel',
        column1='invoice_id',
        column2='order_id',
    )

    @api.onchange('source_document_id')
    def onchange_source_document_id(self):
        self.pricelist_id = self.source_document_id.pricelist_id
    
    @api.depends('product_line_ids.product_uom_qty')
    def _compute_total_qty(self):
        for record in self:
            subtotal_product_uom_qty = sum(record.product_line_ids.mapped('product_uom_qty'))
            record.total_qty = subtotal_product_uom_qty

    @api.depends('product_line_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            subtotal_amount = sum(record.product_line_ids.mapped('amount'))
            record.total_amount = subtotal_amount

    @api.depends('product_line_ids.unit_price')
    def _compute_total_unit_price(self):
        for record in self:
            subtotal_unit_price = sum(record.product_line_ids.mapped('unit_price'))
            record.total_unit_price = subtotal_unit_price

    def _prepare_invoice_lines(self):
        line_detail_inv = []
        for line in self.product_line_ids:
            line_detail = {
                'product_id': line.product_id.id,
                'name': line.name,
                'quantity': line.product_uom_qty,
                'product_uom_id': line.uom_id.id,
                'price_unit': line.unit_price,
                'price_subtotal': line.amount,
                'account_id': line.account_id.id,
            }
            line_detail_inv.append(line_detail)
            # line_detail_inv.append((0, 0, line_detail))
        return line_detail_inv
    
    def send_data(self):
        invoice_ex = self.env['account.move'].create({
            'move_type' : 'out_invoice',
            'payment_reference': self.name,
            'partner_id': self.to_partner_id.id,
            'partner_shipping_id': self.delivery_address_id.id,
            'peb_no': self.peb_no,
            'invoice_date': self.booking_date,
            'state': 'draft',
            'invoice_date_due': self.schedule_date,
            'origin_ids': [(6, 0, self.many_source_document_ids.ids)],
        })
        invoice_lines = []
        for line in self.product_line_ids:
            line_detail = self.env['account.move.line'].create({
                'product_id': line.product_id.id,
                'name': line.name,
                'quantity': line.product_uom_qty,
                'product_uom_id': line.uom_id.id,
                'price_unit': line.unit_price,
                'price_subtotal': line.amount,
                'account_id': line.account_id.id,
                'move_id': invoice_ex.id,
            })
            invoice_lines.append((0, 0, {
                'product_id': line_detail.product_id.id,
                'name': line_detail.name,
                'quantity': line_detail.quantity,
                'product_uom_id': line_detail.product_uom_id.id,
                'price_unit': line_detail.price_unit,
                'price_subtotal': line_detail.price_subtotal,
                'account_id': line_detail.account_id.id,
                'move_id': invoice_ex.id,
            }))
        invoice_ex.write({'invoice_line_ids': invoice_lines})
        return invoice_ex

    # def _prepare_so(self):
    #     sale_order  = self.env['sale.order'].search([('name','=',self.no_sc_id.name)])
    #     if sale_order:
    #         for sc in sale_order:
    #             # if sc.invoice_status == 'no':
    #             if sc.invoice_status == 'to invoice':
    #                 # sc._create_invoices(final=self.deduct_down_payments)
    #                 sc._create_invoices()
                    
    #                 # sc.write({'invoice_status': 'invoiced'})
                    
    def action_validate(self):
        if self.state == 'draft':
            self.write( { 
                         'state': 'done',
                         })
            for invoice_container in self.invoice_container_operation_ids:
                for line in invoice_container.invoice_container_operation_line_ids:
                    if not line.account_id:
                        raise ValidationError('Account in Container Operation Line can not empty, You must fill Income Account inside Product Category')
        
        
        
        # Data Invoice di export masuk ke dalam invoice di accounting
        # Di modul sales (sale.order) ketika berada state sale(Done) tombol create invoice tidak ada, invoice status berubah menjadi invoiced (Fully Invoiced), muncul tombol smart button
        
        invoice_ex = self.env['account.move'].create({
            # 'ref': self.client_order_ref or '', #belum ada di invoice export
            'move_type' : 'out_invoice',
            # 'narration': self.note, #belum ada di invoice export
            # 'currency_id': self.pricelist_id.currency_id.id, #belum ada di invoice export
            # 'campaign_id': self.campaign_id.id, #belum ada di invoice export
            # 'medium_id': self.medium_id.id, #belum ada di invoice export
            # 'source_id': self.source_id.id, #belum ada di invoice export
            # 'user_id': self.user_id.id, #belum ada di invoice export
            # 'invoice_user_id': self.user_id.id, #belum ada di invoice export
            # 'team_id': self.team_id.id, #belum ada di invoice export
            # 'partner_id': self.partner_invoice_id.id, #belum ada di invoice export
            'partner_id': self.to_partner_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            # 'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(self.partner_invoice_id.id)).id, #belum ada di invoice export
            # 'partner_bank_id': self.company_id.partner_id.bank_ids.filtered(lambda bank: bank.company_id.id in (self.company_id.id, False))[:1].id, #belum ada di invoice export
            # 'journal_id': journal.id,  # company comes from the journal #belum ada di invoice export
            'invoice_origin': ', '.join(self.no_sc_ids.mapped('name')),
            # 'invoice_payment_term_id': self.payment_term_id.id, #belum ada di invoice export
            'payment_reference': self.name,
            # 'transaction_ids': [(6, 0, self.transaction_ids.ids)], #belum ada di invoice export
            # 'company_id': self.company_id.id, #belum ada di invoice export
            'peb_no': self.no_peb,
            'invoice_date': self.invoice_date,
            'state': 'draft',
            'invoice_date_due': self.schedule_date,
            'invoice_line_ids':[(0,0,{
                # 'display_type': self.display_type,
                # 'sequence': self.sequence, #belum ada di invoice export
                # 'name': self.name, #belum ada di invoice export
                'product_id': line.product_id.id,
                'product_uom_id': line.product_uom_id.id,
                'quantity': line.quantity,
                # 'discount': self.discount, #belum ada di invoice export
                'price_unit': line.price_unit,
                # 'tax_ids': [(6, 0, self.tax_id.ids)], #belum ada di invoice export
                # 'analytic_account_id': self.order_id.analytic_account_id.id if not self.display_type else False, #belum ada di invoice export
                # 'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)], #belum ada di invoice export
                'sale_line_ids': [(4, line.order_line_id.id)], #UTAMA
                'price_subtotal': line.amount,
                'account_id': line.account_id.id,
                # 'quantity': line.product_uom_qty,
                # 'move_id': invoice_ex.id,
            # })for line in self.invoice_container_operation_ids.invoice_container_operation_line_ids]
            })for line in self.invoice_order_line_ids]
        })
        
        
        
        # for ie in invoice_ex:
        #     ie.action_post()
            
        # print(self._prepare_so())
        # _logger.info("=================PREPARE SO==================")
        # _logger.info(self._prepare_so())
        # _logger.info("=================PREPARE SO==================")
        return invoice_ex
        # return True
                
    
    def action_approve(self):
        if self.state == 'waiting':
            self.write( { 
                         'state': 'ready',
                         })
    
    def action_done(self):
        if self.state == 'ready':
            self.write( { 
                         'state': 'done',
                         })
            
    def action_sign(self):
         if self.state == 'waiting':
            self.write( { 
                         'state': 'ready',
                         })
            
    def action_print(self):
        if self.state == 'waiting':
            self.write( { 
                        'state': 'ready',
                        })
    
    def action_scrap(self):
        if self.state == 'waiting':
            self.write( { 
                        'state': 'ready',
                        })
            
    def action_unlock(self):
        if self.state == 'waiting':
            self.write( { 
                        'state': 'ready',
                        })
    
    def action_cancel(self):
        if self.state == 'waiting':
            self.write( { 
                        'state': 'ready',
                        })   

    @api.onchange('pricelist_id')
    def _onchange_pricelist_id(self):
        if self.pricelist_id and self._origin.pricelist_id != self.pricelist_id:
            self.show_update_pricelist = True
        else:
            self.show_update_pricelist = False

    def _get_update_prices_lines(self):
        """ Hook to exclude specific lines which should not be updated based on price list recomputation """
        return self(lambda line: not line.display_type)

    def update_prices(self):
        self.ensure_one()
        for line in self._get_update_prices_lines():
            line.product_uom_change()
            line.discount = 0  # Force 0 as discount for the cases when _onchange_discount directly returns
            line._onchange_discount()
        self.show_update_pricelist = False
        self.message_post(body=_("Product prices have been recomputed according to pricelist <b>%s<b> ", self.pricelist_id.display_name))
    
    invoice_id = fields.Many2one(
        string='Invoice',
        comodel_name='packing.list',
        # ondelete='restrict',
    )
class InvoiceLine(models.Model):
    _name = 'invoice.line'
    _description = 'Invoice Line'
    

    name = fields.Char(string='Description')
    invoice_id = fields.Many2one(comodel_name='invoice', string='Invoice')
    product_id = fields.Many2one(comodel_name= 'product.product', string='Product')
    uom_id = fields.Many2one("uom.uom","Unit Of Measure", store=True, related='product_id.uom_id')
    lot_id = fields.Many2one(comodel_name='stock.production.lot', string='Lot/Serial Number')
    location_id = fields.Many2one('stock.location', string='From')
    qty_done = fields.Float('Done')
    product_uom_qty = fields.Float('Quantity')
    reserved = fields.Float('Reserved')
    unit_price = fields.Float('Unit Price', store=True)
    amount = fields.Float('Amount',store=True)
    sku = fields.Char('SKU')

    seal_no = fields.Char('Seal No.')
    container_no = fields.Char(string='Container No.')
    move_id = fields.Many2one('stock.move', string='Move', ondelete='cascade')
    picking_id = fields.Many2one('stock.picking', string='Transfers')
    order_line_id = fields.Many2one('sale.order.line', string='Order Line', store=True)
    account_id = fields.Many2one('account.account', store=True,string='Account', related='categ_id.property_account_income_categ_id') 
    categ_id = fields.Many2one(
        'product.category', 'Product Category', ondelete='cascade', related='product_id.categ_id',store=True)

class InvoiceContainerLine(models.Model):
    _name = 'invoice.container.line'
    _description = 'Invoice Container Line'

    invoice_id = fields.Many2one(comodel_name='invoice', string='Invoice')
    no_sc_ids = fields.Many2many('stock.picking',string='SC No', store=True)
    many_no_sc_id = fields.Many2one('stock.picking', string='SC No', store=True)
    container_no = fields.Char('Container No.')
    seal_no = fields.Char('Seal No.')


class InvoiceContainerOperation(models.Model):
    _name = 'invoice.container.operation'
    _description = 'Container Operation'
    
    invoice_id = fields.Many2one(comodel_name='invoice', string='Packing List',store=True)
    container_no = fields.Char('Container No.')
    seal_no = fields.Char('Seal No.')
    order_id = fields.Many2one('sale.order', string='order', compute='_compute_order_id', store=True)
    
    invoice_container_operation_line_ids = fields.One2many(comodel_name='invoice.container.operation.line', inverse_name='invoice_container_operation_id', string='Operation Container Line', store=True)
    picking_ids = fields.Many2many('stock.picking', 'invoice_cont_picking_ids_rel', 'invoice_cont_op_id', 'picking_id', string='SC No', store=True)
    # move_container_ids = fields.Many2many('stock.move','container_operation_move_rel', string='Move Container', compute='_compute_move_container_ids', store=True,)
    
    # available_picking_ids = fields.Many2many('stock.picking', 'container_operation_available_picking_rel', 'container_operation_id', 'picking_id',  string='Available Picking', compute="_get_available_picking", store=True)
    
    total_net_wght = fields.Float('Total Net Weight',)
    total_gross_wght = fields.Float('Total Gross Weight',)
    total_means = fields.Float('Total Measurement',)
    total_qty = fields.Float('Total Quantity', )
    total_qty_pcs = fields.Float('Total Quantity Pcs',)
    total_qty_set = fields.Float('Total Quantity Set',)
    total_pack = fields.Float('Total Pack',)
    volume_uom_name_line = fields.Char('Measurement')
    weight_uom_name_line = fields.Char('weight_uom_name')
    uom_name_line = fields.Char('Measurement')
    buyer_po = fields.Char('Buyer PO')

    # @api.depends('invoice_container_operation_line_ids.quantity_done')
    # def _compute_total_qty_pcs(self):
    #     for rec in self:
    #          subtotal_qty_pcs = 0.0
    #          for c_line in rec.invoice_container_operation_line_ids:
    #              if c_line.product_uom.name == 'pcs':
    #                  subtotal_qty_pcs += c_line.quantity_done
    
class InvoiceContainerOperationLine(models.Model):
    _name = 'invoice.container.operation.line'
    _description = 'Invoice Container Operation Line'
    
    move_id = fields.Many2one('stock.move', string='Move')
    invoice_container_operation_id = fields.Many2one('invoice.container.operation', string='Invoice Container Operation')
    picking_id = fields.Many2one('stock.picking', string='picking', store=True, )
    order_line_id = fields.Many2one('sale.order.line', string='Order Line', )
    product_container_qty = fields.Float('Quantity in Cont.', store=True)
    
    invoice_id = fields.Many2one(comodel_name='invoice', string='Invoice List', related='invoice_container_operation_id.invoice_id',store=True)
    product_id = fields.Many2one(comodel_name= 'product.product', string='Product',store=True, related='move_id.product_id')
    product_uom_qty = fields.Float('Quantity', store=True, related='move_id.product_uom_qty')
    quantity_done = fields.Float('Quantity', store=True, related='move_id.quantity_done')
    container_no = fields.Char('Container No.', related='invoice_container_operation_id.container_no',store=True)
    seal_no = fields.Char('Seal No.', related='invoice_container_operation_id.seal_no',store=True)
    # pack = fields.Float('Pack (CTN)', store=True, related='product_id.pack' )
    # net_weight = fields.Float('Net Weight (KGS)', store=True , related='product_id.net_weight')
    # gross_weight = fields.Float('Gross Weight (KGS)', store=True, related='product_id.gross_weight' )
    # means = fields.Float('Measurement(CBM)', store=True , related='product_id.means')
    pack = fields.Float('Pack (CTN)', store=True)
    net_weight = fields.Float('Net Weight (KGS)', store=True )
    gross_weight = fields.Float('Gross Weight (KGS)', store=True)
    means = fields.Float('Measurement(CBM)', store=True )
    sku = fields.Char('SKU', store=True)
    product_uom = fields.Many2one('uom.uom', string='UoM',store=True, related='move_id.product_uom')
    unit_price = fields.Float('Unit Price', store=True)
    account_id = fields.Many2one('account.account', store=True,string='Account', related='categ_id.property_account_income_categ_id')
    
    categ_id = fields.Many2one(
        'product.category', 'Product Category', ondelete='cascade', related='product_id.categ_id',store=True)
    property_stock_valuation_account_id = fields.Many2one(
        'account.account', 'Stock Valuation Account', related='categ_id.property_stock_valuation_account_id')
    amount = fields.Float('Amount')
    
    
                
    @api.onchange('product_id','product_container_qty')
    def onchange_field(self):
        # for r in self.container
        self.pack = self.product_container_qty * self.product_id.pack
        self.net_weight = self.product_container_qty * self.product_id.net_weight
        self.gross_weight = self.product_container_qty * self.product_id.gross_weight
        self.means = self.product_container_qty * self.product_id.means
    