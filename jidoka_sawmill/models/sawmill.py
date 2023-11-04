from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tests import Form


from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

import json
import re
import logging
_logger = logging.getLogger(__name__)


class JidokaSawmillNotification(models.TransientModel):
    _name = 'jidoka.sawmill.noftification'
    _description = 'Notification for sawmill'
    name = fields.Char(string='Name')
    
class JidokaSawmill(models.Model):
    _name = 'jidoka.sawmill'
    _description = 'Sawmill'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date DESC'

    name = fields.Char(
        string='Name',
        required=True,
        default=lambda self: _('New'),
        copy=False,
        readonly=True,
        tracking=True
    )
    quantity = fields.Float('Lot Quantity',related='lot_id.product_qty',store=True, digits='Product Unit of Measure')
    display_quantity = fields.Float('Lot Quantity',store=True, digits='Product Unit of Measure')
    show_lots_text = fields.Boolean(default=True)
    nota = fields.Char(related='picking_id.nota', string='No. Nota', readonly=True)
    # SM from MO versi 1
    # is_sawmill_mo = fields.Boolean(string='Sawmill MO', default=False, 
    #     help="Checklist if we will sawmill from existing MO", tracking=True)
    # mo_to_sawmill_ids = fields.Many2many(comodel_name='mrp.production', relation="jidoka_sawmill_mo_rel", column1="sawmill_id", column2="mo_id", string='MO to Sawmill', 
    #     domain="[('state', 'in', ['confirmed', 'draft']), ('product_id.categ_id.is_material','=','board'),('product_id.tebal','>',0)]")
    

    # @api.onchange('mo_to_sawmill_ids')
    # def _onchange_mo_to_sawmill_ids(self):
    #     material_vals = []
    #     if self.is_sawmill_mo and self.mo_to_sawmill_ids:
    #         for mo in self.mo_to_sawmill_ids:
    #             mo_id = mo.id
    #             if 'NewId' in str(mo.id):
    #                 mo_id = int(str(mo.id)[6:])
    #             _logger.info(mo_id)
    #             material_vals.append((0, 0, {
    #                 'product_id': mo.product_id.id,
    #                 'tebal': mo.product_id.tebal,
    #                 'uom_id': mo.product_uom_id.id,
    #                 'mo_sawmill_id': mo_id, # langsung set
    #             }))
    #     self.line_ids = [(5, 0, 0)] + material_vals
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code(
                'jidoka.sawmill') or _('New')
        result = super(JidokaSawmill, self).create(vals)
        return result

    picking_id = fields.Many2one('stock.picking', string='No. Receipt', domain="[('picking_type_code','=','incoming'),('state','=','done')]", tracking=True, required=True)
    picking_id_domain = fields.Char(
        compute="_compute_picking_id_domain",
        readonly=True,
        store=False,
    )
    product_id = fields.Many2one('product.product', string='Log ID', tracking=True, required=True,store=True )
    product_id_domain = fields.Char(
        compute="_compute_product_id_domain",
        readonly=True,
        store=False,
    )

    lot_id = fields.Many2one('stock.production.lot', string='Lot', tracking=True, copy=False, )
    lot_id_domain = fields.Char(
        compute="_compute_lot_id_domain",
        readonly=True,
        store=False,
    )
    lot_name = fields.Html(string='Lot', readonly=True, store=True, copy=False)
    wood_kind_id = fields.Many2one('jidoka.woodkind', string='Jenis Kayu', related='product_id.wood_kind_id', store=True)
    certification_id = fields.Many2one('res.certification', string='Sertifikasi',  related='product_id.certification_id', store=True)
    desc = fields.Html(string='Desc')
    
    
    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        if self.lot_id:
            name = self.lot_id.name
            number = re.findall('\d{5,}', name)
            if number:
                number_str = "<b>{}</b>".format(number[0])
                name = name.replace(number[0], number_str)
            self.lot_name = "<p>{}</p>".format(name)
        if not self.lot_id and self.state == 'draft':
            self.lot_name = "<p></p>"
    
    @api.depends('product_id', 'lot_id')
    def _compute_picking_id_domain(self):
        for rec in self:
            picking_id_domain = [('picking_type_code','=','incoming'),('state','=','done')]
            if rec.product_id:
                pickings = self.env['stock.picking'].sudo().search([('picking_type_code','=','incoming'),('state','=','done')])
                picking_filter = pickings.filtered(lambda x: self.product_id.id in x.move_ids_without_package.product_id.ids)
                if picking_filter:
                    picking_id_domain = [('id', 'in', picking_filter.ids),('picking_type_code','=','incoming'),('state','=','done')]
                else: 
                    picking_id_domain = [('id','=',0)]
            check_pickings = self.env['stock.picking'].sudo().search(picking_id_domain)
            if rec.picking_id not in check_pickings:
                rec.picking_id = False
            rec.picking_id_domain = json.dumps(
                picking_id_domain
            )
    
    @api.depends('picking_id', 'lot_id')
    def _compute_product_id_domain(self):
        for rec in self:
            product_id_domain = []
            if rec.picking_id:
                product_id_domain = [('id','in', rec.picking_id.move_ids_without_package.product_id.ids)]
            check_products = self.env['product.product'].sudo().search(product_id_domain)
            if rec.product_id not in check_products:
                rec.product_id = False
            rec.product_id_domain = json.dumps(
                product_id_domain
            )

    @api.depends('product_id', 'picking_id')
    def _compute_lot_id_domain(self):
        for rec in self:
            lots = False
            lot_id_domain = [('id','=',0)]
            if rec.product_id and rec.picking_id:
                moves = rec.picking_id.move_ids_without_package
                moves = moves.filtered(lambda x: rec.product_id.id == x.product_id.id)
                lots = moves.move_line_nosuggest_ids.lot_id
                # Quantity lot tidak boleh 0
                quants = lots.filtered(lambda x: x.product_qty > 0).mapped('quant_ids')
                quants = quants.filtered(lambda q: q.location_id.usage == 'internal' or (q.location_id.usage == 'transit' and q.location_id.company_id) and q.quantity > 0)
                # Cek lot di stock.quant yang on_hand = True & onhand quantity lebih dari 0
                lots = quants.mapped('lot_id')
                # lots = lots.quant_ids.filtered(lambda x: x.on_hand == True and x.inventory_quantity > 0).lot_id
                if lots:
                    lot_id_domain = [('id','in',lots.ids)]
            check_lots = self.env['stock.production.lot'].sudo().search(lot_id_domain).ids
            if rec.lot_id.id not in check_lots:
                rec.lot_id = False
            rec.lot_id_domain = json.dumps(
                lot_id_domain
            )

    
    date = fields.Date(string='Date', default=fields.Date.today(), tracking=True)
    rendemen = fields.Float('Total Rendemen', tracking=True, compute='_compute_rendemen', store=True)
    display_rendemen = fields.Float('Total Rendemen', store=True, digits='Product Unit of Measure')
    
    @api.onchange('rendemen')
    def _onchange_rendemen(self):
        if self.state == 'draft':
            self.display_rendemen = self.rendemen
    
    @api.onchange('rendemen')
    def _onchange_lot_quantity(self):
        if self.state == 'draft':
            self.display_quantity = self.quantity
    
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')
    ], string='State',default='draft', tracking=True)
    
    count_mo_sawmill = fields.Integer('Count Mo Sawmill',compute='_compute_count_mo_sawmill')
    
    def _compute_count_mo_sawmill(self):
        for rec in self:
            mo_ids = self.env['mrp.production'].sudo().search([('sawmill_id', '=', self.id)])
            rec.count_mo_sawmill = len(mo_ids)
    
    def mo_sawmill_action_view(self):
        # views = [(self.env.ref('mrp.mrp_production_tree_view').id, 'tree'),
        #              (self.env.ref('mrp.mrp_production_form_view').id, 'form')]
        action = {
            'name': _("Manufacturing Order of %s"%(self.name)),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'tree,form',
            # 'views': views,
            'domain':[('sawmill_id','=',self.id)],
            'context': {'create': False},
        }
        return action
    
    @api.model
    def _get_default_picking_type(self):
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        picking_type =  self.env['stock.picking.type'].search([
            ('warehouse_id.company_id', '=', company_id),
            ('material_process', '=', 'sawmill')
        ], limit=1)
        if picking_type:
            return picking_type.id
        return False
        
    @api.model
    def _get_default_location_src(self):
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        picking_type =  self.env['stock.picking.type'].search([
            ('warehouse_id.company_id', '=', company_id),
            ('material_process', '=', 'sawmill')
        ], limit=1)
        if picking_type and picking_type.default_location_src_id:
            return picking_type.default_location_src_id.id
        return None
        
    @api.model
    def _get_default_location_dest(self):
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        picking_type =  self.env['stock.picking.type'].search([
            ('warehouse_id.company_id', '=', company_id),
            ('material_process', '=', 'sawmill')
        ], limit=1)
        if picking_type and picking_type.default_location_dest_id:
            return picking_type.default_location_dest_id.id
        return None

    picking_type_id = fields.Many2one(comodel_name='stock.picking.type', string='Operation Type', check_company=True, default=_get_default_picking_type, tracking=True)
    location_src_id = fields.Many2one(
        'stock.location', 'Components Location',
        default=_get_default_location_src,
        required=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        states={'draft': [('readonly', False)]}, check_company=True,
        help="Location where the system will look for components.", tracking=True)
    location_dest_id = fields.Many2one(
        'stock.location', 'Finished Products Location',
        default=_get_default_location_dest,
        required=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        states={'draft': [('readonly', False)]}, check_company=True,
        help="Location where the system will stock the finished products.", tracking=True)
    
    line_ids = fields.One2many(comodel_name='jidoka.material', inverse_name='sawmill_id', string='Details')
    
    total_done = fields.Float(string='Total Done', store=True, compute="_compute_total_done", digits='Product Unit of Measure', copy=False)
    
    @api.depends('total_done','quantity')
    def _compute_rendemen(self):
        for r in self:
            total_rendemen = 0
            if r.quantity and r.total_done:
                total_rendemen = r.total_done / r.quantity
            r.rendemen = total_rendemen
            
    @api.depends('line_ids')
    def _compute_total_done(self):
        for rec in self:
            total_done = 0
            for line in rec.line_ids:
                total_done += line.quantity
            rec.total_done = total_done
            
    
    def action_done(self):
        self.ensure_one()
        self._validate_record()
        if self.state == 'draft':
            self.write({
                'state': 'done',
                'display_quantity': self.quantity,
                'display_rendemen': self.rendemen,
            })
            self._create_mo()
            if self.lot_id.product_qty > 0:
                self.scrap_sawmill_material(self.lot_id.product_qty)
            return True
        return False
    
    def _check_data(self):
        if not self.line_ids:
            raise ValidationError(_("Detail Product cannot be empty !"))

    def action_done_and_duplicate(self, default=None):
        self.ensure_one()
        act_done = self.action_done()
        if act_done:
            new_record = super(JidokaSawmill, self).copy(default)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'jidoka.sawmill',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': new_record.id,
                'target': 'current',
            }
    
    def _create_mo(self):
        self.ensure_one()
        vals = {}
        len_success_mo = 0
        self._check_bom()
        lot_prod_qty = self.lot_id.product_qty
        mo_to_reduce = {}
        for line in self.line_ids:
            line.sudo()._generate_lot_name()
            company_id = self.company_id.id
            product_id = line.product_id.id
            domain=[
                '&',
                    '|',
                        ('company_id', '=', False),
                        ('company_id', '=', company_id),
                    '&',
                        '|',
                            ('product_id','=',product_id),
                            '&',
                                ('product_tmpl_id.product_variant_ids','=',product_id),
                                ('product_id','=',False),
                ('type', '=', 'normal')]
            bom = self.env['mrp.bom'].sudo().search(domain, limit=1)
            calc_consume = 0
            try:
                calc_consume = lot_prod_qty / self.total_done * line.quantity
            except Exception as e:
                calc_consume = 0
            calc_consume = float_round(calc_consume, precision_rounding=line.product_id.uom_id.rounding, rounding_method='HALF-UP')
            vals = {
                'product_id': line.product_id.id,
                'product_qty': line.quantity,
                'product_uom_id': line.uom_id.id,
                'bom_id': bom.id,
                'date_planned_start': datetime.now(),
                'company_id': self.company_id.id,
                'picking_type_id': self.picking_type_id.id,
                'location_src_id': self.location_src_id.id,
                'location_dest_id': self.location_dest_id.id,
                'material_process': 'sawmill',
                'sawmill_id': self.id,
                'origin':self.name
                # 'move_raw_ids': [(4,move_raw.id)]
            }
            mrp = self.env['mrp.production'].sudo().create(vals)
            mrp._default_odoo_onchange_mrp()
            mrp.sudo().action_generate_serial()
            mrp.lot_producing_id.write({
                'name': line.lot,
                'tebal': line.tebal,
                'lebar': line.lebar,
                'panjang': line.panjang,
                'product_qty': line.quantity,
                'wood_kind_id': self.product_id.wood_kind_id.id,
            })
            mrp.write({
                'qty_producing': line.quantity,
                'product_qty': line.quantity,
            })
            if not mrp.move_raw_ids:
                raise ValidationError(_('No component for Product %s !') % line.product_id.name)
            mrp.move_raw_ids[0].write({
                'product_id': self.product_id.id,
                'product_uom_qty': calc_consume
            })
            mrp.sudo().action_confirm()
            move_line_vals = mrp.move_raw_ids[0]._prepare_move_line_vals()
            move_line_vals.update({
                'location_id': self.location_src_id.id,
                'lot_id': self.lot_id.id,
                'qty_done': calc_consume
            })
            self.env['stock.move.line'].create(move_line_vals)
            mrp_done = mrp.sudo().button_mark_done()
            try:
                warn_id = mrp_done.get('id', False)
                warn = self.env['mrp.consumption.warning'].sudo().browse(warn_id)
                ctx = dict(warn.env.context)
                ctx.pop('default_mrp_production_ids', None)
                mrp.with_context(ctx, skip_consumption=True).button_mark_done()
            except Exception as e:
                _logger.error(e)
            line.write({
                'location_id': self.location_dest_id.id,
                'wood_kind_id': self.product_id.wood_kind_id.id,
                'process': 'sawmill',
                'mo_sawmill_id': mrp.id,
                'lot_id': mrp.lot_producing_id.id,
            })
            # kurangi qty mo sumber
            if line.source_mo_id:
                if line.source_mo_id.id not in mo_to_reduce:
                    mo_to_reduce[line.source_mo_id.id] = line.quantity
                else:
                    mo_to_reduce[line.source_mo_id.id] += line.quantity
            len_success_mo += 1
        if mo_to_reduce:
            for k,v in mo_to_reduce.items():
                mtr = self.env['mrp.production'].browse(k)
                if mtr.state in ('done', 'cancel'):
                    raise UserError(_('MO %s state %s is not updateable!') % (mtr.name, mtr.state))
                mtr.product_qty = mtr.product_qty - v
                if mtr.product_qty <= 0.0:
                    mtr.unlink()

    # SM from MO versi 1
    # def _update_mo(self):
    #     self.ensure_one()
    #     vals = {}
    #     len_success_mo = 0
    #     # TODO validasi jika ada yg belum punya BoM
    #     # NOTE langsung dibuatkan BoM?
    #     # self._check_bom()
    #     lot_prod_qty = self.lot_id.product_qty
    #     for line in self.line_ids:
    #         line.sudo()._generate_lot_name()
    #         calc_consume = 0
    #         try:
    #             calc_consume = lot_prod_qty / self.total_done * line.quantity
    #         except Exception as e:
    #             calc_consume = 0
    #         calc_consume = float_round(calc_consume, precision_rounding=line.product_id.uom_id.rounding, rounding_method='HALF-UP')
    #         mrp = line.mo_sawmill_id
    #         # jika perlu update qty
    #         # if mrp.product_qty != line.quantity:
    #         #     mrp.product_qty = line.quantity
    #         if not mrp.exists():
    #             raise ValidationError(_('No MO for Product %s !') % line.product_id.name)
    #         if mrp.state == 'draft':
    #             mrp.product_qty = line.quantity
    #             mrp._default_odoo_onchange_mrp()
    #         mrp.write({
    #             'qty_producing': line.quantity,
    #             # 'product_qty': line.quantity,
    #             'sawmill_id': self.id,
    #             'material_process': 'sawmill',
    #         })
    #         mrp.sudo().action_generate_serial()
    #         mrp.lot_producing_id.write({
    #             'name': line.lot,
    #             'tebal': line.tebal,
    #             'lebar': line.lebar,
    #             'panjang': line.panjang,
    #             'product_qty': line.quantity,
    #             'wood_kind_id': self.product_id.wood_kind_id.id,
    #         })
    #         # mrp.write({
    #         #     'qty_producing': line.quantity,
    #         #     # 'product_qty': line.quantity,
    #         #     'sawmill_id': self.id,
    #         #     'material_process': 'sawmill',
    #         # })
    #         if not mrp.move_raw_ids:
    #             raise ValidationError(_('No component for Product %s !') % line.product_id.name)
    #         # TODO validasi jika material to consume lebih dari 1, atau satuan salah
    #         mrp.move_raw_ids[0].write({
    #             'product_id': self.product_id.id,
    #             'product_uom_qty': calc_consume
    #         })
    #         if mrp.state == 'draft':
    #             mrp.sudo().action_confirm()
    #         move_line_vals = mrp.move_raw_ids[0]._prepare_move_line_vals()
    #         move_line_vals.update({
    #             'location_id': self.location_src_id.id,
    #             'lot_id': self.lot_id.id,
    #             'qty_done': calc_consume
    #         })
    #         self.env['stock.move.line'].create(move_line_vals)
    #         mrp_done = mrp.sudo().button_mark_done()
            
    #         # handle consumtion issue
    #         consumption_issues = mrp._get_consumption_issues()
    #         _logger.info('consumption_issues')
    #         _logger.info(consumption_issues)
    #         if consumption_issues:
    #             action = mrp._action_generate_consumption_wizard(consumption_issues)
    #             warning = Form(self.env['mrp.consumption.warning'].with_context(**action['context']))
    #             warning = warning.save()
    #             warning.action_confirm()
    #         # handle backorder
    #         backorder = Form(self.env['mrp.production.backorder'].with_context(**mrp_done['context']))
    #         backorder.save().action_backorder()

    #         mo_backorder = mrp.procurement_group_id.mrp_production_ids[-1]
    #         if mo_backorder and mo_backorder.state == 'draft':
    #             mo_backorder.onchange_product_id()
    #             mo_backorder.sudo().action_confirm()

    #         line.write({
    #             'location_id': self.location_dest_id.id,
    #             'wood_kind_id': self.product_id.wood_kind_id.id,
    #             'process': 'sawmill',
    #             # 'mo_sawmill_id': mrp.id,
    #             'lot_id': mrp.lot_producing_id.id,
    #         })
    #         len_success_mo += 1
    
    def _validate_record(self):
        self.ensure_one()
        if self.product_id and not self.product_id.wood_kind_id:
            raise ValidationError(_("Jenis Kayu is not set for this Log ID!"))
        if not self.line_ids:
            raise ValidationError(_("Products Detail cannot be empty !"))
        if self.quantity < self.total_done:
            raise ValidationError(_("Lot quantity must be greater than the total done"))
        if not self.product_id.id in self.picking_id.move_ids_without_package.product_id.ids:
            raise ValidationError(_("{} not found in {}".format(self.product_id.name, self.picking_id.name)))
        if not self.lot_id.product_id.id == self.product_id.id:
            raise ValidationError(_("{} is not a valid lot for {}".format(self.lot_id.name, self.product_id.name)))
        moves = self.picking_id.move_ids_without_package
        moves = moves.filtered(lambda x: self.product_id.id == x.product_id.id)
        lots = moves.move_line_nosuggest_ids.lot_id.ids
        if not self.lot_id.id in lots:
            raise ValidationError(_("{} not found in {}".format(self.lot_id.name, self.picking_id.name)))
        
    def _check_bom(self):
        bom_not_found = []

        for line in self.line_ids:
            company_id = self.company_id.id
            product_id = line.product_id.id
            domain=[
                '&',
                    '|',
                        ('company_id', '=', False),
                        ('company_id', '=', company_id),
                    '&',
                        '|',
                            ('product_id','=',product_id),
                            '&',
                                ('product_tmpl_id.product_variant_ids','=',product_id),
                                ('product_id','=',False),
                ('type', '=', 'normal')]
            bom = self.env['mrp.bom'].sudo().search(domain, limit=1)
            if not bom:
                lot_prod_qty = self.lot_id.product_qty
                calc_consume = 0
                try:
                    calc_consume = lot_prod_qty / self.total_done * line.quantity
                except Exception as e:
                    calc_consume = 0
                calc_consume = float_round(calc_consume, precision_rounding=line.product_id.uom_id.rounding, rounding_method='HALF-UP')
                bom_line = {
                    'product_id': self.product_id.id,
                    'product_qty': calc_consume,
                    'product_uom_id': self.product_id.uom_id.id,
                }
                product_id = line.product_id
                product_tmpl = False
                product_variant = False
                if not product_id.product_tmpl_id:
                    product_tmpl = product_id.id
                else:
                    product_tmpl = product_id.product_tmpl_id.id
                    product_variant = product_id.id
                bom = self.env['mrp.bom']
                bom.sudo().create({
                    'product_tmpl_id': product_tmpl,
                    'product_id': product_variant,
                    'product_qty': line.quantity,
                    'product_uom_id': line.uom_id.id,
                    'type': 'normal',
                    'company_id': company_id,
                    'bom_line_ids': [(0, 0, bom_line)]
                })
        return    
    
    def _get_unique_lines(self):
        unique_lines = []
        unique_combinations = set()
        for line in self.line_ids:
            combination = (line.product_id.id, line.panjang, line.lebar)
            if combination not in unique_combinations:
                unique_combinations.add(combination)
                unique_lines.append(line)
        return unique_lines

    def generate_multi_product(self):
        
        unique_lines = self._get_unique_lines()
        wizard_lines = []
        
        for line in unique_lines:
        # Menghitung total untuk setiap produk unique pada line_ids
            filtered_lines = self.line_ids.filtered(lambda l: l.product_id == line.product_id and l.panjang == line.panjang and l.lebar == line.lebar)
            total = sum(filtered_lines.mapped('total'))

            wizard_line = (0, 0, {
                'product_id': line.product_id.id,
                'total': total,
                'panjang': line.panjang,
                'lebar': line.lebar,
                'quantity': line.quantity,
            })
            wizard_lines.append(wizard_line)
        
        # if not wizard_lines:


            # self.line_ids.unlink() 

        wizard_vals = {
            'sawmill_id': self.id,
            'line_ids': wizard_lines,
        }
        
        return {
            'name': _('Generate Multi Detail Product Sawmill'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wiz.multi.line.sawmill',
            'target': 'new',
            'context': {'default_sawmill_id': self.id},
            'res_id': self.env['wiz.multi.line.sawmill'].create(wizard_vals).id,
        }


        
    def scrap_sawmill_material(self, scrap_qty):
        scrap = self.env['stock.scrap']
        scrap_location_id = self.env['stock.location'].sudo().search([('scrap_location','=',True),('company_id','in',[self.company_id.id])], limit=1)
        if not scrap_location_id:
            raise ValidationError(_("Scrap location not found."))
        scrap = scrap.sudo().create({
            'product_id': self.product_id.id,
            'scrap_qty': scrap_qty,
            'product_uom_id': self.product_id.uom_id.id,
            'location_id': self.location_src_id.id,
            'scrap_location_id': scrap_location_id.id,
            'origin': self.name,
            'company_id': self.company_id.id,
            'lot_id': self.lot_id.id,
            'sawmill_id':self.id,
        })
        if scrap:
            scrap.sudo().action_validate()
            return True
        return False
    
    def action_sawmill_scrap_view(self):
        return {
            'name': _(' Sawmill Scrap'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.scrap',
            'domain': [('sawmill_id', '=', self.id)],
        }
        

    # def debug(self):
    #     import pdb;pdb.set_trace()
    #     return
        
    
class JidokaSawmillMaterial(models.Model):
    _inherit = 'jidoka.material'
    
    sawmill_id = fields.Many2one(comodel_name='jidoka.sawmill', string='Sawmill')
    mo_sawmill_id = fields.Many2one(comodel_name='mrp.production', string='MO Sawmill')
    source_mo_id = fields.Many2one(comodel_name='mrp.production', string='Source MO')
    total = fields.Integer('total', store=True)
    wiz_ref = fields.Reference(string='Wizard Reference', selection=[('option1', 'Opsi 1'), ('option2', 'Opsi 2'), ('option3', 'Opsi 3')])
    
                
    def _generate_lot_name(self):
        seq = self.env['ir.sequence'].next_by_code('jidoka.sawmill.line.lot')
        self.lot = '{}x{}x{}-{}'.format(self.tebal, self.panjang, self.lebar, seq)



    
class JidokaSawmillScrap(models.Model):
    _inherit = 'stock.scrap'
    
    sawmill_id = fields.Many2one(comodel_name='jidoka.sawmill', string='Sawmill')
    
        