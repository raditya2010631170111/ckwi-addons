# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

from re import findall as regex_findall
from re import split as regex_split
from collections import Counter, defaultdict

class MrpSawmill(models.Model):
    _name = 'mrp.sawmill'
    _description = 'Mrp Sawmill'


    @api.model
    def _get_default_picking_type(self):
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        return self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'),
            ('warehouse_id.company_id', '=', company_id),
        ], limit=1).id

    @api.model
    def _get_default_location_src_id(self):
        location = False
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        if self.env.context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(self.env.context['default_picking_type_id']).default_location_src_id
        if not location:
            location = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1).lot_stock_id
        return location and location.id or False

    @api.model
    def _get_default_location_dest_id(self):
        location = False
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        if self._context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(self.env.context['default_picking_type_id']).default_location_dest_id
        if not location:
            location = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1).lot_stock_id
        return location and location.id or False

    name = fields.Char('Name',default='New',copy=False)
    mo_id = fields.Many2many('sale.order', string='No. MO')
    picking_id = fields.Many2one('stock.picking', string='No. Nota', domain="[('picking_type_code','=','incoming'),('state','=','done')]")
    product_id = fields.Many2one('product.product', string='Log ID',domain="[('id','=',False)]")
    rub_date = fields.Date('Tgl Gesek',default=fields.Date.today())
    workorder_id = fields.Many2many('mrp.production', string='Work Order')
    is_all_ready_mo = fields.Boolean('Is All Ready Mo?')
    rendemen = fields.Float('Rendemen')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)    
    line_ids = fields.One2many('mrp.sawmill.line', 'mrp_sawmill_id', string='line')
    line_detail_ids = fields.One2many('mrp.sawmill.line.detail', 'mrp_sawmill_id', string='line Detail')
    move_ids = fields.One2many('stock.move', 'mrp_sawmill_id', string='line',domain=[('state','!=','cancel')])
    location_src_id = fields.Many2one(
        'stock.location', 'Components Location',
        default=_get_default_location_src_id,
        readonly=True, required=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        states={'draft': [('readonly', False)]}, check_company=True,
        help="Location where the system will look for components.")
    location_dest_id = fields.Many2one(
        'stock.location', 'Finished Products Location',
        default=_get_default_location_dest_id,
        readonly=True, required=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        states={'draft': [('readonly', False)]}, check_company=True,
        help="Location where the system will stock the finished products.")
    lot_ids = fields.Many2many('stock.production.lot', string='Lots',domain="[('id','=',False)]")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')
    ], string='State',default='draft')
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        domain="[('code', '=', 'mrp_operation'), ('company_id', '=', company_id)]",
        default=_get_default_picking_type, required=True, check_company=True,
        readonly=True, states={'draft': [('readonly', False)]})
    picking_type_code = fields.Selection(
        related='picking_type_id.code',
        readonly=True)
    show_lots_text = fields.Boolean(default=True)
    immediate_transfer = fields.Boolean(default=False)
    is_all_mo = fields.Boolean('Select All?')
    mo_sawmill_ids = fields.One2many('mrp.production', 'mrp_sawmill_id', string='Mo Sawmill')
    count_mo_sawmill = fields.Integer('Count Mo Sawmill',compute='_compute_count_mo_sawmill_ids')
    
    @api.depends('mo_sawmill_ids')
    def _compute_count_mo_sawmill_ids(self):
        for rec in self:
            rec.count_mo_sawmill = len(rec.mo_sawmill_ids.ids)

    def mrp_sawmill_action_view(self):
        views = [(self.env.ref('mrp.mrp_production_tree_view').id, 'tree'),
                     (self.env.ref('mrp.mrp_production_form_view').id, 'form')]
        action = {
            'name': _("Manufacturing Order of %s"%(self.display_name)),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'tree,form',
            'views': views,
            'domain':[('id','in',self.mo_sawmill_ids.ids)],
            'context': {'create': False},
        }
        return action

    def button_draft(self):
        self.ensure_one()
        self.state = 'draft'

    def button_confirm(self):
        # import pdb; pdb.set_trace()
        self.ensure_one()
        # self.line_ids.line_details_ids._create_and_assign_production_lot()
        # for line in self.line_ids:
        #     move_id = self.env['stock.move'].create(line._prepare_stock_move_vals())
        #     print(">>>>>>>>>>>> quantity_done",move_id.quantity_done)
        #     # move_id._action_confirm()
        #     move_id._action_assign()
        #     QTY_DONE = line.line_details_ids.mapped('qty_done')
        #     LOT_NAME = line.line_details_ids.mapped('lot_name')
        #     count = 0
        #     for move_line in move_id.move_line_ids:
        #         move_line.write({
        #             'qty_done':QTY_DONE[count],
        #             'lot_name':LOT_NAME[count]})
        #         count += 1
        #         move_line._action_done()
        #     move_id._action_done(cancel_backorder=True)
        MOVE_LINE = self.env['stock.move.line']
        for line in self.line_ids:
            vals = {
                    'product_id': line.product_id.id,
                    'product_qty': line.quantity_done,
                    'product_uom_id':line.product_uom.id,
                    'origin': self.name,
                    'mrp_sawmill_id':self.id
                }
            mrp = self.env['mrp.production'].create(vals)
            mrp.onchange_company_id()
            mrp.onchange_product_id()
            mrp._onchange_product_qty()
            mrp._onchange_bom_id()
            mrp._onchange_date_planned_start()
            mrp._onchange_move_raw()
            mrp._onchange_move_finished_product()
            mrp._onchange_move_finished()
            mrp._onchange_location()
            mrp._onchange_location_dest()
            mrp.onchange_picking_type()
            mrp._onchange_producing()
            mrp._onchange_lot_producing()
            mrp._onchange_workorder_ids()
            if mrp:
                mrp.write({'product_qty': line.quantity_done})
                if mrp.move_raw_ids:
                    move_id = mrp.move_raw_ids[0]
                    move_id.product_id = self.product_id.id
                    move_id.product_uom_qty = 0
                    for detail in self.line_detail_ids:
                        move_id.product_uom_qty = move_id.product_uom_qty + detail.qty_done
                        move_line_vals = move_id._prepare_move_line_vals()
                        move_line_vals.update({
                            'lot_id' : detail.consume_lot_id.id,
                            'qty_done' : detail.qty_done
                        })
                        MOVE_LINE.create(move_line_vals)
                else:
                    raise UserError(_('Please input BOM for the finish goods product.'))
                # mrp.move_raw_ids = [(5,0)]
                # self._get_moves_raw_values(mrp)
        self.state = 'done'
                
    def _get_moves_raw_values(self, mrp):
        # moves = []
        raw_vals = []
        for detail in self.line:
            raw = mrp._get_move_raw_values(
                    detail.consume_lot_id.product_id,
                    detail.qty_done,
                    detail.consume_lot_id.product_id.uom_id
                )
        move_id = self.env['stock.move'].create(raw)
        move_id._prepare_move_line_vals()
            # moves.append((0,0,raw))
        # return moves

    @api.model
    def create(self, vals):
        res = super(MrpSawmill, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.mrp.sawmil') or '/'
                rec.name = seq
        return res
    
    @api.onchange('workorder_id')
    def _onchange_workorder_id(self):
        if self.workorder_id:
            if self.location_dest_id:
                vals = [(5,0)]
                for line in self.workorder_id.mapped('move_raw_ids'):
                    vals.append((0,0,{
                        'product_id':line.product_id.id,
                        'product_uom_qty':line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'location_id':self.location_src_id.id,
                        'location_dest_id':self.location_dest_id.id,
                        'company_id':self.company_id.id,
                        'next_serial_count':len(self.lot_ids.ids),
                        'mrp_sawmill_id':self.id
                    }))
                self.line_ids = vals
            else:
                raise UserError(_('Please input destionation location before choose MO.'))
    
    @api.onchange('is_all_mo')
    def _onchange_is_all_mo(self):
        if self.is_all_mo:
            mo_ids = self.env['mrp.workorder'].search([('workcenter_id.name','=','Sawmill')]).mapped('production_id')
            self.workorder_id = [(6,0,mo_ids.ids)]
    
    @api.onchange('picking_id')
    def _onchange_picking_id(self):
        res = {'domain':{'product_id':[('id','=',False)]}}
        if self.picking_id:
            list_product = self.picking_id.move_ids_without_package.mapped('product_id').ids
            if list_product:
                res = {'domain':{'product_id':[('id','in',list_product)]}}
        return res

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            lots = self.picking_id.move_ids_without_package.filtered(lambda r: r.product_id == self.product_id).mapped('lot_ids').ids
            if lots:
                self.lot_ids = [(6,0,lots)]

    
class MrpSawmillLine(models.Model):
    _name = 'mrp.sawmill.line'
    _description = 'Mrp Sawmill Line'

    mrp_sawmill_id = fields.Many2one('mrp.sawmill', string='Sawmill')
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product', string='Product')
    product_uom_qty = fields.Float(
        'Demand',
        digits='Product Unit of Measure',
        default=0.0, required=True,
        help="This is the quantity of products from an inventory "
             "point of view. For moves in the state 'done', this is the "
             "quantity of products that were actually moved. For other "
             "moves, this is the quantity of product that is planned to "
             "be moved. Lowering this quantity does not generate a "
             "backorder. Changing this quantity on assigned moves affects "
             "the product reservation, and should be done with care.")
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure', required=True, domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    # TDE FIXME: make it stored, otherwise group will not work
    quantity_done = fields.Float('Quantity Done', compute='_quantity_done_compute', digits='Product Unit of Measure')
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template',
        related='product_id.product_tmpl_id', readonly=False,
        help="Technical: used in views")
    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        auto_join=True, index=True, required=True,
        check_company=True,
        help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations.")
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location',
        auto_join=True, index=True, required=True,
        check_company=True,
        help="Location where the system will stock the finished products.")
    next_serial = fields.Char('First SN')
    next_serial_count = fields.Integer('Number of SN')
    # lot_ids = fields.Many2many('stock.production.lot', compute='_compute_lot_ids', inverse='_set_lot_ids', string='Serial Numbers', readonly=False)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    line_details_ids = fields.One2many('mrp.sawmill.line.detail', 'mrp_sawmill_line_id', string='Line Details')
    material_dimention_ids = fields.Many2many('res.material.dimention', string='Material Dimention')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm')
    ], string='State',related='mrp_sawmill_id.state')
    packaging_id = fields.Many2one(
        'product.packaging', 'Package Type', index=True, check_company=True)
    
    product_pcs = fields.Integer('Pcs', 
        compute='_compute_product_pcs' )
    
    @api.depends('line_details_ids')
    def _compute_product_pcs(self):
        for r in self:
            r.product_pcs = len(r.line_details_ids)

    def _prepare_stock_move_vals(self):
        self.ensure_one()
        date_planned = self.mrp_sawmill_id.rub_date
        return {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.mrp_sawmill_id.name or '')[:2000],
            'product_id': self.product_id.id,
            'date': date_planned,
            'date_deadline': date_planned,
            'location_id': self.mrp_sawmill_id.location_src_id.id,
            'location_dest_id': self.mrp_sawmill_id.location_dest_id.id,
            'mrp_sawmill_id': self.mrp_sawmill_id.id,
            'partner_id': self.mrp_sawmill_id.picking_id.partner_id.id,
            # 'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'confirmed',
            # 'purchase_line_id': self.id,
            'company_id': self.company_id.id,
            # 'price_unit': price_unit,
            'picking_type_id': self.mrp_sawmill_id.picking_type_id.id,
            # 'group_id': self.order_id.group_id.id,
            'origin': self.mrp_sawmill_id.name,
            # 'description_picking': description_picking,
            'propagate_cancel': True,
            'warehouse_id': self.mrp_sawmill_id.picking_type_id.warehouse_id.id,
            'product_uom_qty': self.product_uom_qty,
            # 'quantity_done':self.quantity_done,
            'product_uom': self.product_uom.id,
            'sequence': self.sequence,
            'purchase_line_id':False
        }
    
    @api.depends('line_details_ids.qty_done')
    def _quantity_done_compute(self):
        for rec in self:
            res = 0.00
            if len(rec.line_details_ids)>0:
                res = sum([x.qty_done for x in rec.line_details_ids])
            rec.quantity_done = res

    def action_show_details(self):
        """ Returns an action that will open a form view (in a popup) allowing to work on all the
        move lines of a particular move. This form view is used when "show operations" is not
        checked on the picking type.
        """
        self.ensure_one()

        # If "show suggestions" is not checked on the picking type, we have to filter out the
        # reserved move lines. We do this by displaying `move_line_nosuggest_ids`. We use
        # different views to display one field or another so that the webclient doesn't have to
        # fetch both.
        view = self.env.ref('jidoka_manufacturing.view_mrp_sawmill_line_operations')

        return {
            'name': _('Detailed Operations'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mrp.sawmill.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context,
                # show_owner=self.picking_type_id.code != 'incoming',
                # show_lots_m2o=self.has_tracking != 'none' and (picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),  # able to create lots, whatever the value of ` use_create_lots`.
                # show_lots_text=self.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
                # show_source_location=self.picking_type_id.code != 'incoming',
                # show_destination_location=self.picking_type_id.code != 'outgoing',
                # show_package=not self.location_id.usage == 'supplier',
                # show_reserved_quantity=self.state != 'done' and not self.picking_id.immediate_transfer and self.picking_type_id.code != 'incoming'
            ),
        }
    
    def action_assign_serial_show_details(self):
        """ On `self.move_line_ids`, assign `lot_name` according to
        `self.next_serial` before returning `self.action_show_details`.
        """
        self.ensure_one()
        if not self.next_serial:
            raise UserError(_("You need to set a Serial Number before generating more."))
        self._generate_serial_numbers()
        return self.action_show_details()

    def action_clear_lines_show_details(self):
        """ Unlink `self.move_line_ids` before returning `self.action_show_details`.
        Useful for if a user creates too many SNs by accident via action_assign_serial_show_details
        since there's no way to undo the action.
        """
        self.ensure_one()
        self.line_details_ids.unlink()
        return self.action_show_details()

    def _generate_serial_sawmill_line_details_commands(self, lot_names, material_dimention_ids):
        self.ensure_one()
        LINE_DETAIL = self.env['mrp.sawmill.line.detail']
        vals= []
        count=0
        for material in material_dimention_ids:
            vals.append((0,0,{
                'mrp_sawmill_id':self.mrp_sawmill_id.id,
                'mrp_sawmill_line_id':self.id,
                'product_id':self.product_id.id,
                'product_uom_id':self.product_uom.id,
                'material_dimention_id':material.id,
                'lot_name':lot_names[count],
                'qty_done':material.kubikasi,
            }))
            count=count+1
        return vals

    def _generate_serial_numbers(self, next_serial_count=False):
        """ This method will generate `lot_name` from a string (field
        `next_serial`) and create a move line for each generated `lot_name`.
        """
        self.ensure_one()
        if not next_serial_count:
            next_serial_count = self.next_serial_count
        # We look if the serial number contains at least one digit.
        caught_initial_number = regex_findall("\d+", self.next_serial)
        if not caught_initial_number:
            raise UserError(_('The serial number must contain at least one digit.'))
        # We base the serie on the last number find in the base serial number.
        initial_number = caught_initial_number[-1]
        padding = len(initial_number)
        # We split the serial number to get the prefix and suffix.
        splitted = regex_split(initial_number, self.next_serial)
        # initial_number could appear several times in the SN, e.g. BAV023B00001S00001
        prefix = initial_number.join(splitted[:-1])
        suffix = splitted[-1]
        initial_number = int(initial_number)
        
        lot_names = []
        for i in range(0, next_serial_count):
            lot_names.append('%s%s%s' % (
                    prefix,
                    self.env['ir.sequence'].next_by_code('stock.lot.serial'),
                    suffix
                ))
        sawmill_line_details = self._generate_serial_sawmill_line_details_commands(lot_names,self.material_dimention_ids)
        self.write({'line_details_ids': sawmill_line_details})
        return True

