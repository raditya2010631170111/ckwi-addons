from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo import http
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)




class ShippingIns(models.Model):
    _name = 'shipping.ins'
    _description = 'Shipping Instruction'

    name = fields.Char('Name', default=lambda self: _('New'), copy=False, readonly=True)
    # product_line_ids = fields.One2many(comodel_name='shipping.ins.line', string='Product Detail', 
                                    #    inverse_name='shipping_id')
    # to_partner_id = fields.Many2one('res.partner', string='To', required=True, store=True)
    # to_partner_id = fields.Many2one('res.partner', string='Customer', required=True, store=True)
    # to_partner_country_id = fields.Many2one('res.country', string='To', required=True)
    to_partner_id = fields.Many2one('res.partner', string='Buyer', store=True)
    to_partner_country_id = fields.Many2one('res.country', string='To')
    to_city_deliver = fields.Char('Deliver City')
    to_country_of_deliver_id = fields.Many2one('res.country', string='Country of Delivery')

    to_respartner_destination_id = fields.Many2one('res.partner', string='To')

    # delivery_address_id = fields.Many2one('res.partner', string='Delivery Address', required=True)
    delivery_address_id = fields.Many2one('res.partner', string='Delivery Address')
    responsible_id = fields.Many2one('res.partner', string='Responsible', required=True)
    invoice_address_id = fields.Many2one('res.partner',string='Invoice Address')
    # part_of_load = fields.Many2one("res.","Port of Loading")
    shipper_id = fields.Many2one(
    'res.company',
    string='Shipper',
    default=lambda self: self.env['res.company'].search([('name', 'in', ['PT. CIPTA KREASI WOOD INDUSTRY', 'Cipta Kreasi Wood Industry'])], limit=1) or self.env['res.company'].search([], limit=1),
    readonly=True
)
    schedule_date = fields.Date('Schedule Date')
    booking_date = fields.Date('Booking date',required=True)
    cargo_date = fields.Date('Cargo Ready', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='State',default='draft', tracking=True)
    # no_sc_id = fields.Many2one('sale.order', 'Sales Confirmation No.')
    no_sc_id = fields.Many2one('sale.order', 'SC No.')
    marchandise = fields.Char(string= 'Merchandise', default='SEE ATTACHMENTS')    
    vessel = fields.Char(string='Vessel')
    container = fields.Char(string='Container')
    container_no = fields.Char(string='Container No.')
    total_net_wght = fields.Float('Total Net Weight', compute='_compute_total_net_weight')
    total_gross_wght = fields.Float('Total Gross Weight', compute='_compute_total_gross_wght')
    total_means = fields.Float('Total Measurement', compute='_compute_total_total_means')
    total_qty = fields.Float('Total Quantity', compute='_compute_total_total_qty',store=True)
    total_pack = fields.Float('Total Pack', compute='_compute_total_pack')
    volume_uom_name_line = fields.Char('Measurement', related='product_line_ids.volume_uom_name')
    weight_uom_name_line = fields.Char('weight_uom_name', related='product_line_ids.weight_uom_name')
    uom_name_line = fields.Char('Measurement', related='product_line_ids.product_id.uom_id.name')
    freight = fields.Char('Freight', default='Collect')
    indicating = fields.Text('Indicating')
    seal_no = fields.Char('Seal No.')
    # peb_no = fields.Char(string='PEB No.')
    no_peb = fields.Integer(string='PEB No.')
    buyer_po = fields.Char('Buyer PO')
    packing_list_count = fields.Integer(
            compute="_compute_packing_list_count", string='Packing List Count', copy=False, default=0, store=True)
    packing_list_ids = fields.One2many(
        string='Packing',
        comodel_name='packing.list',
        inverse_name='shipping_ins_id',
    )
    

    sail_date = fields.Date(string='Sail Date')
    bl = fields.Char(string='BL')
    shipping_date = fields.Date('Date', required=True)
    
    city_of_deliver_id = fields.Many2one("res.country.state","Deliver State")
    city_deliver = fields.Char('Deliver City')
    country_of_deliver_id = fields.Many2one('res.country', string='Country of Delivery')
    
    to_shipping_id = fields.Many2one('res.partner', string='To')
    
    pol_city = fields.Char('Deliver City', required=True)
    pol_country_id = fields.Many2one('res.country', string='Country of Delivery', required=True)
    
    destination_city = fields.Char('City', required=True)
    destination_country_state_id = fields.Many2one('res.country.state', string='Country State')
    destination_country_id = fields.Many2one('res.country', string='Country', required=True)
    consignee_id = fields.Many2one('res.partner', string='Consignee')
    
    is_do = fields.Boolean('Is DO', copy=False)
    
    no_sc_ids = fields.Many2many(
        string='No SC',
        comodel_name='sale.order',
        relation='shipping_ins_nosc_order_rel',
        column1='shipping_ins_id',
        column2='order_id',copy=False
    )
    
    picking_ids = fields.Many2many(
        string='Picking',
        comodel_name='stock.picking',
        relation='shipping_ins_picking_order_rel',
        column1='shipping_ins_id',
        column2='picking_id',
        compute='_compute_picking_ids' )
    
    shipping_inst_line_ids = fields.Many2many(
        string='Shipping Inst Line',
        comodel_name='shipping.inst.line',
        relation='shipping_ins_line_order_rel',
        column1='shipping_ins_id',
        column2='shipping_inst_line_id',
            compute='_compute_shipping_inst_line_ids')
    #  =====================================================   
    available_order_line_ids = fields.Many2many(
        string='Available Order Line',
        comodel_name='sale.order.line',
        relation='shipping_ins_available_order_line_order_rel',
        column1='shipping_ins_id',
        column2='order_line_id', 
            compute='_compute_available_order_line_ids')
    move_ids = fields.Many2many('stock.move', string='Moves', 
        compute='_compute_move_ids' )
    move_line_ids = fields.Many2many('stock.move.line', string='Move Line',
        compute='_compute_move_line_ids' )
    
    product_line_ids = fields.One2many(comodel_name='shipping.ins.line', string='Product Detail', inverse_name='shipping_id', copy=False)
    
    delivery_order_count = fields.Integer(
            compute="_compute_delivery_order_count", string='Delivery Order Count', copy=False, default=0)
    
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('shipping.ins') or _('New')
        result = super(ShippingIns, self).create(vals)
        # _logger.info("================create")
        # _logger.info(vals)
        # product_line_ids = self._update_product_line_ids
        # _logger.info("================create product_line_ids")
        # _logger.info(product_line_ids)
        return result
    
    def write(self, values):
        result = super(ShippingIns, self).write(values)
        _logger.info("================write values")
        _logger.info(values)
        _logger.info("================write result")
        _logger.info(result)
        for rec in self:
            if 'product_line_ids' in values:
                self._remove_nolink_shipping()
        return result
    #    ====================================== 
    
    @api.depends('no_sc_ids')
    def _compute_picking_ids(self):
        for shipping_ins in self:
            pickings = self.env['stock.picking'].search([('origin', 'in', shipping_ins.no_sc_ids.mapped('name'))])
            shipping_ins.picking_ids = pickings
                            
    @api.depends('picking_ids')
    def _compute_delivery_order_count(self):
        for picking in self:
            picking.delivery_order_count = len(picking.picking_ids)
            
            # domain': [('origin','in',self.no_sc_ids.mapped('name')
            
    @api.depends('available_order_line_ids')
    def _compute_shipping_inst_line_ids(self):
        for r in self:
            shipping_inst_lines = self.env['shipping.inst.line']
            product_lines = self.env['shipping.ins.line']
            if not r.available_order_line_ids:
                r.shipping_inst_line_ids = False
            # else:
            # vals= {}
            for rec in r.available_order_line_ids:
                vals = {
                    'order_line_id':rec.id,
                    'order_id': rec.order_id.id,
                    'product_id' : rec.product_id.id,
                    'product_uom_qty' : rec.product_uom_qty,
                    'qty_delivered' : rec.qty_delivered,
                    'reserved' : rec.product_uom_qty,
                    'name'  : rec.name,
                    'william_fob_price' : rec.william_fob_price,
                    'william_set_price' : rec.william_set_price,
                    'sku' : rec.sku,
                    'shipping_id' : self.id,
                }
                shipping_inst_line = shipping_inst_lines.create(vals)
                # self.write({'shipping_inst_line_ids':[(4,shipping_inst_line.id)]})
                    
                r.shipping_inst_line_ids += shipping_inst_line
    
    @api.depends('available_order_line_ids')
    def _compute_move_ids(self):
        # for r in self:
        # if not self.available_order_line_ids:
        #     self.move_ids = False
        for record in self:
            record.move_ids = record.available_order_line_ids.mapped('move_ids')
        
    @api.depends('no_sc_ids.order_line')
    def _compute_available_order_line_ids(self):
        for shipping_ins in self:
            order_lines = shipping_ins.no_sc_ids.mapped('order_line')
            shipping_ins.available_order_line_ids = order_lines
    
    @api.depends('move_ids')
    def _compute_move_line_ids(self):
        for r in self:
            if not r.move_ids:
                r.move_line_ids = False
            r.move_line_ids = r.move_ids.move_line_ids
        
    @api.depends('product_line_ids.pack', 'product_line_ids.product_uom_qty')
    def _compute_total_pack(self):
        for record in self:
            subtotal_pack = sum(line.pack * line.product_uom_qty for line in record.product_line_ids)
            record.total_pack = subtotal_pack

    @api.depends('product_line_ids.product_uom_qty')
    def _compute_total_total_qty(self):
        for record in self:
            subtotal_qty = sum(record.product_line_ids.mapped('product_uom_qty'))
            record.total_qty = subtotal_qty
    
    @api.depends('product_line_ids.means', 'product_line_ids.product_uom_qty')
    def _compute_total_total_means(self):
        for record in self:
            subtotal_means = sum(line.means * line.product_uom_qty for line in record.product_line_ids)
            record.total_means = subtotal_means
    
    @api.depends('product_line_ids.gross_weight', 'product_line_ids.product_uom_qty')
    def _compute_total_gross_wght(self):
        for record in self:
            total_weight_gross = sum(record.product_line_ids.mapped(lambda line: line.gross_weight * line.product_uom_qty))
            record.total_gross_wght = total_weight_gross

    
    @api.depends('product_line_ids.net_weight', 'product_line_ids.product_uom_qty')
    def _compute_total_net_weight(self):
        for record in self:
            total_weight = sum(record.product_line_ids.mapped(lambda line: line.net_weight * line.product_uom_qty))
            record.total_net_wght = total_weight

    @api.depends('packing_list_ids')
    def _compute_packing_list_count(self):
        for order in self:
            order.packing_list_count = len(order.packing_list_ids)
                
    @api.onchange('country_of_deliver_id')
    def _onchange_country_of_deliver_id(self):
        self.city_of_deliver_id = False
