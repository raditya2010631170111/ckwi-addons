from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

# 2 packing list container
class ContainerOperation(models.Model):
    _name = 'container.operation'
    _description = 'Container Operation'
    _rec_name = 'container_no'
    
    packing_id = fields.Many2one(comodel_name='packing.list', string='Packing List')
    container_no = fields.Char('Container No.', index=True, required=True)
    seal_no = fields.Char('Seal No.')
    # perlu?
    order_id = fields.Many2one('sale.order', string='Order', related='packing_id.no_sc_id', store=True)
    order_ids = fields.Many2many('sale.order', string='Order', 
        related='packing_id.no_sc_ids', store=True)
    # detail isi container
    container_operation_line_ids = fields.One2many(comodel_name='container.operation.line', 
        inverse_name='container_operation_id', string='Operation Container Line', store=True)
    picking_ids = fields.Many2many('stock.picking', 'picking_ids_rel', 'container_line_id', 'picking_id',
        string='No SJ', store=True)
    available_picking_ids = fields.Many2many('stock.picking', 'container_operation_available_picking_rel',
        'container_operation_id', 'picking_id',  string='Available Picking', 
        compute="_get_available_picking", store=True)
    # total - total
    total_net_wght = fields.Float('Total Net Weight', compute='_compute_totals')
    total_gross_wght = fields.Float('Total Gross Weight', compute='_compute_totals')
    total_means = fields.Float('Total Measurement', compute='_compute_totals')
    total_qty = fields.Float('Total Quantity', compute='_compute_totals')
    total_qty_pcs = fields.Float('Total Quantity Pcs', compute='_compute_totals')
    total_qty_set = fields.Float('Total Quantity Set', compute='_compute_totals')
    total_pack = fields.Float('Total Pack', compute='_compute_totals')
    # char ???
    volume_uom_name_line = fields.Char('Measurement')
    weight_uom_name_line = fields.Char('weight_uom_name')
    uom_name_line = fields.Char('Measurement')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,
        index=True, required=True)
    state = fields.Selection(string='State', store=True, related='packing_id.state')
    move_container_ids = fields.Many2many('stock.move','container_operation_move_rel', string='Move Container', compute='_compute_move_container_ids', store=True,)

    order_ids = fields.Many2many('sale.order', 'container_operation_sale_order_rel', string='order', related='packing_id.no_sc_ids')
    buyer_po = fields.Char('Buyer PO', 
        compute='_compute_buyer_po',store=True)
    @api.depends('container_operation_line_ids.buyer_po')
    def _compute_buyer_po(self):
        # for record in self:
        #     buyer_pos = record.container_operation_line_ids.mapped('buyer_po')
        #     buyer_pos = list(set(buyer_pos))  # Menghapus duplikat dengan menggunakan set()
        #     record.buyer_po = ', '.join(buyer_pos)
            
        for record in self:
            # buyer_pos = record.container_operation_line_ids.mapped('buyer_po')
            # buyer_pos = list(set(buyer_pos))  # Menghapus duplikat dengan menggunakan set()
            # # record.buyer_po = ', '.join(buyer_pos)
            # buyer_pos = [str(po) for po in buyer_pos if isinstance(po, str)]
            # record.buyer_po = ', '.join(buyer_pos)
            
            buyer_pos = record.container_operation_line_ids.filtered(lambda r: r.buyer_po).mapped('buyer_po')
            buyer_pos = list(set(buyer_pos))
            record.buyer_po = ', '.join(buyer_pos)


    
    # @api.depends(
    #     'container_operation_line_ids',
    #     'container_operation_line_ids.pack',
    #     )
    def _compute_totals(self):
        for record in self:
            # pack
            subtotal_pack = sum(line.pack for line in record.container_operation_line_ids)
            # qty
            subtotal_qty_pcs = 0.0
            subtotal_qty_set = 0.0
            for c_line in record.container_operation_line_ids:
                if c_line.product_uom.name == 'pcs':
                    subtotal_qty_pcs += c_line.product_container_qty
                elif c_line.product_uom.name == 'set':
                    subtotal_qty_set += c_line.product_container_qty
            # means
            subtotal_means = sum(line.means for line in record.container_operation_line_ids)
            # gross
            total_weight_gross = sum(record.container_operation_line_ids.mapped(lambda line: line.gross_weight ))
            # weight
            total_weight = sum(record.container_operation_line_ids.mapped(lambda line: line.net_weight))

            record.total_pack = subtotal_pack
            record.total_qty = sum(line.product_container_qty for line in record.container_operation_line_ids)
            record.total_qty_pcs = subtotal_qty_pcs
            record.total_qty_set = subtotal_qty_set
            record.total_means = subtotal_means
            record.total_gross_wght = total_weight_gross
            record.total_net_wght = total_weight


    # @api.depends('order_id', 'container_no', 'seal_no')
    # def _get_available_picking(self):
    #     for rec in self:
    #         picking_ids = False
    #         if rec.order_id:
    #             picking_ids = rec.env['stock.picking'].search([
    #                 ('sale_id', '=', rec.order_id.id),
    #                 ('state', '=', 'done')])
    #         rec.available_picking_ids = picking_ids
    
    
    # BACA order_id available_picking
    # @api.depends('order_id', 'container_no', 'seal_no')
    # def _get_available_picking(self):
    #     for rec in self:
    #         if rec.order_id:
    #             res = [(5, 0)]
    #             picking_ids = False
    #             if rec.container_no or rec.seal_no:
    #                 picking_ids = rec.env['stock.picking'].search([('origin', '=', rec.order_id.name), ('state', '=', 'done')])
    #             if picking_ids:
    #                 res = [(6, 0, picking_ids.ids)]
    #             rec.available_picking_ids = res
    
    @api.depends('order_ids')
    def _get_available_picking(self):
        # for operation in self:
        #     operation.available_picking_ids = operation.order_ids.mapped('picking_ids')
        for operation in self:
            picking_ids = self.env['stock.picking'].search([
                ('sale_id', 'in', operation.order_ids.ids),
                ('state', '=', 'done')
            ])
            operation.available_picking_ids = picking_ids.ids

    @api.onchange('container_no')
    def onchange_container_no(self):
        if self.container_no:
            self.order_ids = self.packing_id.no_sc_ids.ids
    
                
                
                
    
    def action_show_details(self):
        self.ensure_one()
        view = self.env.ref('jidoka_export.view_container_operations')
        return {
            'name': _('Container Details'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'container.operation',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context
            ),
        }
    
    def _verify_container(self):
        for rec in self:
            for move in rec.container_operation_line_ids.mapped('move_id'):
                move._compute_qty_in_container()
                if move.qty_available_container < 0:
                    raise ValidationError(_('Invalid product %s in container %s') % (move.product_id.name, rec.container_no))
    
    def write(self, vals):
        # _logger.info('--- write event container ----')
        # _logger.info(vals)
        res = super(ContainerOperation, self).write(vals)
        self._verify_container()
        return res
    
    def unlink(self):
        picking_ids = self.picking_ids
        line_ids = self.container_operation_line_ids
        res = super(ContainerOperation, self).unlink()
        try:
            line_ids.unlink()
        except:
            _logger.info('Failed to delete %s' % str(line_ids))
        picking_ids.move_lines._compute_qty_in_container()
        return res
    
    # TODO validasi agar valid / tidak kelebihan kirim barang di container
    