class MrpSawmillLineDetail(models.Model):
    _name = 'mrp.sawmill.line.detail'
    _description = 'Mrp Sawmill Line Detail'

    mrp_sawmill_id = fields.Many2one('mrp.sawmill', string='Sawmill')
    mrp_sawmill_line_id = fields.Many2one('mrp.sawmill.line', string='Sawmill Lines')
    product_id = fields.Many2one('product.product', 'Product', ondelete="cascade", check_company=True, domain="[('type', '!=', 'service'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", index=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=True, domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    material_dimention_id = fields.Many2one('res.material.dimention', string='Material Dimention')
    qty_done = fields.Float('Done', default=0.0, digits='Product Unit of Measure', copy=False)
    lot_ids = fields.Many2many('stock.production.lot',related='mrp_sawmill_id.lot_ids' ,string='Lots',domain="[('id','=',False)]")
    consume_lot_id = fields.Many2one('stock.production.lot', string='Consume S/N')
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number',
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]", check_company=True)
    lot_name = fields.Char('Lot/Serial Number Name')
    result_package_id = fields.Many2one(
        'stock.quant.package', 'Tag Card',
        ondelete='restrict', required=False, check_company=True,
        domain="['|', '|', ('location_id', '=', False), ('location_id', '=', location_dest_id), ('id', '=', package_id)]",
        help="If set, the operations are packed into this package")
    location_id = fields.Many2one('stock.location', 'From', check_company=True, required=True)
    location_dest_id = fields.Many2one('stock.location', 'To', check_company=True, required=True)
    tracking = fields.Selection(related='product_id.tracking', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    move_line_id = fields.Many2one('stock.move.line', string='Move Line')

    @api.constrains('lot_id', 'product_id')
    def _check_lot_product(self):
        for line in self:
            if line.lot_id and line.product_id != line.lot_id.sudo().product_id:
                raise ValidationError(_(
                    'This lot %(lot_name)s is incompatible with this product %(product_name)s',
                    lot_name=line.lot_id.name,
                    product_name=line.product_id.display_name
                ))

    @api.constrains('qty_done')
    def _check_positive_qty_done(self):
        if any([ml.qty_done < 0 for ml in self]):
            raise ValidationError(_('You can not enter negative quantities.'))

    def _create_and_assign_production_lot(self):
        """ Creates and assign new production lots for move lines."""
        lot_vals = []
        key_to_index = {}  # key to index of the lot
        key_to_mls = defaultdict(lambda: self.env['mrp.sawmill.line.detail'])  # key to all mls
        for ml in self:
            key = (ml.company_id.id, ml.product_id.id, ml.lot_name)
            key_to_mls[key] |= ml
            if ml.tracking != 'lot' or key not in key_to_index:
                key_to_index[key] = len(lot_vals)
                lot_vals.append({
                    'company_id': ml.company_id.id,
                    'name': ml.lot_name,
                    'product_id': ml.product_id.id,
                    'product_qty':ml.qty_done
                })
        # lots = self.env['stock.production.lot'].create(lot_vals)
        # for key, mls in key_to_mls.items():
        #     mls._assign_production_lot(lots[key_to_index[key]].with_prefetch(lots._ids))  # With prefetch to reconstruct the ones broke by accessing by index