#    ========================================================== 
    @api.onchange('no_sc_ids')
    def onchange_no_sc_ids(self):
        for rec in self:
            # rec.product_line_ids.unlink()
            if not rec.no_sc_ids:
            #     # for r in self:
            #     #     for shipping_line in r.product_line_ids:
            #     #         if shipping_line.move_id.state == 'done':
            #     #             raise ValidationError(_("DO sudah validate, tidak bisa di edit kembali"))                    
                rec.product_line_ids = [(5, 0, 0)]
            #     rec._remove_nolink_shipping()
                
            # rec.product_line_ids.unlink()
            if rec.no_sc_ids:
                rec.product_line_ids = [(5, 0, 0)]
                rec._update_product_line_ids()
                # rec._remove_nolink_shipping()
    
    # @api.model
    def _update_product_line_ids(self):
        # self.product_line_ids = [(5, 0, 0)]  # Remove existing lines
        for record in self:
            lines = []
            for no_sc in record.no_sc_ids:
                for rec in no_sc.order_line.filtered(lambda r: r.product_id.type != 'service'):
                    qty_selisih = rec.product_uom_qty - rec.qty_delivered 
                    vals = {
                        'order_id': rec.order_id.id,
                        # 'order_line_id': rec.id,
                        'move_id': rec.move_ids.ids[-1],
                        'product_id': rec.product_id.id,
                        'product_uom_qty': rec.product_uom_qty,
                        'qty_delivered': rec.qty_delivered,
                        'reserved': rec.product_uom_qty,
                        'name': rec.name,
                        'william_fob_price': rec.william_fob_price,
                        'william_set_price': rec.william_set_price,
                        'sku': rec.sku,
                        'shipping_id': self.id,
                        'qty_selisih': qty_selisih,
                        'total_qty_si': sum(rec.shipping_ins_line_ids.filtered(lambda line: line.state == 'done').mapped('qty_si'))
                    }
                    shipping_inst_line = self.env['shipping.ins.line'].create(vals)
                    # vals['qty_si'] = vals.get('qty_si')
                    _logger.info('=====================_update_product_line_ids')
                    _logger.info(shipping_inst_line)
                # lines.append((4, shipping_inst_line.id))
        #         lines.append((0,0,vals))
        # self.product_line_ids = lines
        return


    def _remove_nolink_shipping(self):
        shipping_ins_lines_without_shipping_id = self.env['shipping.ins.line'].search([('shipping_id', '=', False)])
        shipping_ins_lines_without_shipping_id.unlink()
        
    # @api.multi
    def unlink(self):
        for record in self:
            if record.is_do == True:
                raise UserError(
                    'You cannot delete a document!'
                )
        return super(ShippingIns, self).unlink()
    
    
    
    def create_product_line(self, product_id):
        """Function to add product_id to the product_line_ids when creating a shipping.ins record."""
        shipping_line = self.env['shipping.ins.line'].create({
            'shipping_id': self.id,
            'product_id': product_id,
        })
        _logger.info('===================')
        _logger.info(shipping_line)
        
        return shipping_line
    
    
    def action_validate(self):
        for r in self:
            if not r.product_line_ids:
                raise UserError(_('No. SJ filled again, Detailed Operation Empty.'))
        
        if self.packing_list_count == 0:
            if self.state == 'draft':
                self.write({'state': 'done'})
                packing_list = self.env['packing.list'].create({
                    'shipping_ins_id': self.id,   
                    'name' : self.name, 
                    'to_partner_id': self.to_partner_id.id,
                    'no_sc_ids' : self.no_sc_ids,
                    'from_packing_country_id': self.pol_country_id.id,
                    'from_packing_city': self.pol_city,
                    'to_packing_country_id': self.destination_country_id.id,
                    'to_packing_country_state_id': self.destination_country_state_id.id,
                    'to_packing_city': self.destination_city,
                    'state': 'draft',
                    'sail_date': self.sail_date,
                    'bl': self.bl,
                    'vessel': self.vessel,
                    'partner_shipping_id':self.consignee_id.id,
                    'no_peb': self.no_peb
                })
                
        else:
            if self.state == 'draft':
                self.write({'state': 'done'})
                packing_list = self.env['packing.list'].search([('shipping_ins_id','=', self.id)])
                for r in packing_list:
                    r.write({
                        'no_sc_ids': self.no_sc_ids,
                        'to_partner_id': self.to_partner_id.id,
                        'from_packing_country_id': self.pol_country_id.id,
                        'from_packing_city': self.pol_city,
                        'to_packing_country_id': self.destination_country_id.id,
                        'to_packing_country_state_id': self.destination_country_state_id.id,
                        'to_packing_city': self.destination_city,
                        'state': 'draft',
                        # 'invoice_date': self.cargo_date,
                        'sail_date': self.sail_date,
                        'bl': self.bl,
                        'vessel': self.vessel,
                        'partner_shipping_id':self.consignee_id.id,
                        'no_peb': self.no_peb
                    })
                
        # return {
        #     'name': 'Packing List',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'packing.list',
        #     'type': 'ir.actions.act_window',
        #     'res_id': packing_list.id,
        # }
        return True
    
    def action_draft(self):
        self.write({
            'state': 'draft'
        })
    
    def _packing_list_action_view(self):
        views = [(self.env.ref('jidoka_export.packing_list_view_tree').id, 'tree'),
                (self.env.ref('jidoka_export.packing_list_view_form').id, 'form')]
        action = {
            'name': _("Packing List of %s" % (self.display_name)),
            'type': 'ir.actions.act_window',
            'res_model': 'packing.list',
            'view_mode': 'tree,form',
            'views': views,
            'context': {'create': False},
            'domain': [('id', 'in', self.packing_list_ids.ids)],
        }
        return action

    def packing_list_btn(self):
        action = self._packing_list_action_view()
        action['domain'] = [('id','in',self.packing_list_ids.ids)]
        return action
    
    def _delivery_order_action_view(self):
        views = [(self.env.ref('stock.vpicktree').id,'tree'),
                (self.env.ref('stock.view_picking_form').id,'form')]
        action = {
            'name': _("Delivery Order of %s" % (self.display_name)),
            'type': 'ir.actions.act_window',
            'res_model':'stock.picking',
            'view_mode': 'tree, form',
            'views': views,
            # 'domain': [('id','in',self.)]
            'domain': [('origin','in',self.no_sc_ids.mapped('name'))]
        }
        return action
        
    
    def delivery_order_btn(self):
        action = self._delivery_order_action_view()
        action['domain'] = [('origin','in',self.no_sc_ids.mapped('name'))]
        return action
    
    # # =================================
    # # # =======================================================================PERUBAHAN AMBIL DARI NO SC IDS========================================================================
    # @api.onchange('no_sc_ids')
    # def onchange_no_sc_ids(self):
    #     if not self.no_sc_ids:
    #         self.product_line_ids = [(5, 0, 0)]
    #     if self.no_sc_ids:
    #         self.product_line_ids = [(5, 0, 0)] # remove existing lines
    #         lines = []
    #         shipping_id = self.id
    #         for rec in self.no_sc_ids.order_line.filtered(lambda r: r.product_id.type != 'service'):
    #             qty_si = rec.product_uom_qty - rec.qty_delivered
    #             vals = {
    #                 'order_line_id':rec.id,
    #                 'order_id': rec.order_id.id,
    #                 'product_id' : rec.product_id.id,
    #                 'product_uom_qty' : rec.product_uom_qty,
    #                 'qty_delivered' : rec.qty_delivered,
    #                 'reserved' : rec.product_uom_qty,
    #                 'name'  : rec.name,
    #                 'william_fob_price' : rec.william_fob_price,
    #                 'william_set_price' : rec.william_set_price,
    #                 'sku' : rec.sku,
    #                 'shipping_id':shipping_id,
    #                 # 'shipping_id':rec.shipping_ins_ids.ids[0],
    #                 'qty_si': qty_si,
    #             }
    #             # shipping_ins = 
    #             # lines.append((0,0,vals))
    #         # self.product_line_ids = lines
    #             product_line = self.product_line_ids.create(vals)
    #             self.write({'product_line_ids':[(4,product_line.id)]})
    # # # ==================================================================================================================                

    # =================================================

