# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_is_zero
from itertools import groupby
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang, format_amount
import logging
_logger = logging.getLogger(__name__)


class GradingSummary1(models.Model):
    _name='grading.summary1.line'
    _description='Operations Summary'
    grading_summary_id = fields.Many2one('grading.summary', string='Grading Summary')
    grading_summary1_id = fields.Many2one('grading.summary', string='Grading Summary')
    name = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product', string='Product', store=True)
    product_name = fields.Char('Product Name', related='grading_summary1_id.product_name',
        store=True)
    wood_class_id = fields.Many2one('res.wood.class', string='Wood Class')
    qty_pcs = fields.Float('PCS',  
        related='grading_summary1_id.qty_pcs',
        store=True )

    # qty_kubikasi = fields.Float('M3',  
    #     related='grading_summary1_id.qty_kubikasi',
    #     store=True )
    # def tes(self):
    #     import pdb;pdb.set_trace()

    #     action = self.id
    #     return action
        


    # @api.depends('product_name')
    # def _compute_product_name(self):
    #     for record in self:
    #         record.product_name = self.env['grading.summary.line'].search_count([('product_id','=', self.product_id)])

    # @api.depends('qty_pcs')
    # def _compute_qty_pcs(self):
    #     for r in self:
    #         r.qty_pcs = self.env['grading.summary.line'].search_count([('qty_pcs','=', self.qty_pcs)])
    
    
    qty_kubikasi = fields.Float('M3', digits='Product Unit of Measure',  
        related='grading_summary1_id.qty_kubikasi',
        store=True )
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_unit = fields.Float('Unit Price', digits='Product Price', 
                 related='grading_summary1_id.price_unit',
                 store=True)
    price_subtotal = fields.Monetary(related='grading_summary1_id.price_subtotal', string='Subtotal', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

    currency_id = fields.Many2one(related='grading_summary1_id.currency_id', store=True, string='Currency', readonly=True)
    company_id = fields.Many2one(related='grading_summary1_id.company_id', string='Company', index=True)
    move_id = fields.Many2one('stock.move', string='Move')
    master_hasil = fields.Selection([
        ('bagus', 'Bagus'),
        ('afkir', 'Afkir'),
        ('triming', 'Triming'),
        ('grade_a', 'Grade A'),
        ('grade_b', 'Grade B')
    ], string='Grading')
    account_analytic_id = fields.Many2one('account.analytic.account', store=True, string='Analytic Account', compute='_compute_account_analytic_id', readonly=False)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', store=True, string='Analytic Tags', compute='_compute_analytic_tag_ids', readonly=False)
    invoice_lines = fields.One2many('account.move.line', 'grading_summary_line_id', string="Bill Lines", readonly=True, copy=False)

    # Replace by invoiced Qty
    qty_invoiced = fields.Float(compute='_compute_qty_invoiced', string="Billed Qty", digits='Product Unit of Measure', store=True)
    qty_to_invoice = fields.Float(compute='_compute_qty_invoiced', string='To Invoice Quantity', store=True, readonly=True,
                                  digits='Product Unit of Measure')
    date_order = fields.Date(related='grading_summary1_id.date', string='Order Date', readonly=True)   

    @api.depends(
        'grading_summary_line_ids',
        'grading_summary_line_ids.qty_pcs',
        'grading_summary_line_ids.qty_kubikasi'
        )
    def _compute_match_fields(self):
        for rec in self:
            vals_line = [(5, 0, 0)]
            # [id, vals]
            list_to_add = {}
            for ol in self.grading_summary_line_ids.sorted(key=lambda l: l.product_id.name):
                if ol.product_id.id not in list_to_add.keys():
                    list_to_add[ol.product_id.id] = {
                        'product_id': ol.product_id.id,
                        'product_name': ol.product_name,
                        'qty_pcs': ol.qty_pcs,
                        'qty_kubikasi': ol.qty_kubikasi,
                        'price_unit': ol.price_unit,
                        'price_subtotal': ol.price_subtotal,

                    }
                else:
                    list_to_add[ol.product_id.id]['qty_pcs'] = list_to_add[ol.product_id.id]['qty_pcs'] + ol.qty_pcs
                    list_to_add[ol.product_id.id]['qty_kubikasi'] = list_to_add[ol.product_id.id]['qty_kubikasi'] + ol.qty_kubikasi
                    list_to_add[ol.product_id.id]['price_subtotal'] = list_to_add[ol.product_id.id]['price_subtotal'] + ol.price_subtotal
                    # TODO
            if list_to_add:
                for k, v in list_to_add.items():
                    vals_line.append((0, 0, v))
            rec.grading_summary_line1_ids = vals_line

                
    @api.depends('grading_summary_line_ids')
    def _compute_product_id(self):
        for r in self:
            grading_sum = self.grading_summary_line_ids
            r.product_id = grading_sum.mapped('product_id')

    @api.depends('grading_summary_line_ids')
    def _compute_product_name(self):
        for r in self:
            grading_sum = self.grading_summary_line_ids
            if grading_sum and grading_sum.mapped('product_name'):
                r.product_name = grading_sum.mapped('product_name')[0]
            else:
                r.product_name = False

    @api.depends('grading_summary_line_ids')
    def _compute_qty_pcs(self):
        for r in self:
            grading_sum = self.grading_summary_line_ids
            r.qty_pcs = sum(grading_sum.mapped('qty_pcs'))

    @api.depends('grading_summary_line_ids')
    def _compute_qty_kubikasi(self):
        for r in self:
            grading_sum = self.grading_summary_line_ids
            r.qty_kubikasi = sum(grading_sum.mapped('qty_kubikasi'))
            
    @api.depends('grading_summary_line_ids')
    def _compute_price_unit(self):
        # for r in self:
        #     grading_sum = self.grading_summary_line_ids
        #     r.price_unit = grading_sum.mapped('price_unit')[0]
        for r in self:
            grading_sum = self.grading_summary_line_ids
            if grading_sum and grading_sum.mapped('price_unit'):
                r.price_unit = grading_sum.mapped('price_unit')[0]
            else:
                r.price_unit = False

            
    @api.depends('grading_summary_line_ids')
    def _compute_price_subtotal(self):
        for r in self:
            grading_sum = self.grading_summary_line_ids
            r.price_subtotal = sum(grading_sum.mapped('price_subtotal'))

    def action_validate_grading(self):
        # import pdb;pdb.set_trace()
        self.state = 'done'

    @api.depends('state')
    def _compute_css(self):
        for record in self:
            # You can modify the below below condition
            if record.state != 'draft':
                record.is_closed = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.is_closed = False
    @api.depends('qty_kubikasi', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['qty_kubikasi'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
    
    @api.depends('product_id', 'date_order')
    def _compute_account_analytic_id(self):
        for rec in self:
            if not rec.account_analytic_id:
                default_analytic_account = rec.env['account.analytic.default'].sudo().account_get(
                    product_id=rec.product_id.id,
                    partner_id=rec.grading_summary_id.partner_id.id,
                    user_id=rec.env.uid,
                    date=rec.date_order,
                    company_id=rec.company_id.id,
                )
                rec.account_analytic_id = default_analytic_account.analytic_id

    @api.depends('product_id', 'date_order')
    def _compute_analytic_tag_ids(self):
        for rec in self:
            if not rec.analytic_tag_ids:
                default_analytic_account = rec.env['account.analytic.default'].sudo().account_get(
                    product_id=rec.product_id.id,
                    partner_id=rec.grading_summary_id.partner_id.id,
                    user_id=rec.env.uid,
                    date=rec.date_order,
                    company_id=rec.company_id.id,
                )
                rec.analytic_tag_ids = default_analytic_account.analytic_tag_ids
    
    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity')
    def _compute_qty_invoiced(self):
        for line in self:
            # compute qty_invoiced
            qty = 0.0
            for inv_line in line.invoice_lines:
                if inv_line.move_id.state not in ['cancel']:
                    if inv_line.move_id.move_type == 'in_invoice':
                        qty += inv_line.product_uom_id._compute_quantity(inv_line.quantity, line.product_uom)
                    elif inv_line.move_id.move_type == 'in_refund':
                        qty -= inv_line.product_uom_id._compute_quantity(inv_line.quantity, line.product_uom)
            line.qty_invoiced = qty

            # compute qty_to_invoice
            line.qty_to_invoice = line.qty_kubikasi - line.qty_invoiced

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        aml_currency = move and move.currency_id or self.currency_id
        date = move and move.date or fields.Date.today()
        res = {
            # 'display_type': self.display_type,
            'sequence': self.sequence,
            'name': '%s: %s' % (self.grading_summary_id.name, self.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'price_unit': self.currency_id._convert(self.price_unit, aml_currency, self.company_id, date, round=False),
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'analytic_account_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'grading_summary_line_id': self.id,
        }
        if not move:
            return res

        if self.currency_id == move.company_id.currency_id:
            currency = False
        else:
            currency = move.currency_id

        res.update({
            'move_id': move.id,
            'currency_id': currency and currency.id or False,
            'date_maturity': move.invoice_date_due,
            'partner_id': move.partner_id.id,
        })
        return res
    
    def _compute_tax_id(self):
        for line in self:
            line = line.with_company(line.company_id)
            fpos = line.grading_summary_id.fiscal_position_id or line.grading_summary_id.fiscal_position_id.get_fiscal_position(line.grading_summary_id.partner_id.id)
            # filter taxes by company
            taxes = line.product_id.supplier_taxes_id.filtered(lambda r: r.company_id == line.env.company)
            line.taxes_id = fpos.map_tax(taxes, line.product_id, line.grading_summary_id.partner_id)

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.grading_summary_id.currency_id,
            'qty_kubikasi': self.qty_kubikasi,
            'product': self.product_id,
            'partner': self.grading_summary_id.partner_id,
        }
    
class GradingSummary(models.Model):
    _name = 'grading.summary'
    _description = 'Grading Summary'
    
    name = fields.Char('Name',default='New')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], default="draft")
    partner_id = fields.Many2one('res.partner', string='Vendor', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    partner_ref = fields.Char('Vendor Reference', copy=False,
        help="Reference of the sales order or bid sent by the vendor. "
             "It's used to do the matching when you receive the "
             "products as this reference is usually written on the "
             "delivery order sent by your vendor.")
    commence = fields.Date('Commence',required=True)
    species_id = fields.Many2one('jidoka.species', string='Species')
    species = fields.Selection([
        ('log', 'Log')
    ], string='Species')
    shipping_marks = fields.Char('Shipping Marks')
    date = fields.Date('Date',required=True)
    our_code = fields.Char('Our Code')
    complete_date = fields.Date('Complete',required=True)
    grade = fields.Char('Grade')
    end_tally = fields.Date('End Tally',required=True)
    purchase_id = fields.Many2one('purchase.order', string='Po NO')
    truck = fields.Char('Truck')
    turun = fields.Char('Turun')
    nota = fields.Char('SKSHHK / Nota')
    dkhp = fields.Char('DKHP')
    certification_id = fields.Many2one('res.certification', string='Sertifikasi')

    information = fields.Text('Information', strip_style=True)
    equal_symbol = fields.Text('Equal Symbol', strip_style=True)
   
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', tracking=True)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    picking_id = fields.Many2one('stock.picking', string='Picking')
    invoice_count = fields.Integer(compute="_compute_invoice", string='Bill Count', copy=False, default=0, store=True)
    invoice_ids = fields.Many2many('account.move', compute="_compute_invoice", string='Bills', copy=False, store=True)
    invoice_status = fields.Selection([
        ('no', 'Nothing to Bill'),
        ('to invoice', 'Waiting Bills'),
        ('invoiced', 'Fully Billed'),
    ], string='Billing Status', compute='_get_invoiced', store=True, readonly=True, copy=False, default='no')
    user_id = fields.Many2one(
        'res.users', string='Purchase Representative', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    incoterm_id = fields.Many2one('account.incoterms', 'Incoterm', states={'done': [('readonly', True)]}, help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")
    is_closed = fields.Html(string='Done', sanitize=False, compute='_compute_css', store=False)

    grading_summary_line_ids = fields.One2many('grading.summary.line', 'grading_summary_id', string='Grading Summary Line')
    
    # TODO compute this field
    grading_summary_line1_ids = fields.One2many('grading.summary1.line', 'grading_summary1_id', string='Grading Summary Line', 
        compute='_compute_match_fields' , store=True )
    product_id = fields.Many2one('product.product', string='Product', store=True
            # ,compute='_compute_product_id',
            )
    product_name = fields.Char('product_name', 
        compute='_compute_product_name', store=True )

    qty_pcs = fields.Float('qty_pcs', 
        compute='_compute_qty_pcs', store=True )
    
   
    qty_kubikasi = fields.Float('qty_kubikasi', 
        compute='_compute_qty_kubikasi', store=True )

    price_unit = fields.Float('price_unit', 
            compute='_compute_price_unit', store=True )

    price_subtotal = fields.Monetary('price_subtotal', 
            compute='_compute_price_subtotal', store=True )
    # amount_fee = fields.Float('Amount Fee',store=True, readonly=True, compute='_amount_all')

    # @api.depends('grading_summary_line_ids')
    # def _compute_grading_summary_line1_ids(self):
    #     for r in self:
    #         grading_sum = self.grading_summary_line_ids
    #         r.grading_summary_line1_ids = grading_sum.mapped('grading_summary_line_ids')
    #     if r.grading_summary_line_ids and r.grading_summary_line1_ids:
    #             new_var = r.grading_summary_line1_ids
    #             r.match_fields = r.grading_summary_line_ids == new_var
    @api.depends(
        'grading_summary_line_ids',
        'grading_summary_line_ids.qty_pcs',
        'grading_summary_line_ids.qty_kubikasi'
        )
    def _compute_match_fields(self):
        for rec in self:
            vals_line = [(5, 0, 0)]
            # [id, vals]
            list_to_add = {}
            # for ol in self.grading_summary_line_ids.sorted(key=lambda l: l.product_id.name):
            for ol in self.grading_summary_line_ids.sorted(key=lambda l: (l.product_id.name or '')):
                if ol.product_id.id not in list_to_add.keys():
                    list_to_add[ol.product_id.id] = {
                        'product_id': ol.product_id.id,
                        'product_name': ol.product_name,
                        'qty_pcs': ol.qty_pcs,
                        'qty_kubikasi': ol.qty_kubikasi,
                        'price_unit': ol.price_unit,
                        'price_subtotal': ol.price_subtotal,

                    }
                else:
                    list_to_add[ol.product_id.id]['qty_pcs'] = list_to_add[ol.product_id.id]['qty_pcs'] + ol.qty_pcs
                    list_to_add[ol.product_id.id]['qty_kubikasi'] = list_to_add[ol.product_id.id]['qty_kubikasi'] + ol.qty_kubikasi
                    list_to_add[ol.product_id.id]['price_subtotal'] = list_to_add[ol.product_id.id]['price_subtotal'] + ol.price_subtotal
                    # TODO
            if list_to_add:
                # for v in list_to_add.items():
                for v in list_to_add.values():

                    vals_line.append((0, 0, v))
            rec.grading_summary_line1_ids = vals_line

                
    @api.depends('grading_summary_line_ids')
    def _compute_product_id(self):
        for r in self:
            grading_sum = self.grading_summary_line_ids
            r.product_id = grading_sum.mapped('product_id')

    @api.depends('grading_summary_line_ids')
    def _compute_product_name(self):
        for r in self:
            grading_sum = self.grading_summary_line_ids
            if grading_sum and grading_sum.mapped('product_name'):
                r.product_name = grading_sum.mapped('product_name')[0]
            else:
                r.product_name = False

    @api.depends('grading_summary_line_ids')
    def _compute_qty_pcs(self):
        for r in self:
            grading_sum = self.grading_summary_line_ids
            r.qty_pcs = sum(grading_sum.mapped('qty_pcs'))

    @api.depends('grading_summary_line_ids')
    def _compute_qty_kubikasi(self):
        for r in self:
            grading_sum = self.grading_summary_line_ids
            r.qty_kubikasi = sum(grading_sum.mapped('qty_kubikasi'))
            
    @api.depends('grading_summary_line_ids')
    def _compute_price_unit(self):
        # for r in self:
        #     grading_sum = self.grading_summary_line_ids
        #     r.price_unit = grading_sum.mapped('price_unit')[0]
        for r in self:
            grading_sum = self.grading_summary_line_ids
            if grading_sum and grading_sum.mapped('price_unit'):
                r.price_unit = grading_sum.mapped('price_unit')[0]
            else:
                r.price_unit = False

            
    @api.depends('grading_summary_line_ids')
    def _compute_price_subtotal(self):
        for r in self:
            grading_sum = self.grading_summary_line_ids
            r.price_subtotal = sum(grading_sum.mapped('price_subtotal'))

    def action_validate_grading(self):
        # import pdb;pdb.set_trace()
        # self.state = 'done'
        self.write({'state':'done'})

    @api.depends('state')
    def _compute_css(self):
        for record in self:
            # You can modify the below below condition
            if record.state != 'draft':
                record.is_closed = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.is_closed = False

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        # Ensures all properties and fiscal positions
        # are taken with the company of the order
        # if not defined, with_company doesn't change anything.
        self = self.with_company(self.company_id)
        if self.name and self.partner_id and self.name != 'New':
            split_name = self.name.split('/')
            split_name[1] = self.partner_id.supplier_code_id.code
            self.name = ('/').join(split_name)
        if not self.partner_id:
            self.fiscal_position_id = False
            self.currency_id = self.env.company.currency_id.id
        else:
            self.fiscal_position_id = self.env['account.fiscal.position'].get_fiscal_position(self.partner_id.id)
            self.payment_term_id = self.partner_id.property_supplier_payment_term_id.id
            self.currency_id = self.partner_id.property_purchase_currency_id.id or self.env.company.currency_id.id
        return {}
    
    @api.onchange('fiscal_position_id', 'company_id')
    def _compute_tax_id(self):
        """
        Trigger the recompute of the taxes if the fiscal position is changed on the PO.
        """
        self.grading_summary_line_ids._compute_tax_id()

    @api.depends('grading_summary_line_ids.invoice_lines.move_id')
    def _compute_invoice(self):
        for order in self:
            invoices = order.mapped('grading_summary_line_ids.invoice_lines.move_id')
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            code = False
            if vals.get('partner_id'):
                partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
                if partner_id:
                    code = partner_id.supplier_code_id.code
            seq = self.env['ir.sequence'].next_by_code('seq.grading.summary.ckwi') or '/'
            name = 'New'
            if code:
                split_name = seq.split('/')
                split_name[1] = code
                name = ('/').join(split_name)
            vals['name'] = name
        return super().create(vals)

    # @api.depends('grading_summary_line_ids.price_subtotal')
    # def _amount_all(self):
    #     for rec in self:
    #         rec.amount_total = sum([x.price_subtotal for x in rec.grading_summary_line_ids])
    
    @api.depends('grading_summary_line_ids.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            # amount_untaxed = amount_tax = amount_fee =  0.0
            for line in order.grading_summary_line_ids:
                line._compute_amount()
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                # amount_fee += line.price_fee_subtotal
            currency = order.currency_id or order.partner_id.property_purchase_currency_id or self.env.company.currency_id
            order.update({
                'amount_untaxed': currency.round(amount_untaxed),
                'amount_tax': currency.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
                # 'amount_total': amount_untaxed + amount_tax + amount_fee,
                # 'amount_fee': currency.round(amount_fee),
            })

    @api.depends('grading_summary_line_ids.qty_to_invoice')
    def _get_invoiced(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            order.invoice_status = 'no'
            if any(
                not float_is_zero(line.qty_to_invoice, precision_digits=precision)
                for line in order.grading_summary_line_ids
            ):
                order.invoice_status = 'to invoice'
            elif (
                all(
                    float_is_zero(line.qty_to_invoice, precision_digits=precision)
                    for line in order.grading_summary_line_ids
                )
                and order.invoice_ids
            ):
                order.invoice_status = 'invoiced'
            else:
                order.invoice_status = 'no'

    def action_create_invoice(self):
        # import pdb;pdb.set_trace()
        """Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # GRADING SUMMARY
        # 1) Prepare invoice vals and clean-up the section lines
        invoice_vals_list = []
        sequence = 10
        for order in self:
            if order.invoice_status != 'to invoice':
                continue

            order = order.with_company(order.company_id)
            pending_section = None
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
            for line in order.grading_summary_line_ids:
                # if line.display_type == 'line_section':
                #     pending_section = line
                #     continue
                if not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    if pending_section:
                        line_vals = pending_section._prepare_account_move_line()
                        line_vals.update({'sequence': sequence})
                        invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                        sequence += 1
                        pending_section = None
                    line_vals = line._prepare_account_move_line()
                    line_vals.update({'sequence': sequence})
                    invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                    sequence += 1
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        # 2) group by (company_id, partner_id, currency_id) for batch creation
        new_invoice_vals_list = []
        for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (x.get('company_id'), x.get('partner_id'), x.get('currency_id'))):
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
        # _logger.info('====================INVOICE VAL LIST====================')
        # _logger.info('invoice_vals_list: %s', invoice_vals_list)

        # 3')

        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        moves.filtered(lambda m: m.currency_id.round(m.amount_total) < 0).action_switch_invoice_into_refund_credit_note()

        return self.action_view_invoice(moves)

    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'in_invoice')
        journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        partner_invoice_id = self.partner_id.address_get(['invoice'])['invoice']
        partner_bank_id = self.partner_id.commercial_partner_id.bank_ids.filtered_domain(['|', ('company_id', '=', False), ('company_id', '=', self.company_id.id)])[:1]
        nama_po = self.purchase_id.name
        invoice_vals = {
            'ref': self.partner_ref or '',
            'move_type': move_type,
            # 'narration': self.notes,
            'currency_id': self.currency_id.id,
            'invoice_user_id': self.user_id and self.user_id.id or self.env.user.id,
            'partner_id': partner_invoice_id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(partner_invoice_id)).id,
            'payment_reference': self.partner_ref or '',
            'partner_bank_id': partner_bank_id.id,
            # 'invoice_origin': self.name,
            'invoice_origin': nama_po,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            # 'stock_move_id': self.grading_summary_line_ids.move_id.id #stock_move_id masuk ke account.move
        }
        return invoice_vals

    def action_view_invoice(self, invoices=False):
        """This function returns an action that display existing vendor bills of
        given purchase order ids. When only one found, show the vendor bill
        immediately.
        """
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the purchase order, we read them in sudo to fill the
            # cache.
            self.sudo()._read(['invoice_ids'])
            invoices = self.invoice_ids

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

class GradingSummaryLine(models.Model):
    _name = 'grading.summary.line'
    _description = 'Grading Summary Line'
    
    grading_summary_id = fields.Many2one('grading.summary', string='Grading Summary')
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product', string='Product')
    product_name = fields.Char('Product Name')
    wood_class_id = fields.Many2one('res.wood.class', string='Wood Class')
    qty_pcs = fields.Float('PCS', default=0.0)
    qty_kubikasi = fields.Float('M3', digits='Product Unit of Measure', default=0.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_unit = fields.Float('Unit Price', digits='Product Price', default=0.0)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

    currency_id = fields.Many2one(related='grading_summary_id.currency_id', store=True, string='Currency', readonly=True)
    company_id = fields.Many2one(related='grading_summary_id.company_id', string='Company', index=True)
    move_id = fields.Many2one('stock.move', string='Move')
    master_hasil = fields.Selection([
        ('bagus', 'Bagus'),
        ('afkir', 'Afkir'),
        ('triming', 'Triming'),
        ('grade_a', 'Grade A'),
        ('grade_b', 'Grade B')
    ], string='Grading')
    account_analytic_id = fields.Many2one('account.analytic.account', store=True, string='Analytic Account', compute='_compute_account_analytic_id', readonly=False)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', store=True, string='Analytic Tags', compute='_compute_analytic_tag_ids', readonly=False)
    invoice_lines = fields.One2many('account.move.line', 'grading_summary_line_id', string="Bill Lines", readonly=True, copy=False)

    # desc = fields.Text(string='Description', required=True)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    
    # Replace by invoiced Qty
    qty_invoiced = fields.Float(compute='_compute_qty_invoiced', string="Billed Qty", digits='Product Unit of Measure', store=True)
    qty_to_invoice = fields.Float(compute='_compute_qty_invoiced', string='To Invoice Quantity', store=True, readonly=True,
                                  digits='Product Unit of Measure')
    date_order = fields.Date(related='grading_summary_id.date', string='Order Date', readonly=True)
    
    # fee = fields.Float(compute='_compute_fee', inverse='_inverse_price', string='Fee',store=True)
    # fee = fields.Float(string='Fee')
    # price_fee_subtotal = fields.Monetary(compute='_compute_price_fee_subtotal', string='Subtotal Fee', default=0.00,store=True)
    # lot_name = fields.Char('Lot/Serial Number Name')
    
    # @api.model_create_multi
    # def create(self, vals_list):
    #     for values in vals_list:
    #         if values.get('display_type', self.default_get(['display_type'])['display_type']):
    #             values.update(product_name=False, wood_class_id=False, master_hasil=False, qty_pcs=0, qty_kubikasi=0, price_unit=0, price_subtotal=0)
    #         else:
    #             values.update(self._prepare_add_missing_fields(values))

    # @api.model
    # def _prepare_add_missing_fields(self, values):
    #     """ Deduce missing required fields from the onchange """
    #     res = {}
    #     onchange_fields = ['name', 'product_name', 'wood_class_id', 'master_hasil', 'qty_pcs', 'qty_kubikasi', 'price_unit', 'price_subtotal']
    #     if values.get('grading_summary_id') and values.get('product_name') and any(f not in values for f in onchange_fields):
    #         line = self.new(values)
    #         line.onchange_product_id()
    #         for field in onchange_fields:
    #             if field not in values:
    #                 res[field] = line._fields[field].convert_to_write(line[field], line)
    #     return res



    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.price_unit = self.product_qty = 0.0
        # self.price_unit = 0.0
        # self.product_qty = 0.0

        self._product_id_change()

        # self._suggest_quantity()
        # self._onchange_quantity()

    # @api.depends('fee','qty_kubikasi')    
    # def _compute_price_fee_subtotal(self):
    #     for rec in self:
    #         rec.price_fee_subtotal =  rec.qty_kubikasi * rec.fee
    
    # @api.depends('product_id')
    def _get_product_purchase_description(self, product_lang):
        self.ensure_one()
        name = product_lang.display_name
        if product_lang.description_purchase:
            name += '\n' + product_lang.description_purchase

        return name

    def _product_id_change(self):
        for rec in self:
            if not rec.product_id:
                return

            rec.product_uom = rec.product_id.uom_po_id or rec.product_id.uom_id
            product_lang = rec.product_id.with_context(
                lang=get_lang(rec.env, rec.grading_summary_id.partner_id.lang).code,
                partner_id=rec.grading_summary_id.partner_id.id,
                company_id=rec.grading_summary_id.company_id.id,
            )
            rec.name = rec._get_product_purchase_description(product_lang)

            rec._compute_tax_id()

    # @api.depends('qty_kubikasi', 'price_unit')
    # def _compute_amount(self):
    #     for rec in self:
    #         rec.price_subtotal = rec.qty_kubikasi * rec.price_unit
    
    @api.depends('qty_kubikasi', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['qty_kubikasi'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
    
    @api.depends('product_id', 'date_order')
    def _compute_account_analytic_id(self):
        for rec in self:
            if not rec.account_analytic_id:
                default_analytic_account = rec.env['account.analytic.default'].sudo().account_get(
                    product_id=rec.product_id.id,
                    partner_id=rec.grading_summary_id.partner_id.id,
                    user_id=rec.env.uid,
                    date=rec.date_order,
                    company_id=rec.company_id.id,
                )
                rec.account_analytic_id = default_analytic_account.analytic_id

    @api.depends('product_id', 'date_order')
    def _compute_analytic_tag_ids(self):
        for rec in self:
            if not rec.analytic_tag_ids:
                default_analytic_account = rec.env['account.analytic.default'].sudo().account_get(
                    product_id=rec.product_id.id,
                    partner_id=rec.grading_summary_id.partner_id.id,
                    user_id=rec.env.uid,
                    date=rec.date_order,
                    company_id=rec.company_id.id,
                )
                rec.analytic_tag_ids = default_analytic_account.analytic_tag_ids

# (Pdb) self.grading_summary_line_ids.invoice_lines
    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity')
    # @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity','move_id.purchase_line_id.product_id','product_id')
    
    def _compute_qty_invoiced(self):
        for line in self:
            # compute qty_invoiced
            qty = 0.0
            for inv_line in line.invoice_lines:
                if inv_line.move_id.state not in ['cancel']:
                    if inv_line.move_id.move_type == 'in_invoice':
                        qty += inv_line.product_uom_id._compute_quantity(inv_line.quantity, line.product_uom)
                    elif inv_line.move_id.move_type == 'in_refund':
                        qty -= inv_line.product_uom_id._compute_quantity(inv_line.quantity, line.product_uom)
            line.qty_invoiced = qty

            # compute qty_to_invoice
            line.qty_to_invoice = line.qty_kubikasi - line.qty_invoiced

        # Perulangan ambil data dari move_id
        # for stock_move in self.move_id.browse(1):
        #     for purchase_line in stock_move.purchase_line_id:
        #         if purchase_line.product_id.id == self.product_id.id:
        #             # self.qty_to_invoice = purchase_line.product_qty - purchase_line.qty_invoiced
        #             if purchase_line.move_ids.state not in ['cancel']:
        #                 if purchase_line.move_id.move_type == 'in_invoice':
        #                     qty += purchase_line.product_uom_id._compute_quantity(purchase_line.quantity, self.product_uom)
        #                 elif purchase_line.move_id.move_type == 'in_refund':
        #                     qty -= purchase_line.product_uom_id._compute_quantity(purchase_line.quantity, self.product_uom)
        #             logger.info('========================================================')
        #             logger.info('qty_to_invoice: %s') % (qty)
        #             logger.info('========================================================')
        #             self.qty_to_invoice = qty

        #             purchase_line.qty_invoiced = qty
            
            
        
    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        aml_currency = move and move.currency_id or self.currency_id
        date = move and move.date or fields.Date.today()
        res = {
            # 'display_type': self.display_type,
            'sequence': self.sequence,
            'name': '%s: %s' % (self.grading_summary_id.name, self.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'price_unit': self.currency_id._convert(self.price_unit, aml_currency, self.company_id, date, round=False),
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'analytic_account_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'grading_summary_line_id': self.id,
            # 'purchase_line_id': self.move_id.purchase_line_id.id,
            
            # # Tambahkan fee di account.move.line
            # 'fee': self.fee,
            # 'price_fee_subtotal': self.price_fee_subtotal,
            
            # # self.grading_summary_line_ids.move_id.purchase_line_id
            # # 'purchase_line_id':self.grading_summary_id.picking_id.purchase_id.order_line.id
            
            
        }
        if not move:
            return res

        if self.currency_id == move.company_id.currency_id:
            currency = False
        else:
            currency = move.currency_id

        res.update({
            'move_id': move.id,
            'currency_id': currency and currency.id or False,
            'date_maturity': move.invoice_date_due,
            'partner_id': move.partner_id.id,
        })
        return res
    
    def _compute_tax_id(self):
        for line in self:
            line = line.with_company(line.company_id)
            fpos = line.grading_summary_id.fiscal_position_id or line.grading_summary_id.fiscal_position_id.get_fiscal_position(line.grading_summary_id.partner_id.id)
            # filter taxes by company
            taxes = line.product_id.supplier_taxes_id.filtered(lambda r: r.company_id == line.env.company)
            line.taxes_id = fpos.map_tax(taxes, line.product_id, line.grading_summary_id.partner_id)

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.grading_summary_id.currency_id,
            'qty_kubikasi': self.qty_kubikasi,
            'product': self.product_id,
            'partner': self.grading_summary_id.partner_id,
        }