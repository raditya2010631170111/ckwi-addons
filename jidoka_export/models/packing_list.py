from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

#1 packing list
class PackingList(models.Model):
    _name = 'packing.list'
    _description = 'Packing List'
    _inherit = ['mail.thread']

    name = fields.Char(string='Name',copy=False, readonly=True, tracking=True, index=True)
    no_sc_id = fields.Many2one('sale.order', 'SC No.')
    nosc_name = fields.Char('nosc_name', related='no_sc_id.name')
    to_partner_id = fields.Many2one('res.partner', string='Buyer',)
    to_partner_country_id = fields.Many2one('res.country', string='To')
    to_city_deliver = fields.Char('Deliver City')
    to_country_of_deliver_id = fields.Many2one('res.country', string='Country of Delivery')
    delivery_address_id = fields.Many2one('res.partner', string='Delivery Address', readonly=True)
    invoice_address_id = fields.Many2one('res.partner',string='Invoice Address')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,
        index=True)
    
    # TODO harusnya jangan hard code
    # shipper_id = fields.Many2one('res.company', string='Shipper', default=lambda self: self.env['res.company'].search([('name', '=', 'PT. CIPTA KREASI WOOD INDUSTRY')]),readonly=True)   
    shipper_id = fields.Many2one('res.company', string='shipper', default= lambda r: r.env.user.company_id)
    vessel = fields.Char(string='Vessel',)
    peb_no = fields.Char(string='PEB NO.', readonly=True)
    marchandise = fields.Char(string='Merchandise')
    schedule_date = fields.Date('Schedule Date')
    booking_date = fields.Date('Booking date')
    # cargo_date = fields.Date('Cargo Date', required=True)
    source_document_ids = fields.Many2many('stock.picking', string='Source Documents',
        compute='_compute_source_document_ids')
    # container data (details)
    container_operation_ids = fields.One2many(comodel_name='container.operation',
        string='Container Operation', inverse_name='packing_id')
    container_operation_line_ids = fields.One2many(comodel_name='container.operation.line', string='Product Detail', 
        inverse_name='packing_id')
    # TODO remove me?
    container = fields.Char('Container')
    container_no = fields.Char(string='Container No.')
    freight = fields.Char('Freight')
    seal_no = fields.Char('Seal No.')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('ready', 'Ready'),
        ('done', 'Done'),
    ], string='State', default='draft', tracking=True, required=True, readonly=True, copy=False)
    # TODO remove me
    picking_id = fields.Many2one('stock.picking', string='Transfers')
    no_st_id = fields.Many2one('stock.picking', string='no_st')
    # total data
    total_net_wght = fields.Float('Total Net Weight', compute='_compute_totals')
    total_gross_wght = fields.Float('Total Gross Weight', compute='_compute_totals')
    total_means = fields.Float('Total Measurement', compute='_compute_totals')
    total_qty_pcs = fields.Float('Total Quantity', compute='_compute_totals')
    total_qty_set = fields.Float('Total Quantity', compute='_compute_totals')
    total_pack = fields.Float('Total Pack', compute='_compute_totals')

    volume_uom_name_line = fields.Char('Measurement')
    weight_uom_name_line = fields.Char('weight_uom_name')
    uom_name_line = fields.Char('Measurement')
    city_of_deliver_id = fields.Many2one("res.country.state", "Deliver State")
    city_deliver = fields.Char('Deliver City')
    country_of_deliver_id = fields.Many2one('res.country', string='Country of Delivery')
    # buyer_po = fields.Char('Buyer PO', )
    buyer_po = fields.Char('Buyer PO', 
        compute='_compute_buyer_po',store=True )
    @api.depends('container_operation_ids.container_operation_line_ids.buyer_po')
    def _compute_buyer_po(self):
        for record in self:
            # buyer_pos = record.container_operation_ids.container_operation_line_ids.mapped('buyer_po')
            # buyer_pos = list(set(buyer_pos))  # Menghapus duplikat dengan menggunakan set()
            # # record.buyer_po = ', '.join(buyer_pos)
            # buyer_pos = [str(po) for po in buyer_pos if isinstance(po, str)]

            # record.buyer_po = ', '.join(buyer_pos)
            
            buyer_pos = record.container_operation_ids.container_operation_line_ids.filtered(lambda r: r.buyer_po).mapped('buyer_po')
            buyer_pos = list(set(buyer_pos))
            record.buyer_po = ', '.join(buyer_pos)



    
    # # @api.depends('container_operation_ids')
    # # def _compute_buyer_po(self):
    # #     for record in self:
    # #         cust_refs = record.container_operation_ids.container_operation_line_ids.mapped('cust_ref')
    # #         buyer_po = ','.join(cust_refs)
    # #         record.buyer_po = buyer_po
    #     # for r in self:
    #     #     cust_ref = r.container_operation_ids.container_operation_line_ids.mapped('cust_ref')
    #     #     if cust_ref:
    #     #         r.buyer_po = ','.join(cust_ref)
    # # self.container_operation_ids.container_operation_line_ids.mapped('cust_ref')
    #     # for r in self:
    #     #     cust_ref = r.container_operation_ids.container_operation_line_ids.mapped('cust_ref')
    #     #     if cust_ref and isinstance(cust_ref, list):
    #     #         r.buyer_po = ','.join(cust_ref)
    #     #     else:
    #     #         r.buyer_po = ''
    
    # @api.depends('container_operation_ids.container_operation_line_ids')
    # def _compute_buyer_po(self):
    #     for rec in self:
    #         # buyer_po = ""
    #         # # container_operations = record.container_operation_ids
    #         # container_operations = record.container_operation_ids.filtered(lambda line: line.container_operation_line_ids.buyer_po == )
    #         # # filtered_lines = rec.container_operation_line_ids.filtered(lambda line: line.move_id == move_id  )
    #         # for container_operation in container_operations:
    #         #     container_lines = container_operation.container_operation_line_ids
    #         #     buyer_po += ",".join(container_lines.mapped('buyer_po'))

    #         # record.buyer_po = buyer_po
    #         buyer_pos = rec.container_operation_ids.container_operation_line_ids.mapped('buyer_po')
    #         for buyer_po in buyer_pos:
    #             filtered_lines = rec.container_operation_ids.container_operation_line_ids.filtered(lambda line: line.buyer_po == buyer_po)
    #             for line in filtered_lines:
    #                 rec.buyer_po = ','.join(line)
            
            
    # move_ids = rec.container_operation_line_ids.mapped('move_id')
    #         # for product_id in product_ids:
    #         vals = {}
    #         for move_id in move_ids:
    #             # filtered_lines = rec.container_operation_line_ids.filtered(lambda line: line.product_id == product_id  )
    #             filtered_lines = rec.container_operation_line_ids.filtered(lambda line: line.move_id == move_id  )
    #             total_price = sum(line.unit_price for line in filtered_lines)
    #             total_qty = sum(line.product_container_qty for line in filtered_lines)
    #             amount = sum(line.amount for line in filtered_lines)
    #             pack = sum(line.pack for line in filtered_lines)
    #             net_weight = sum(line.net_weight for line in filtered_lines)
    #             gross_weight = sum(line.gross_weight for line in filtered_lines)
    #             means = sum(line.means for line in filtered_lines)    
    
    invoice_count = fields.Integer(compute="_compute_invoice_count", string='Invoice Count',
        copy=False,)
    invoice_ids = fields.One2many(string='Invoice', comodel_name='invoice', inverse_name='invoice_id',)
    
    sail_date = fields.Date(string='Sail Date')
    bl = fields.Char(string='BL')
    onboard_date = fields.Date(string='On Board')
    invoice_date = fields.Date(string='Invoice Date')
    
    from_packing_country_id = fields.Many2one('res.country', string='From Country', )
    from_packing_city = fields.Char('From City City', )
    to_packing_city = fields.Char('To City', )
    to_packing_country_state_id = fields.Many2one('res.country.state', string='To Country State', )
    to_packing_country_id = fields.Many2one('res.country', string='To Country', )
    # payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')
    fob_term_id = fields.Many2one('account.payment.term', string='Term')
    
    # Other Info
    shipping_ins_id = fields.Many2one(string='Shipping', comodel_name='shipping.ins', readonly=True)
    partner_invoice_id = fields.Many2one('res.partner',string='Invoice Address', 
        compute='_compute_partner_invoice_id' )
    partner_shipping_id = fields.Many2one('res.partner',string='Customer')
    no_peb = fields.Integer(string='PEB No.', readonly=True)
    
    no_sc_ids = fields.Many2many(
        string='No SC',
        comodel_name='sale.order',
        relation='packinglist_nosc_order_rel',
        column1='packing_list_id',
        column2='order_id',
    )
    available_order_line_ids = fields.Many2many(
        string='Available Order Line',
        comodel_name='sale.order.line',
        relation='packing_list_available_order_line_order_rel',
        column1='packing_list_id',
        column2='order_line_id', 
            compute='_compute_available_order_line_ids' )
    
    currency_id = fields.Many2one('res.currency', string='Currency', compute='_compute_currency_id' )
    
    @api.depends('company_id')
    def _compute_currency_id(self):
        for r in self:
            r.currency_id = r.company_id.currency_id.id
    
    packing_list_order_line_ids = fields.One2many(comodel_name='packing.list.order.line',inverse_name= 'packing_id', string='Packing List Order Line', compute='_compute_packing_list_order_line_ids',store=True)
    
    
    @api.depends('container_operation_line_ids.product_container_qty')
    def _compute_packing_list_order_line_ids(self):
        _logger.info("============A==============")
        if not self.container_operation_ids:
            self.container_operation_line_ids = False
            
        if not self.container_operation_ids:
            self.packing_list_order_line_ids = False
            
        if not self.container_operation_line_ids:
            self.packing_list_order_line_ids = False
        for rec in self:
            packinglist_order = []
            # product_ids = rec.container_operation_line_ids.mapped('product_id')
            move_ids = rec.container_operation_line_ids.mapped('move_id')
            # for product_id in product_ids:
            vals = {}
            for move_id in move_ids:
                # filtered_lines = rec.container_operation_line_ids.filtered(lambda line: line.product_id == product_id  )
                filtered_lines = rec.container_operation_line_ids.filtered(lambda line: line.move_id == move_id  )
                total_price = sum(line.unit_price for line in filtered_lines)
                total_qty = sum(line.product_container_qty for line in filtered_lines)
                amount = sum(line.amount for line in filtered_lines)
                pack = sum(line.pack for line in filtered_lines)
                net_weight = sum(line.net_weight for line in filtered_lines)
                gross_weight = sum(line.gross_weight for line in filtered_lines)
                means = sum(line.means for line in filtered_lines)
                

                for line in filtered_lines:
                    vals = {
                    'move_id': line.move_id.id,
                    'packing_id': rec.id,
                    'product_id': line.product_id.id,
                    'price_unit': total_price,
                    'amount': amount,
                    'quantity':total_qty,
                    'product_uom_id':line.product_uom.id,
                    'pack':line.pack,
                    'net_weight':line.net_weight,
                    'gross_weight':line.gross_weight,
                    'means':line.means,
                    'order_line_id':line.order_line_id.id,
                    # 'buyer_po':line.buyer_po,
                    'cust_ref':line.cust_ref,
                }
                packinglist_order.append((0, 0, vals))
                
            rec.packing_list_order_line_ids.unlink()  # Hapus baris yang ada sebelum membuat yang baru
            rec.packing_list_order_line_ids = packinglist_order
            _logger.info("============C==============")
            _logger.info(rec.packing_list_order_line_ids)
    
    
    @api.depends('to_partner_id')
    def _compute_partner_invoice_id(self):
        for r in self:
            r.partner_invoice_id = r.to_partner_id.id
        
    @api.depends('no_sc_ids.order_line')
    def _compute_available_order_line_ids(self):
        for shipping_ins in self:
            order_lines = shipping_ins.no_sc_ids.mapped('order_line')
            shipping_ins.available_order_line_ids = order_lines
    

    @api.depends('no_sc_id')
    def _compute_source_document_ids(self):
        for record in self:
            if record.delivery_address_id:
                record.source_document_ids = self.env['stock.picking'].search([
                    ('origin', '=', record.nosc_name),
                    ('state', '=', 'done'),
                    ('picking_type_code', '=', 'outgoing')])
            else:
                record.source_document_ids = False
    
    # @api.depends(
    #     'container_operation_line_ids',
    #     'container_operation_line_ids.product_id',
    #     'container_operation_line_ids.product_container_qty'
    #     )
    def _compute_totals(self):
        for record in self:
            # pack
            # subtotal_pack = sum(line.pack * line.product_container_qty for line in record.container_operation_line_ids)
            subtotal_pack = sum(line.pack for line in record.container_operation_line_ids)
            # qty
            subtotal_qty_pcs = 0.0
            subtotal_qty_set = 0.0
            for p_line in record.container_operation_line_ids:
                if p_line.product_uom.name == 'pcs':
                    subtotal_qty_pcs += p_line.product_container_qty
                elif p_line.product_uom.name == 'set':
                    subtotal_qty_set += p_line.product_container_qty
            # means
            # subtotal_means = sum(line.means * line.product_container_qty for line in record.container_operation_line_ids)
            subtotal_means = sum(line.means for line in record.container_operation_line_ids)
            # gross
            # total_weight_gross = sum(record.container_operation_line_ids.mapped(lambda line: line.gross_weight * line.product_container_qty))
            total_weight_gross = sum(record.container_operation_line_ids.mapped(lambda line: line.gross_weight))
            # weight
            # total_weight = sum(record.container_operation_line_ids.mapped(lambda line: line.net_weight * line.product_container_qty))
            total_weight = sum(record.container_operation_line_ids.mapped(lambda line: line.net_weight))

            record.total_pack = subtotal_pack
            record.total_qty_pcs = subtotal_qty_pcs
            record.total_qty_set = subtotal_qty_set
            record.total_means = subtotal_means
            record.total_gross_wght = total_weight_gross
            record.total_net_wght = total_weight

    @api.onchange('country_of_deliver_id')
    def _onchange_country_of_deliver_id(self):
        self.city_of_deliver_id = True
    
    # --- actions ---
    def action_validate(self):
        for r in self:
            if not r.from_packing_city:
                raise UserError(_('From City Empty.'))
            if not r.from_packing_country_id:
                raise UserError(_('From Country Empty.'))
            if not r.to_packing_city:
                raise UserError(_('To City Empty.'))
            # if not r.to_packing_country_state_id:
            #     raise UserError(_('To State Empty.'))
            if not r.to_packing_country_id:
                raise UserError(_('To Country Empty.'))
            if not r.buyer_po:
                raise UserError(_('Buyer PO Empty.'))
            
            if not r.invoice_date:
                raise UserError(_('Invoice Date Empty.'))
            # if not r.sail_date:
            #     raise UserError(_('Sail Date Empty.'))
            # if not r.bl:
            #     raise UserError(_('BL Empty.'))
            
            # if not r.vessel:
            #     raise UserError(_('Vessel Empty.'))
            # if not r.onboard_date:
            #     raise UserError(_('Onboard Date Empty.'))
            if not r.fob_term_id:
                raise UserError(_('Term Empty.'))
            
            if not r.container_operation_ids:
                raise UserError(_('Container Empty.'))
            for container in r.container_operation_ids:
                if not container.total_qty:
                    raise UserError(_('Total Quantity Empty. Details in Container must filled'))
            
        if self.state == 'draft':
            self.write({'state': 'waiting',})

    # INI WORK UNTUK SOLUSI BERDASARKAN many_source_document_ids yang terpilih
    def action_approve(self):
        # TODO jangan seperti ini, biasakan pakai ID
        # count_stock_picking = len(self.env['stock.picking'].search([('origin', '=', self.source_document_ids.name)]))
        # count_done = len(self.env['stock.picking'].search([('origin', '=', self.source_document_ids.name), ('state', '=', 'done')]))
        #entar dipake kalo perlu
        # if count_stock_picking != count_done:
        #     raise ValidationError('Unable to validate, all stock picking must be in done status to perform validation')
        
        # selected_stock_pickings = self.many_source_document_ids.filtered(lambda picking: picking.state == 'done')
        #entar dipake kalo perlu
        # if len(selected_stock_pickings) != len(self.many_source_document_ids):
        #     raise ValidationError('Unable to validate, all selected stock pickings must be in done status to perform validation')
        if self.state == 'waiting':
            #entar dipake kalo perlu
            # if not self.no_st_id or self.no_st_id.state != 'done':
            #     raise ValidationError('Unable to validate, please check again whether done status has been fulfilled or not')
            self.write({ 
                'state': 'ready',
            })
    
    def action_done(self):
        if self.state == 'ready':
            self.write({'state': 'done'})
            invoice_list = self.env['invoice'].create({
                'name': self.name,
                'to_partner_id': self.to_partner_id.id,
                'shipping_ins_id':self.shipping_ins_id.id,
                'packing_id':self.id,
                'shipper_id':self.shipper_id.id,
                'no_sc_ids': self.no_sc_ids,
                'from_invoice_country_id': self.from_packing_country_id.id ,
                'from_invoice_city':self.from_packing_city,
                'to_invoice_country_id': self.to_packing_country_id.id ,
                'to_invoice_country_state_id': self.to_packing_country_state_id.id ,
                'to_invoice_city':self.to_packing_city,
                'buyer_po' : self.buyer_po,
                'invoice_date': self.invoice_date,
                'sail_date': self.sail_date,
                'bl' : self.bl,
                'vessel': self.vessel,
                'onboard_date': self.onboard_date,
                'fob_term_id': self.fob_term_id.id,
                'no_peb': self.no_peb,
                'partner_invoice_id':self.partner_invoice_id.id,
                'partner_shipping_id':self.partner_shipping_id.id,
                # 'company_id':self.company_id, #tambahan
                # 'currency_id':self.currency_id, #tambahan
                'invoice_container_operation_ids': [(0, 0, {
                    'picking_ids': line.picking_ids,
                    'container_no': line.container_no,
                    'seal_no': line.seal_no,
                    'total_qty_pcs' : line.total_qty_pcs,
                    'total_qty_set' : line.total_qty_set,
                    'total_pack' : line.total_pack,
                    'total_net_wght' : line.total_net_wght,
                    'total_gross_wght' : line.total_gross_wght,
                    'total_means' : line.total_means,
                    'buyer_po':line.buyer_po,
                    'invoice_container_operation_line_ids':[(0,0,{
                        'container_no':in_line.container_no,
                        'order_line_id':in_line.order_line_id.id,
                        'move_id': in_line.move_id.id,
                        'container_no': in_line.container_no,
                        'seal_no': in_line.seal_no,
                        'product_id': in_line.product_id.id,
                        'quantity_done': in_line.quantity_done,
                        # 'product_uom': in_line.product_uom.id,
                        'product_container_qty': in_line.product_container_qty,
                        'pack': in_line.pack,
                        'net_weight': in_line.net_weight,
                        'gross_weight': in_line.gross_weight,
                        'means': in_line.means,
                        'unit_price': in_line.unit_price,
                        'amount': in_line.amount,
                        # 'account_id': line.account_id.id,
                    })for in_line in line.container_operation_line_ids],
                    # 'invoice_id': line.invoice_id.id,e.id,
                    # 'product_uom_qty': line.product_uom_qty
                }) for line in self.container_operation_ids],
                'product_line_ids': [(0, 0, {
                    'container_no': line.container_no,
                    'seal_no': line.seal_no,
                    # 'account_id': line.account_id.id,
                    'product_id': line.product_id.id,
                    'sku': line.sku,
                    'product_uom_qty': line.product_container_qty,
                    'unit_price': line.unit_price,
                    'amount': line.amount,
                    'move_id': line.move_id.id,
                    'picking_id': line.picking_id.id,
                    'order_line_id': line.order_line_id.id,
                    # 'uom_id': line.product_uom.id,
                }) for line in self.container_operation_line_ids],
                'invoice_order_line_ids': [(0, 0, {
                    'move_id': line.move_id.id,
                    'company_id': line.company_id.id,
                    # 'account_id': line.account_id.id,
                    'product_id': line.product_id.id,
                    'price_unit': line.price_unit,
                    'amount': line.amount,
                    'quantity':line.quantity,
                    'product_uom_id':line.product_uom_id.id,
                    'pack':line.pack,
                    'net_weight':line.net_weight,
                    'gross_weight':line.gross_weight,
                    'means':line.means,
                    # 'order_line_id': line.order_line_id.id,
                    # 'uom_id': line.product_uom.id,
                }) for line in self.packing_list_order_line_ids],
            })
            self.invoice_ids = [(4, invoice_list.id, 0)]
            
            # return {
            #     'name': 'Invoice',
            #     'view_type': 'form',
            #     'view_mode': 'form',
            #     'res_model': 'invoice',
            #     'type': 'ir.actions.act_window',
            #     'res_id': invoice_list.id,
            # }
        return True
        
            
    def action_sign(self):
         if self.state == 'waiting':
            self.write({'state': 'ready',})
            
    def action_print(self):
        if self.state == 'waiting':
            self.write({'state': 'ready',})
    
    def action_scrap(self):
        if self.state == 'waiting':
            self.write({'state': 'ready',})
            
    def action_unlock(self):
        if self.state == 'waiting':
            self.write({'state': 'ready',})
    
    def action_cancel(self):
        if self.state == 'waiting':
            self.write({'state': 'ready',})
            
    def _compute_invoice_count(self):
        for record in self:
            invoice_count = self.env['invoice'].search_count([('name', '=', record.name)])
            record.invoice_count = invoice_count
    
    def _invoice_action_view(self):
        views = [(self.env.ref('jidoka_export.invoice_view_tree').id, 'tree'),
        (self.env.ref('jidoka_export.invoice_view_form').id, 'form')]
        action = {
            'name': _("Invoice of %s" % (self.display_name)),
            'type': 'ir.actions.act_window',
            'res_model': 'invoice',
            'view_mode': 'tree,form',
            # 'views': views,
            'context': {'create': False},
        }
        return action

    def invoice_btn(self):
        action = self._invoice_action_view()
        action['domain'] = [('name','=',self.name)]
        self._compute_invoice_count()  # Memperbarui invoice_count sebelum mengembalikan action
        return action
    
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Could not delete document except in Draft state.'))
        return super().unlink()
    
    def write(self, vals):
        _logger.info('--- write event packing ----')
        _logger.info(vals)
        return super(PackingList, self).write(vals)