class ShippingInsLine(models.Model):
    _name = 'shipping.ins.line'
    _description = 'Shipping Instruction Line'
    
    name = fields.Char(string='Description')
    sku = fields.Char('SKU')
    type = fields.Char('type')
    state_move = fields.Selection('State Move', related='move_id.state')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='State',related='shipping_id.state')
    qty_done = fields.Float('Done')
    product_uom_qty = fields.Float('Quantity SC',store=True)
    reserved = fields.Float('Reserved')
    william_fob_price = fields.Float('Single Price',store=True)
    william_set_price = fields.Float('Set Price',store=True)
    qty_done = fields.Float('Done')
    qty_si = fields.Float('Qty SI',store=True)
    total_qty_si = fields.Float(string='Total Qty SI',store=True)
    # total_qty_si = fields.Float(string='Total Qty SI', compute='_compute_total_qty_si')
    qty_selisih = fields.Float(string='Qty Selisih')
    
    shipping_id = fields.Many2one(comodel_name='shipping.ins', string='Shipping Instruction', copy=False, store=True,)
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',)
    lot_id = fields.Many2one(comodel_name='stock.production.lot', string='Lot/Serial Number', domain="[('product_id','=',product_id)]")
    location_id = fields.Many2one('stock.location', string='From', default=lambda self: self.env.ref('stock.stock_location_stock').id)
    order_id = fields.Many2one(comodel_name='sale.order', string='Order', store=True)
    move_id = fields.Many2one(comodel_name='stock.move', string='move',store=True)
    
    volume_uom_name = fields.Char('Measurement', related='product_tmpl_id.volume_uom_name')
    weight_uom_name = fields.Char('Measurement', related='product_tmpl_id.weight_uom_name')
    
    qty_delivered = fields.Float('Total Qty SJ',related='order_line_id.qty_delivered',)
    pack = fields.Float('Pack (CTN)', related='product_tmpl_id.pack')
    net_weight = fields.Float('Net Weight (KGS)', related='product_tmpl_id.net_weight',store=True)
    gross_weight = fields.Float('Gross Weight (KGS)', related='product_tmpl_id.gross_weight',store=True)
    means = fields.Float('Measurement (CBM)', related='product_tmpl_id.means',store=True)
    draft_si = fields.Float('Draft SI', 
        compute='_compute_draft_si')
    
    @api.depends('move_id.shipping_line_ids')
    def _compute_draft_si(self):
        for rec in self:
            for move in rec.move_id:
                rec.draft_si = sum(move.shipping_line_ids.mapped('qty_si'))
    
    product_tmpl_id = fields.Many2one('product.template', string='Product', related='product_id.product_tmpl_id')
    uom_id = fields.Many2one("uom.uom","Unit Of Measure", related='product_id.uom_id')
    
    
    unit_price = fields.Float('Unit Price', compute='_compute_unit_price', store=True)
    amount = fields.Float('Amount', compute='_compute_amount', store=True)
    
    order_line_id = fields.Many2one(comodel_name='sale.order.line', string='Order Line', 
        compute='_compute_order_line_id' )
    
    @api.depends('move_id')
    def _compute_order_line_id(self):
        for r in self:
            if r.move_id:
                r.order_line_id = r.move_id.sale_line_id.id
            else:
                r.order_line_id = False

    # @api.depends('order_line_id.shipping_ins_line_ids')
    # def _compute_total_qty_si(self):
    #     for rec in self:
    #         total_qty_si = 0
    #         if rec.order_line_id:
    #             total_qty_si = sum(rec.order_line_id.shipping_ins_line_ids.filtered(lambda line: line.state == 'done').mapped('qty_si'))
    #             if total_qty_si:
    #                 rec.total_qty_si = total_qty_si
    #             else:
    #                 rec.total_qty_si = 0.0
                    
    # @api.depends('order_line_id.shipping_ins_line_ids')
    # def _compute_total_qty_si(self):
    #     for rec in self:
    #         total_qty_si = 0
    #         if rec.order_line_id:
    #             for order_line in rec.order_line_id:
    #                 total_qty_si += sum(order_line.shipping_ins_line_ids.filtered(lambda line: line.state == 'done').mapped('qty_si'))
    #         rec.total_qty_si = total_qty_si
                        
    @api.depends('william_fob_price', 'william_set_price')
    def _compute_unit_price(self):
        for record in self:
            record.unit_price = record.william_fob_price + record.william_set_price

    @api.depends('product_uom_qty', 'unit_price')
    def _compute_amount(self):
        for record in self:
            record.amount = record.product_uom_qty * record.unit_price    
                    
    # @api.onchange('qty_selisih','draft_si')
    # def _onchange_qty_selisih(self):
    #     for r in self:
    #         selisih =  r.qty_selisih - r.draft_si
    #         if selisih != 0:
    #         # if selisih:
    #             # r.qty_si = selisih
    #             r.qty_si = r.qty_selisih
    #         # else:
    #         #     r.qty_si = 0.0
    
    
                
    @api.onchange('product_uom_qty','qty_delivered','qty_si')
    def _onchange_qty_si(self):
        for r in self:
            if r.product_uom_qty == r.qty_delivered:
                if r.qty_si > 0 :
                    raise ValidationError(_("you can't fill it"))
                if r.qty_si <= -1 :
                    raise ValidationError(_("you can't fill it"))
                
            if r.move_id.state == 'done':
                raise ValidationError(_("DO sudah validate, tidak bisa di edit kembali"))
    # qty_sc - total_qty_si -draft_si
    