# 3 detail isi container
class ContainerOperationLine(models.Model):
    _name = 'container.operation.line'
    _description = 'Container Operation Line'
    
    container_operation_id = fields.Many2one('container.operation', string='Container Operation', 
        ondelete='cascade')
    packing_id = fields.Many2one(comodel_name='packing.list', string='Packing List', 
        related='container_operation_id.packing_id', store=True, ondelete='cascade')
    # move data
    move_id = fields.Many2one('stock.move', string='Move', required=True, ondelete='cascade')
    product_id = fields.Many2one(comodel_name= 'product.product', string='Product',store=True, 
        related='move_id.product_id')
    product_uom_qty = fields.Float('Quantity', store=True, related='move_id.product_uom_qty')
    quantity_done = fields.Float('Quantity', store=True, related='move_id.quantity_done')
    product_uom = fields.Many2one('uom.uom', string='UoM',store=True, related='move_id.product_uom')
    picking_id = fields.Many2one('stock.picking', string='picking', store=True, 
        related='move_id.picking_id')
    # container data (related)
    container_no = fields.Char('Container No.', related='container_operation_id.container_no', store=True)
    seal_no = fields.Char('Seal No.', related='container_operation_id.seal_no', store=True)
    # Qty
    product_container_qty = fields.Float('Quantity in Cont.')
    # other data
    sku = fields.Char('SKU', compute='_compute_order_line_id', store=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,
        index=True, required=True)
    # unit_price = fields.Float('Unit Price')
    # amount = fields.Float('Amount')
    unit_price = fields.Float('Unit Price', 
        compute='_compute_unit_price' )
    # amount = fields.Float('Amount', 
    #     compute='_compute_amount' )
    amount = fields.Monetary('Amount', 
        compute='_compute_amount', currency_field='currency_id')
    
    currency_id = fields.Many2one('res.currency', string='Currency', related='packing_id.currency_id')
    
    #sale.order
    # order_id = fields.Many2one('sale.order', string='order', related='field_name')
    
    # product data
    # pack = fields.Float('Pack (CTN)', store=True, related='product_id.pack' )
    # net_weight = fields.Float('Net Weight (KGS)', store=True , related='product_id.net_weight')
    # gross_weight = fields.Float('Gross Weight (KGS)', store=True, related='product_id.gross_weight' )
    # means = fields.Float('Measurement(CBM)', store=True , related='product_id.means')
    pack = fields.Float('Pack (CTN)', store=True, compute='_compute_value_logistic')
    net_weight = fields.Float('Net Weight (KGS)', store=True, compute='_compute_value_logistic')
    gross_weight = fields.Float('Gross Weight (KGS)', store=True, compute='_compute_value_logistic')
    means = fields.Float('Measurement(CBM)', store=True, compute='_compute_value_logistic')
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    account_id = fields.Many2one('account.account', store=True,string='Account', 
        related='product_id.property_account_income_id')
    buyer_po = fields.Char('Buyer PO', related='order_line_id.order_id.buyer_po', readonly=False)
    cust_ref = fields.Char('Cust Ref', related='order_line_id.no_po_cust', readonly=False)
    
    
    @api.depends('product_container_qty','product_container_qty')
    def _compute_value_logistic(self):
        for r in self:
            r.pack = r.product_container_qty * r.product_id.pack
            r.net_weight = r.product_container_qty * r.product_id.net_weight
            r.gross_weight = r.product_container_qty * r.product_id.gross_weight
            r.means = r.product_container_qty * r.product_id.means
            
    @api.depends('product_container_qty','unit_price')
    def _compute_amount(self):
        for r in self:
            r.amount = r.unit_price * r.product_container_qty
            
    @api.depends('order_line_id.william_fob_price', 'order_line_id.william_set_price')
    def _compute_unit_price(self):
        for record in self:
            if record.order_line_id.william_fob_price:
                record.unit_price = record.order_line_id.william_fob_price
            elif record.order_line_id.william_set_price:
                record.unit_price = record.order_line_id.william_set_price
            else:
                record.unit_price = 0.0
                
                
    # # @api.onchange('product_id','product_container_qty')
    # @api.onchange('product_container_qty')
    # def onchange_field(self):
    #     # for r in self.container
    #     # self.pack = self.product_container_qty * self.product_id.pack
    #     # self.net_weight = self.product_container_qty * self.product_id.net_weight
    #     # self.gross_weight = self.product_container_qty * self.product_id.gross_weight
    #     # self.means = self.product_container_qty * self.product_id.means
    #     for r in self:
    #         r.pack = r.product_container_qty * r.product_id.pack
    #         r.net_weight = r.product_container_qty * r.product_id.net_weight
    #         r.gross_weight = r.product_container_qty * r.product_id.gross_weight
    #         r.means = r.product_container_qty * r.product_id.means
    
    
    # @api.onchange('product_container_qty')
    # def onchange_product_container_qty(self):
    #     for r in self:
    #         r.pack = r.product_container_qty * r.product_id.pack
    #         r.net_weight = r.product_container_qty * r.product_id.net_weight
    #         r.gross_weight = r.product_container_qty * r.product_id.gross_weight
    #         r.means = r.product_container_qty * r.product_id.means
    

    
    
    
    

    # TODO perlu hitung amount?

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
                record.sku = so_line.sku
            else:
                record.order_line_id = False
                record.sku = False

                
                
                

    @api.onchange('move_id')
    def _onchange_move_id(self):
        # _logger.info('---- onchange event -----')
        if self.move_id:
            lols = self.container_operation_id.container_operation_line_ids
            _logger.info('---- all lines -----')
            _logger.info([(l.move_id, l.product_container_qty, l.container_operation_id) for l in lols])
            existing_data = self.env['container.operation.line'].sudo().search([
                ('move_id', '=', self.move_id.id),
                ('container_operation_id', '!=', False)
            ])
            _logger.info('---- search db -----')
            _logger.info(existing_data.mapped('product_container_qty'))
            qty_avail = self.move_id.quantity_done - sum(existing_data.mapped('product_container_qty'))
            _logger.info(qty_avail)
            self.product_container_qty = qty_avail
        else:
            self.product_container_qty = 0

    def write(self, vals):
        # _logger.info('--- write event container line ----')
        # _logger.info(vals)
        return super(ContainerOperationLine, self).write(vals)
    
