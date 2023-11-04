from itertools import groupby

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare


class ScRevisi(models.Model):
    _name = 'sc.revisi'
    _description = 'Sale Confirmation Revisi'
    
    count_mo_search = fields.Integer(string='Hitung', compute='compute_count_mo_search')
    def action_invoice_create(self):
        sale_line_obj = self.env['sale.order.line']
        for revisi in self:
            # Lakukan operasi lain yang diperlukan berdasarkan revisi
            # ...

            # Buat baris faktur untuk sc.revisi
            invoice_line_values = {
                'product_id': revisi.product_id.id,
                'name': revisi.name,
                'quantity': 1,
                'price_unit': revisi.amount,
                # Tambahkan field lain yang diperlukan
            }
            invoice_line = sale_line_obj.create(invoice_line_values)

            # Buat faktur untuk sc.revisi
            invoice_values = {
                'partner_id': revisi.partner_id.id,
                'invoice_line_ids': [(6, 0, [invoice_line.id])],
                # Tambahkan field lain yang diperlukan
            }
            invoice = self.env['account.move'].create(invoice_values)

        return True
    @api.depends('name')
    def compute_count_mo_search(self):
        for record in self:
            record.count_mo_search = record.get_count_mo()

    def get_count_mo(self):
        domain = [('no_ckwi', '=', self.name)]
        mo_count = self.search_count(domain)
        return mo_count
    
    name = fields.Char(string='Name', readonly=True, copy=False, default=lambda self: self._get_sequence_default())

    def _get_sequence_default(self):
        sequence_code = 'sc.revisi.sequence'
        sequence = self.env['ir.sequence'].sudo().next_by_code(sequence_code) or ''
        return sequence.replace('%(range_y)s', str(fields.Date.today().year)).replace('%(range_month)s', str(fields.Date.today().month))
    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()
    
    partner_id = fields.Many2one('res.partner', string='Buyer')
    partner_invoice_id = fields.Many2one('res.partner', string='Invoice Address')
    partner_shipping_id = fields.Many2one('res.partner', string='Customer')
    country_of_deliver = fields.Many2one('res.country', string='Port Of Country')
    buyer_po = fields.Char(string='Buyer PO')
    department_id = fields.Many2one('hr.department', string='Department')
    origin = fields.Char(string='Cust Reference')
    destination_id = fields.Many2one('res.country', string='Destination')
    date_order = fields.Datetime(string='Date Meeting')
    date_o = fields.Datetime(string='Date')
    pricelist_id = fields.Many2one('product.pricelist', string='Currency')
    term_id = fields.Many2one('account.payment.term', string='Terms')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment')
    notes_sale_id = fields.Many2one('res.notes.sale', string='Notes Sale')
    no_ckwi = fields.Char(string='Source Document')
    certification_id = fields.Many2one('res.certification', string='Certification')
    order_line_ids = fields.One2many('sc.revisi.line', 'sc_rev_id', string='Order Line')
    state= fields.Selection([
        ('draft', 'Sale Confirmation Draft'),
        ('sr', 'Sale Confirmation'),
    ], string='Status', readonly=True, tracking=True, default='draft')
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_delivery_count')
    picking_ids = fields.One2many('stock.picking', 'sale_id', string='Transfers')
    invoice_count = fields.Integer(string='Invoice Count', compute='_get_invoiced', readonly=True)
    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)
    mrp_production_count = fields.Integer(
        "Count of MO generated",
        compute='_compute_mrp_production_count',
        groups='mrp.group_mrp_user')
    procurement_group_id = fields.Many2one('procurement.group', 'Procurement Group', copy=False)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    client_order_ref = fields.Char(string='Customer Reference', copy=False)
    note = fields.Text('Terms and conditions')
    fiscal_position_id = fields.Many2one(
        'account.fiscal.position', string='Fiscal Position',
        domain="[('company_id', '=', company_id)]", check_company=True,
        help="Fiscal positions are used to adapt taxes and accounts for particular customers or sales orders/invoices."
        "The default value comes from the customer.")
    team_id = fields.Many2one(
        'crm.team', 'Sales Team',
        change_default=True, default=_get_default_team, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    is_downpayment = fields.Boolean(
        string="Is a down payment", help="Down payments are made when creating invoices from a sales order."
        " They are not copied when duplicating a sales order.")
    currency_id = fields.Many2one('res.currency', 
    string='currency'
    )
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', tracking=4)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', tracking=5)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')



    # catatan = fields.Char(string='catatan', related='name', store=True,)

    def cancel(self):
        self.write({'state' : 'cancel'})

    def done(self):
        self.write({'state' : 'done'})
    
    def draft(self):
        self.write({'state' : 'draft'})
    
    def sr(self):
        self.write({'state' : 'sr'}) 

        # #Invoice
        # vals_invoice = {
        #     'move_type': 'out_invoice', 
        #     'partner_id': self.partner_id.id,
        #     'invoice_date': fields.Date.today(),
        #     'origin': self.name,
        # }

        # move = self.env['account.move'].create(vals_invoice)

        # stock picking
        picking_vals = {
            'partner_id': self.partner_id.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'origin': self.name,
            'group_id': self.env['procurement.group'].create({}).id, 
            'location_id': self.partner_id.property_stock_customer.id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
        }
        picking = self.env['stock.picking'].create(picking_vals)

        vals = {
            'partner_id' : self.partner_id.id,
            'partner_invoice_id' : self.partner_invoice_id.id,
            'partner_shipping_id' : self.partner_shipping_id.id,
            'country_of_deliver' : self.country_of_deliver.id,
            'buyer_po' : self.buyer_po,
            'department_id' : self.department_id.id,
            'origin' : self.origin,
            'destination_id' : self.destination_id.id,
            'date_order' : self.date_order,
            'date_o' : self.date_order,
            'pricelist_id' : self.pricelist_id.id,
            'term_id' : self.term_id.id,
            'payment_term_id' : self.payment_term_id.id,
            'notes_sale_id' : self.notes_sale_id.id,
            'no_ckwi' : self.name,
            'certification_id' : self.certification_id.id,
        }
        new_record = self.env['sc.revisi'].create(vals)

        #mrp Production
        for line in self.order_line_ids:
            bom_id = line.product_id.bom_ids[0].id if line.product_id.bom_ids else False
            move_line_mrp_vals = { 
                'origin': self.name,
                'product_id': line.product_id.id,
                'product_uom_id': line.product_uom.id,
                'bom_id': bom_id,
            }
            self.env['mrp.production'].create(move_line_mrp_vals)


        # #Invoice
        # for line in self.order_line_ids:
        #     move_line_vals = {
        #         'move_id': move.id,
        #         'product_id': line.product_id.id,
        #         'quantity': line.product_uom_qty,
        #         'price_unit': line.william_fob_price,
        #         'account_id' : line.account_id.id
        #     }
        # self.env['account.move.line'].create(move_line_vals)
        # action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        # action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
        # action['res_id'] = move.id

        #stock PIking
        for line in self.order_line_ids:
            move_vals = {
                'name': line.product_id.display_name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'picking_id': picking.id,
                'location_id': self.partner_id.property_stock_customer.id,
                'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            }
            move = self.env['stock.move'].create(move_vals)
            move._action_confirm()
            move._action_assign()

        line_vals = []
        for ol in self.order_line_ids: 
            line_vals.append((0,0,{
                'product_template_id': ol.product_template_id.id,
                'product_id': ol.product_id.id,
                'material_finish_id': ol.material_finish_id.id,
                'finish_id': ol.finish_id.id,
                'sku': ol.sku,
                'request_date': ol.request_date,
                'cont_load': ol.cont_load,
                'product_uom_qty':ol.product_uom_qty,
                'product_uom':ol.product_uom.id,
                'name': ol.name,
                'william_fob_price': ol.william_fob_price,
                'william_set_price': ol.william_set_price,
                'packing_size_p': ol.packing_size_p,
                'packing_size_l': ol.packing_size_l,
                'packing_size_t': ol.packing_size_t,
                'qty_carton': ol.qty_carton,
                'cu_ft': ol.cu_ft,
                'inch_40': ol.inch_40,
                'inch_40_hq': ol.inch_40_hq,
            }))
        new_record.write({'order_line_ids': line_vals})
        return True

    def cek(self):
        vals = {
            # 'name': new_request_no,
            'partner_id' : self.partner_id.id,
            'partner_invoice_id' : self.partner_invoice_id.id,
            'partner_shipping_id' : self.partner_shipping_id.id,
            'country_of_deliver' : self.country_of_deliver.id,
            'buyer_po' : self.buyer_po,
            'department_id' : self.department_id.id,
            'origin' : self.origin,
            'destination_id' : self.destination_id.id,
            'date_order' : self.date_order,
            'date_o' : self.date_order,
            'pricelist_id' : self.pricelist_id.id,
            'term_id' : self.term_id.id,
            'payment_term_id' : self.payment_term_id.id,
            'notes_sale_id' : self.notes_sale_id.id,
            'no_ckwi' : self.name,
            'certification_id' : self.certification_id.id,
        }
        new_record = self.env['sc.revisi'].create(vals)

        line_vals = []
        for ol in self.order_line_ids: 
                line_vals.append((0,0,{
                    'product_template_id': ol.product_template_id.id,
                    'product_id': ol.product_id.id,
                    # 'material_finishing': ol.material_finishing,
                    'material_finish_id': ol.material_finish_id.id,
                    'finish_id': ol.finish_id.id,
                    'sku': ol.sku,
                    'request_date': ol.request_date,
                    'cont_load': ol.cont_load,
                    'product_uom_qty':ol.product_uom_qty,
                    'product_uom':ol.product_uom.id,
                    # 'sku_id': l.sku_id.id,
                    'name': ol.name,
                    'william_fob_price': ol.william_fob_price,
                    'william_set_price': ol.william_set_price,
                    'packing_size_p': ol.packing_size_p,
                    'packing_size_l': ol.packing_size_l,
                    'packing_size_t': ol.packing_size_t,
                    'qty_carton': ol.qty_carton,
                    'cu_ft': ol.cu_ft,
                    'inch_40': ol.inch_40,
                    'inch_40_hq': ol.inch_40_hq,
                 }))
        new_record.write({'order_line_ids': line_vals})
    
    def action_sale_mo(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale MO',
            'view_mode': 'tree,form',
            'res_model': 'sc.revisi',
            'res_id':self.name,
            'domain': [('no_ckwi', '=', self.name)],
            'context':{
                'default_document_type': 'manufacture_order',}
        }
    
    def action_view_delivery(self):
        # pickings = self.mapped('picking_ids')
        # picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
        # if picking_id:
        #     picking_id = picking_id[0]
        # elif pickings:
        #     picking_id = pickings[0]

        context = {
            'default_partner_id': self.partner_id.id,
            # 'default_picking_type_id': picking_id.picking_type_id.id if picking_id else False,
            'default_origin': self.name,
            # 'default_group_id': picking_id.group_id.id if picking_id else False,
        }

        domain = []
        if self.name:
            domain = [('origin', '=', self.name)]

        return {
            'type': 'ir.actions.act_window',
            'name': 'Delivery',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'res_id': self.name,
            'domain': domain,
            'context': context,
        }

    @api.depends('picking_ids')
    def _compute_delivery_count(self):
        for order in self:
            new_picking_ids = self.env['stock.picking'].search([('origin', '=', order.name)])
            order.delivery_count = len(new_picking_ids)

    def action_view_invoice(self):
        # invoices = self.mapped('invoice_ids')
        # action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        # if len(invoices) > 1:
        #     action['domain'] = [('id', 'in', invoices.ids)]
        # elif len(invoices) == 1:
        #     form_view = [(self.env.ref('account.view_move_form').id, 'form')]
        #     if 'views' in action:
        #         action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        #     else:
        #         action['views'] = form_view
        #     action['res_id'] = invoices.id
        # else:
        #     action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.partner_id.id,
                'default_partner_shipping_id': self.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.name,
            })
        # action['context'] = context

        domain = []
        if self.name:
            domain = [('origin', '=', self.name)]

        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'res_id': self.name,
            'domain': domain,
            'context': context,
        }
    
    @api.depends('order_line_ids')
    def _get_invoiced(self):
        for order in self:
            new_invoice_ids = self.env['account.move'].search([('origin', '=', order.name)])
            order.invoice_count = len(new_invoice_ids)


    def action_view_mrp_production(self):
        context = {
            'default_partner_id': self.partner_id.id,
            'default_origin': self.name,
        }
        domain = []
        if self.name:
            domain = [('origin', '=', self.name)]

        return {
            'type': 'ir.actions.act_window',
            'name': 'Manufacturing',
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'res_id':self.name,
            'domain': domain,
            'context': context,
        }
    
    @api.depends('order_line')
    def _compute_mrp_production_count(self):
        for order in self:
            mrp_productions = self.env['mrp.production'].search([('origin', '=', order.name)])
            order.mrp_production_count = len(mrp_productions)

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'move_type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            # 'campaign_id': self.campaign_id.id,
            # 'medium_id': self.medium_id.id,
            # 'source_id': self.source_id.id,
            # 'user_id': self.user_id.id,
            # 'invoice_user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(self.partner_invoice_id.id)).id,
            'partner_bank_id': self.company_id.partner_id.bank_ids.filtered(lambda bank: bank.company_id.id in (self.company_id.id, False))[:1].id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            # 'payment_reference': self.reference,
            # 'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
        }
        return invoice_vals
    
    def _get_invoice_grouping_keys(self):
        return ['company_id', 'partner_id', 'currency_id']


    def create_invoice(self):
        vals_invoice = {
            'move_type': 'out_invoice', 
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
            'origin': self.name,
        }
        move = self.env['account.move'].create(vals_invoice)
        
        for line in self.order_line_ids:
            move_line_vals = {
                'move_id': move.id,
                'product_id': line.product_id.id,
                'quantity': line.product_uom_qty,
                'price_unit': line.william_fob_price,
                'account_id' : line.account_id.id
            }
            self.env['account.move.line'].create(move_line_vals)
        
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
        action['res_id'] = move.id
        
        return action
    
    def create_invoice_revisi(self):
         return {
            'type': 'ir.actions.act_window',
            'name': 'Revisi',
            'view_mode': 'form',
            'res_model': 'sale.advance.payment.inv.revisi',
            'target': 'new',
            }
    
    def _get_invoiceable_lines(self, final=False):
        """Return the invoiceable lines for order `self`."""
        down_payment_line_ids = []
        invoiceable_line_ids = []
        pending_section = None
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        for line in self.order_line:
            if line.display_type == 'line_section':
                # Only invoice the section if one of its lines is invoiceable
                pending_section = line
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue
            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                if line.is_downpayment:
                    # Keep down payment lines separately, to put them together
                    # at the end of the invoice, in a specific dedicated section.
                    down_payment_line_ids.append(line.id)
                    continue
                if pending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = None
                invoiceable_line_ids.append(line.id)

        return self.env['sc.revisi.line'].browse(invoiceable_line_ids + down_payment_line_ids)

    def _create_invoices(self, grouped=False, final=False, date=None):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        # 1) Create invoices.
        invoice_vals_list = []
        invoice_item_sequence = 0 # Incremental sequencing to keep the lines order on the invoice.
        for order in self:
            order = order.with_company(order.company_id)
            current_section_vals = None
            down_payments = order.env['sc.revisi.line']

            invoice_vals = order._prepare_invoice()
            invoiceable_lines = order._get_invoiceable_lines(final)

            if not any(not line.display_type for line in invoiceable_lines):
                continue

            invoice_line_vals = []
            down_payment_section_added = False
            for line in invoiceable_lines:
                if not down_payment_section_added and line.is_downpayment:
                    # Create a dedicated section for the down payments
                    # (put at the end of the invoiceable_lines)
                    invoice_line_vals.append(
                        (0, 0, order._prepare_down_payment_section_line(
                            sequence=invoice_item_sequence,
                        )),
                    )
                    down_payment_section_added = True
                    invoice_item_sequence += 1
                invoice_line_vals.append(
                    (0, 0, line._prepare_invoice_line(
                        sequence=invoice_item_sequence,
                    )),
                )
                invoice_item_sequence += 1

            invoice_vals['invoice_line_ids'] += invoice_line_vals
            invoice_vals_list.append(invoice_vals)

        # if not invoice_vals_list:
        #     raise self._nothing_to_invoice_error()

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            invoice_vals_list = sorted(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys])
            for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.

        # As part of the invoice creation, we make sure the sequence of multiple SO do not interfere
        # in a single invoice. Example:
        # SO 1:
        # - Section A (sequence: 10)
        # - Product A (sequence: 11)
        # SO 2:
        # - Section B (sequence: 10)
        # - Product B (sequence: 11)
        #
        # If SO 1 & 2 are grouped in the same invoice, the result will be:
        # - Section A (sequence: 10)
        # - Section B (sequence: 10)
        # - Product A (sequence: 11)
        # - Product B (sequence: 11)
        #
        # Resequencing should be safe, however we resequence only if there are less invoices than
        # orders, meaning a grouping might have been done. This could also mean that only a part
        # of the selected SO are invoiceable, but resequencing in this case shouldn't be an issue.
        if len(invoice_vals_list) < len(self):
            SaleOrderLine = self.env['sc.revisi.line']
            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice['invoice_line_ids']:
                    line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
                    sequence += 1

        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        return moves
    
    @api.onchange('fiscal_position_id')
    def _compute_tax_id(self):
        """
        Trigger the recompute of the taxes if the fiscal position is changed on the SO.
        """
        for order in self:
            order.order_line._compute_tax_id()

    @api.onchange('partner_shipping_id', 'partner_id', 'company_id')
    def onchange_partner_shipping_id(self):
        """
        Trigger the change of fiscal position when the shipping address is modified.
        """
        self.fiscal_position_id = self.env['account.fiscal.position'].with_company(self.company_id).get_fiscal_position(self.partner_id.id, self.partner_shipping_id.id)
        return {}

   
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        - Sales Team
        """
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'fiscal_position_id': False,
            })
            return

        self = self.with_company(self.company_id)

        addr = self.partner_id.address_get(['delivery', 'invoice'])
        partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
        }
        user_id = partner_user.id
        if not self.env.context.get('not_self_saleperson'):
            user_id = user_id or self.env.context.get('default_user_id', self.env.uid)
        if user_id and self.user_id.id != user_id:
            values['user_id'] = user_id

        if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms') and self.env.company.invoice_terms:
            values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
        if not self.env.context.get('not_self_saleperson') or not self.team_id:
            values['team_id'] = self.env['crm.team'].with_context(
                default_team_id=self.partner_id.team_id.id
            )._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)], user_id=user_id)
        self.update(values)

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id:
            self.team_id = self.env['crm.team'].with_context(
                default_team_id=self.team_id.id
            )._get_default_team_id(user_id=self.user_id.id)

    @api.depends('order_line_ids.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    

    # def get_count_mo(self):
    #     domain = [('catatan', '=', self.catatan)]
    #     mo_count = self.search_count(domain)
    #     return mo_count

class ScRevisiLine(models.Model):
    _name = 'sc.revisi.line'
    _description = 'Sale Confirmation Revisi Line'

    sc_rev_id = fields.Many2one('sc.revisi', string='SC REVISI')
    product_id = fields.Many2one('product.product', string='Product Variant')
    product_template_id = fields.Many2one('product.template', string='Product')
    name = fields.Char(string='Description')
    material_finish_id = fields.Many2one('design.material', string='Material')
    finish_id = fields.Many2one('design.finish', string='Finish')
    sku = fields.Char(string='SKU No.')
    request_date = fields.Date(string='Ship Date')
    no_mo = fields.Char(string='No. MO')
    cont_load = fields.Char(string='Cont. Load')
    product_uom_qty = fields.Float(string='Quantity')
    william_fob_price = fields.Float(string='Single Price')
    william_set_price = fields.Float(string='Set Price')
    tax_id = fields.Many2many('account.tax', string='Taxes')
    packing_size_p = fields.Float(string='Packing Size Panjang')
    packing_size_l = fields.Float(string='Packing Size Lebar')
    packing_size_t = fields.Float(string='Packing Size Tinggi')
    qty_carton = fields.Float(string='QTY / CTN')
    cu_ft = fields.Float(string='CU FT')
    inch_40 = fields.Float()
    inch_40_hq = fields.Float()
    product_uom = fields.Many2one('uom.uom', string='UoM')
    categ_id = fields.Many2one('product.category', string='categ', related='product_id.categ_id')
    account_id = fields.Many2one('account.account', string='account', related='product_id.categ_id.property_account_income_categ_id')
    is_downpayment = fields.Boolean(
        string="Is a down payment", help="Down payments are made when creating invoices from a sales order."
        " They are not copied when duplicating a sales order.")
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
        ], string='Invoice Status', compute='_compute_invoice_status', store=True, readonly=True, default='no')
    state = fields.Selection(
        related='sc_rev_id.state', string='Order Status', readonly=True, copy=False, store=True, default='draft')
    
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    currency_id = fields.Many2one(related='sc_rev_id.currency_id', depends=['sc_rev_id.currency_id'], store=True, string='Currency', readonly=True)
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag', string='Analytic Tags',
        compute='_compute_analytic_tag_ids', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    analytic_line_ids = fields.One2many('account.analytic.line', 'so_line', string="Analytic lines")
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    company_id = fields.Many2one(related='sc_rev_id.company_id', string='Company', store=True, readonly=True, index=True)



    @api.depends('product_id', 'sc_rev_id.date_order', 'sc_rev_id.partner_id')
    def _compute_analytic_tag_ids(self):
        for line in self:
            if not line.display_type and line.state == 'draft':
                default_analytic_account = line.env['account.analytic.default'].sudo().account_get(
                    product_id=line.product_id.id,
                    partner_id=line.sc_rev_id.partner_id.id,
                    user_id=self.env.uid,
                    date=line.sc_rev_id.date_order,
                    company_id=line.company_id.id,
                )
                line.analytic_tag_ids = default_analytic_account.analytic_tag_ids


    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.sc_rev_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.sc_rev_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.depends('state')
    def _compute_product_uom_readonly(self):
        for line in self:
            line.product_uom_readonly = line.state in ['sale', 'done', 'cancel']
    


    
    @api.depends('state', 'product_uom_qty')
    def _compute_invoice_status(self):
        """
        Compute the invoice status of a SO line. Possible statuses:
        - no: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also hte default value if the conditions of no other status is met.
        - to invoice: we refer to the quantity to invoice of the line. Refer to method
          `_get_to_invoice_qty()` for more information on how this quantity is calculated.
        - upselling: this is possible only for a product invoiced on ordered quantities for which
          we delivered more than expected. The could arise if, for example, a project took more
          time than expected but we decided not to invoice the extra cost to the client. This
          occurs onyl in state 'sale', so that when a SO is set to done, the upselling opportunity
          is removed from the list.
        - invoiced: the quantity invoiced is larger or equal to the quantity ordered.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if line.state not in ('sale', 'done'):
                line.invoice_status = 'no'
            elif line.is_downpayment and line.untaxed_amount_to_invoice == 0:
                line.invoice_status = 'invoiced'
            elif not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                line.invoice_status = 'to invoice'
            elif line.state == 'sale' and line.product_id.invoice_policy == 'order' and\
                    line.product_uom_qty >= 0.0 and\
                    float_compare(line.qty_delivered, line.product_uom_qty, precision_digits=precision) == 1:
                line.invoice_status = 'upselling'
            elif float_compare(line.qty_invoiced, line.product_uom_qty, precision_digits=precision) >= 0:
                line.invoice_status = 'invoiced'
            else:
                line.invoice_status = 'no'

