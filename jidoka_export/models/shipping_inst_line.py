from odoo import _, api, fields, models

class ShippingInstLine(models.Model):
    _name = 'shipping.inst.line'
    _description = 'Shipping Instruction Line'
    
    shipping_id = fields.Many2one(comodel_name='shipping.ins', string='Shipping Instruction')
    name = fields.Char(string='Description')
    sku = fields.Char('SKU')
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
    )
    product_tmpl_id = fields.Many2one('product.template', string='Product', related='product_id.product_tmpl_id')
    uom_id = fields.Many2one("uom.uom","Unit Of Measure", store=True, related='product_id.uom_id')
    lot_id = fields.Many2one(comodel_name='stock.production.lot', string='Lot/Serial Number', domain="[('product_id','=',product_id)]")
    location_id = fields.Many2one('stock.location', string='From', default=lambda self: self.env.ref('stock.stock_location_stock').id)
    
    qty_done = fields.Float('Done')
    product_uom_qty = fields.Float('Quantity',readonly=True)
    qty_delivered = fields.Float('Delivered',readonly=True)
    
    reserved = fields.Float('Reserved')
    type = fields.Char('type')
    
    pack = fields.Float('Pack (CTN)', related='product_tmpl_id.pack', store=True)
    net_weight = fields.Float('Net Weight (KGS)', related='product_tmpl_id.net_weight',store=True)
    gross_weight = fields.Float('Gross Weight (KGS)', related='product_tmpl_id.gross_weight',store=True)
    means = fields.Float('Measurement (CBM)', related='product_tmpl_id.means',store=True)
    
    william_fob_price = fields.Float('Single Price',store=True)
    william_set_price = fields.Float('Set Price',store=True)
    unit_price = fields.Float('Unit Price', compute='_compute_unit_price', store=True)
    amount = fields.Float('Amount', compute='_compute_amount', store=True)
    
    volume_uom_name = fields.Char('Measurement', related='product_tmpl_id.volume_uom_name')
    weight_uom_name = fields.Char('Measurement', related='product_tmpl_id.weight_uom_name')
    qty_done = fields.Float('Done')
    
    order_id = fields.Many2one(comodel_name='sale.order', string='Order',store=True)
    order_line_id = fields.Many2one(comodel_name='sale.order.line', string='Order Line',store=True)
    # move_id = fields.Many2one(comodel_name='stock.move', string='move', )
    move_id = fields.Many2one(comodel_name='stock.move', string='Move', 
        compute='_compute_move_id',store=True)
    qty_si = fields.Float('Qty SI', 
        readonly=False )
        # compute='_compute_qty_si',readonly=False )
    
    # @api.depends('product_uom_qty','qty_delivered')
    # def _compute_qty_si(self):
    #     for r in self:
    #         selisih = r.product_uom_qty - r.qty_delivered
    #         if selisih != 0:
    #             r.qty_si = selisih
    #         else:
    #             r.qty_si = 0
    
    @api.depends('product_id','order_id')
    def _compute_move_id(self):
        for r in self:
            move  = self.env['stock.move'].search([('product_id','=',r.product_id.id),('origin','=',r.order_id.name)],limit=1)
            if move:
                r.move_id = move.id
            else:
                r.move_id = False
                
    @api.depends('william_fob_price', 'william_set_price')
    def _compute_unit_price(self):
        for record in self:
            record.unit_price = record.william_fob_price + record.william_set_price

    @api.depends('product_uom_qty', 'unit_price')
    def _compute_amount(self):
        for record in self:
            record.amount = record.product_uom_qty * record.unit_price
        
        
    # @api.constrains('product_uom_qty','qty_delivered','qty_si')
    # def validate_qty_si(self):
    #     for r in self:
    #         selisih = r.product_uom_qty - r.qty_delivered
    #         if selisih == 0:
    #             if self.qty_si >= selisih:
    #                 raise ValidationError(_("you can't fill it"))

    