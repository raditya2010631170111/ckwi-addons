from odoo import _, api, fields, models

class PackingListOrderLine(models.Model):
    _name = 'packing.list.order.line'
    _description = 'Packing Order Line'
    
    packing_id = fields.Many2one('packing.list', string='Packing')
    company_id = fields.Many2one(related='packing_id.company_id', string='Company', store=True, readonly=True, index=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('ready', 'Ready'),
        ('done', 'Done'),
    ], string='State', related='packing_id.state')
    
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
    
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    # product_id = fields.Many2one('product.product', string='Product', ondelete='restrict')
    product_uom_category_id = fields.Many2one('uom.category', related='product_id.uom_id.category_id')
    # invoice_status = fields.Selection([
    #     ('upselling', 'Upselling Opportunity'),
    #     ('invoiced', 'Fully Invoiced'),
    #     ('to invoice', 'To Invoice'),
    #     ('no', 'Nothing to Invoice')
    #     ], string='Invoice Status', compute='_compute_invoice_status', store=True, readonly=True, default='no')
    
    is_expense = fields.Boolean('Is expense', help="Is true if the sales order line comes from an expense or a vendor bills") 
    # product_uom = fields.Many2one('uom.uom', string='UoM',store=True, related='move_id.product_uom')   
    amount = fields.Monetary('Amount', currency_field='currency_id')
    
    pack = fields.Float('Pack (CTN)', store=True)
    net_weight = fields.Float('Net Weight (KGS)')
    gross_weight = fields.Float('Gross Weight (KGS)')
    means = fields.Float('Measurement(CBM)')
    currency_id = fields.Many2one('res.currency', string='Currency')
    order_line_id = fields.Many2one('sale.order.line', string='Order Line', store=True)   
    cust_ref = fields.Char('Cust Ref', related='order_line_id.cust_ref', store=True) 
    qty_delivered_method = fields.Selection([
        ('manual', 'Manual'),
        ('analytic', 'Analytic From Expenses'),
        ('stock_move', 'Stock Moves')
    ], string="Method to update delivered qty", compute='_compute_qty_delivered_method', compute_sudo=True, store=True, readonly=True,
        help="According to product configuration, the delivered quantity can be automatically computed by mechanism :\n"
             "  - Manual: the quantity is set manually on the line\n"
             "  - Analytic From expenses: the quantity is the quantity sum from posted expenses\n"
             "  - Timesheet: the quantity is the sum of hours recorded on tasks linked to this sale line\n"
             "  - Stock Moves: the quantity comes from confirmed pickings\n")
    @api.depends('state', 'is_expense','product_id')
    def _compute_qty_delivered_method(self):
        """ Sale module compute delivered qty for product [('type', 'in', ['consu']), ('service_type', '=', 'manual')]
                - consu + expense_policy : analytic (sum of analytic unit_amount)
                - consu + no expense_policy : manual (set manually on SOL)
                - service (+ service_type='manual', the only available option) : manual

            This is true when only sale is installed: sale_stock redifine the behavior for 'consu' type,
            and sale_timesheet implements the behavior of 'service' + service_type=timesheet.
        """
        for line in self:
            if line.is_expense:
                line.qty_delivered_method = 'analytic'
            else:  # service and consu
                line.qty_delivered_method = 'manual'
            if not line.is_expense and line.product_id.type in ['consu', 'product']:
                line.qty_delivered_method = 'stock_move'