from odoo import _, api, fields, models

class InvoiceOrderLine(models.Model):
    _name = 'invoice.order.line'
    _description = 'Invoice Order Line'
    
    export_invoice_id = fields.Many2one(comodel_name='invoice', string='invoice')
    # company_id = fields.Many2one(related='export_invoice_id.company_id', string='Company', store=True, readonly=True, index=True)
    company_id = fields.Many2one( string='Company', store=True, readonly=True, index=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('ready', 'Ready'),
        ('done', 'Done'),
    ], string='State', related='export_invoice_id.state')
    
    product_id = fields.Many2one(
        'product.product', string='Product', domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True, ondelete='restrict', check_company=True)  # Unrequired company
    product_template_id = fields.Many2one(
        'product.template', string='Product Template',
        related="product_id.product_tmpl_id", domain=[('sale_ok', '=', True)])
    # order_partner_id = fields.Many2one(related='order_id.partner_id', store=True, string='Customer', readonly=False)
    # product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    # qty_delivered = fields.Float('Delivered Quantity', copy=False, compute='_compute_qty_delivered', inverse='_inverse_qty_delivered', compute_sudo=True, store=True, digits='Product Unit of Measure', default=0.0)
    # qty_invoiced = fields.Float(
    #     compute='_get_invoice_qty', string='Invoiced Quantity', store=True, readonly=True,
    #     compute_sudo=True,
    #     digits='Product Unit of Measure')
    price_unit = fields.Float('Unit Price', digits='Product Price', default=0.0)
    move_id = fields.Many2one('stock.move', string='Move')
    quantity = fields.Float('Quantity')
    picking_id = fields.Many2one('stock.picking', string='picking', store=True, 
        related='move_id.picking_id')
    
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    # product_id = fields.Many2one('product.product', string='Product', ondelete='restrict')
    product_uom_category_id = fields.Many2one('uom.category', related='product_id.uom_id.category_id')
    # invoice_status = fields.Selection([
    #     ('upselling', 'Upselling Opportunity'),
    #     ('invoiced', 'Fully Invoiced'),
    #     ('to invoice', 'To Invoice'),
    #     ('no', 'Nothing to Invoice')
    #     ], string='Invoice Status', compute='_compute_invoice_status', store=True, readonly=True, default='no')
    
    is_expense = fields.Boolean('Is expense', help="Is true if the sales order line comes from an expense or a vendor bills")    
    amount = fields.Monetary('Amount', currency_field='currency_id')
    
    pack = fields.Float('Pack (CTN)', store=True)
    net_weight = fields.Float('Net Weight (KGS)')
    gross_weight = fields.Float('Gross Weight (KGS)')
    means = fields.Float('Measurement(CBM)')
    currency_id = fields.Many2one('res.currency', string='Currency')
    account_id = fields.Many2one('account.account', store=True,string='Account', related='categ_id.property_account_income_categ_id')
    categ_id = fields.Many2one(
        'product.category', 'Product Category', ondelete='cascade', related='product_id.categ_id',store=True)
    # order_line_id = fields.Many2one('sale.order.line', string='Order Line', store=True)
    
    order_line_id = fields.Many2one('sale.order.line', string='Order Line', compute='_compute_order_line_id', store=True)
    @api.depends('product_id', 'picking_id')     
    def _compute_order_line_id(self):
        for record in self:
            so_line = self.env['sale.order.line'].search([
                ('product_id', '=', record.product_id.id),
                ('no_mo', '=', record.picking_id.origin)
            ], limit=1)
            
            if so_line:
                record.order_line_id = so_line
                # record.sku = so_line.sku
            else:
                record.order_line_id = False