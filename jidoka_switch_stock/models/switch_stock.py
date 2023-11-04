# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class JidokaSwitchStock(models.Model):
    _name = 'jidoka.switch.stock'
    _description = 'Jidoka Switch Stock'
    _order = 'id DESC'
    _inherit = ['mail.thread']

    name = fields.Char(string='Number', default=lambda self:_('New'), required=True,
        readonly=True, tracking=True)
    switch_date = fields.Datetime(string='Date', default=fields.Datetime.now, required=True, tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,
        required=True)
    location_id = fields.Many2one('stock.location', string="Location", required=True, tracking=True)
    description = fields.Text(string='Description')
    line_ids = fields.One2many(comodel_name='jidoka.switch.stock.line', inverse_name='switch_id',
        string='Switch Lines', copy=True)
    total_quantity = fields.Float(string='Total Quantity', compute='_compute_total_quantity')
    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'), ('done', 'Done'),], required=True, default='draft',
        tracking=True, readonly=True, copy=False)
    inventory_id = fields.Many2one(comodel_name='stock.inventory', string='Inventory Adjustment', copy=False)
    
    
    # ORM methods
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
           vals['name'] = self.env['ir.sequence'].next_by_code('jidoka.switch.stock') or _('New')
        res = super(JidokaSwitchStock, self).create(vals)
        return res
    
    def unlink(self):
        for record in self:
            if record.state in ['done']:
                raise UserError(_('You cannot delete a document is in %s state.') % (record.state,))
        return super(JidokaSwitchStock, self).unlink()
    
    # action
    def action_done(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Allowed validate only if document draft'))
            if not record.line_ids:
                raise UserError(_('Required details'))
        self._process_inventory_adjustment()
        self.write({'state': 'done'})

    def action_view_inventory_adjustment(self):
        self.ensure_one()
        if not self.inventory_id:
            raise UserError(_('Inventory Adjustment not exist'))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventory Adjustment',
            'res_model': 'stock.inventory',
            'res_id': self.inventory_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _process_inventory_adjustment(self):
        for record in self:
            product_ids = record.line_ids.mapped('product_from_id').ids + record.line_ids.mapped('product_to_id').ids
            # get current "product from" stock
            inventory = self.env['stock.inventory'].create({
                'name': record.name,
                'location_ids': [(4, record.location_id.id)],
                'product_ids': [(4, p_id) for p_id in product_ids],
                'exhausted': True, # include stock 0
                'prefill_counted_quantity': 'counted', # default dg stock
            })
            inventory.action_start()
            # loop product to reduce
            detailed_lot = {
                # 'prod_lot_id': [
                #     product_lot_name, qty
                # ]
            }
            for line in record.line_ids:
                # -- reduce stock --
                qty_to_reduced = line.quantity
                qty_reduced = 0
                inventory_line_from = inventory.line_ids.filtered(lambda l: l.product_id.id == line.product_from_id.id)
                # prevent stock 0 / not enough
                if qty_to_reduced > sum(inventory_line_from.mapped('theoretical_qty')):
                    raise ValidationError(_('Stock tidak cukup, stok %s %s') % (inventory_line_from.product_id.display_name, sum(inventory_line_from.mapped('theoretical_qty'))))
                for inv_line_to_reduce in inventory_line_from:
                    qty_remaining = qty_to_reduced - qty_reduced
                    if qty_remaining > 0.0 and inv_line_to_reduce.theoretical_qty > 0.0:
                        qty_processed = 0
                        if inv_line_to_reduce.theoretical_qty >= qty_remaining:
                            counted_qty = inv_line_to_reduce.theoretical_qty - qty_remaining
                            qty_processed = qty_remaining
                        else:
                            counted_qty = 0
                            qty_processed = inv_line_to_reduce.theoretical_qty
                        inv_line_to_reduce.product_qty = counted_qty
                        # detailed lot
                        if inv_line_to_reduce.prod_lot_id:
                            if inv_line_to_reduce.prod_lot_id.id not in detailed_lot:
                                detailed_lot[inv_line_to_reduce.prod_lot_id.id] = [
                                    inv_line_to_reduce.prod_lot_id.name, qty_processed]
                            else:
                                detailed_lot[inv_line_to_reduce.prod_lot_id.id][1] = detailed_lot[inv_line_to_reduce.prod_lot_id.id][1] + qty_processed
                        qty_reduced += qty_processed
                qty_remaining = qty_to_reduced - qty_reduced
                # jika masih ada sisa?
                if qty_remaining > 0.0:
                    raise ValidationError(_('Stock masih ada sisa %s %s') % (inventory_line_from.product_id.display_name, qty_remaining))
                
                # -- add stock --
                # loop product to add
                qty_to_add = line.quantity
                qty_added = 0
                if line.product_to_id.tracking in ['lot', 'serial']:
                    # detail with existing lot
                    if detailed_lot:
                        for k, lot_old in detailed_lot.items():
                            # create new lot
                            lot = self.env['stock.production.lot'].create({
                                'name': '%s-sw' % lot_old[0],
                                'product_id': line.product_to_id.id,
                                'company_id': self.env.company.id,
                            })
                            self.env['stock.inventory.line'].create({
                                'inventory_id': inventory.id,
                                'product_id': line.product_to_id.id,
                                'prod_lot_id': lot.id,
                                'product_qty': lot_old[1],
                                'location_id': record.location_id.id,
                            })
                            qty_added += lot_old[1]
                    # sisa qty / jika tanpa lot
                    qty_remaining = qty_to_add - qty_added
                    if qty_remaining > 0:
                        # create new lot
                        lot = self.env['stock.production.lot'].create({
                            'name': self.env['ir.sequence'].next_by_code('stock.lot.serial'),
                            'product_id': line.product_to_id.id,
                            'company_id': self.env.company.id,
                        })
                        self.env['stock.inventory.line'].create({
                                'inventory_id': inventory.id,
                                'product_id': line.product_to_id.id,
                                'prod_lot_id': lot.id,
                                'product_qty': qty_remaining,
                                'location_id': record.location_id.id,
                            })
                        qty_added += qty_remaining
                else:
                    # non-tracking
                    inventory_line_to = inventory.line_ids.filtered(lambda l: l.product_id.id == line.product_to_id.id)
                    for inv_line_to_add in inventory_line_to:
                        qty_remaining = qty_to_add - qty_added
                        if qty_remaining > 0.0:
                            # NOTE negatif dianggap 0
                            if inv_line_to_add.theoretical_qty:
                                counted_qty = inv_line_to_add.theoretical_qty + qty_remaining
                            else:
                                counted_qty = qty_remaining
                            inv_line_to_add.product_qty = counted_qty
                            qty_added += qty_remaining
                    qty_remaining = qty_to_add - qty_added
                    if qty_remaining > 0.0:
                        self.env['stock.inventory.line'].create({
                            'inventory_id': inventory.id,
                            'product_id': line.product_to_id.id,
                            'product_qty': qty_remaining,
                            'location_id': record.location_id.id,
                        })
                        qty_added += qty_remaining

            # finally, validate this inventory adjustment
            inventory.action_validate()
            record.inventory_id = inventory.id

    # compute method
    @api.depends('line_ids', 'line_ids.quantity')
    def _compute_total_quantity(self):
        for record in self:
            record.total_quantity = sum(record.line_ids.mapped('quantity'))
        
    
    

class JidokaSwitchStockLine(models.Model):
    _name = 'jidoka.switch.stock.line'
    _description = 'Jidoka Switch Stock Line'
    _rec_name = 'product_from_id'

    switch_id = fields.Many2one('jidoka.switch.stock', string="Switch Stock")
    product_from_id = fields.Many2one('product.product', string="Product From", required=True)
    product_to_id = fields.Many2one('product.product', string="Product To", required=True)
    quantity = fields.Float(string='Quantity', required=True)
    product_uom_id = fields.Many2one('uom.uom', string='UoM', related='product_from_id.uom_id')

    # constraint
    _sql_constraints = [
        (
            "switch_stock_line_uniq",
            "unique (switch_id, product_from_id)",
            "You cannot define multiple times the same Product From on an Document"
        ),
        (
            "switch_stock_line_same_product",
            "CHECK (product_from_id != product_to_id)",
            "You cannot define the same Product From - To"
        ),
    ]
