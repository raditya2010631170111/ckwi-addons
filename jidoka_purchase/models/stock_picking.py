from re import split as regex_split
from re import findall as regex_findall
from odoo import models, fields, api,  _
from odoo.exceptions import UserError
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import logging
_logger = logging.getLogger(__name__)
import datetime
import pytz
from odoo.tests import Form


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    grading_summary_count = fields.Integer(
        compute="_compute_grading_summary_count", string='Summary Count', copy=False, default=0, store=True)
    grading_summary_ids = fields.One2many(
        'grading.summary', 'picking_id', string='Grading Summary')
    account_move_ids = fields.One2many('account.move', 'stock_picking_id', string='account_move', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('grading', 'Grading'), # new state
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")
    grading_done = fields.Boolean('Grading Done', default=False, copy=False)
    cek_button = fields.Char('cek_button', compute='_compute_cek_button', store=True)
    is_kayu = fields.Boolean('Is Kayu', readonly=True, store=True)
    # is_qc_id = fields.Boolean('Is QC', readonly=True, store=True)
    is_qc_id = fields.Boolean('Is QC', store=True)

    show_c = fields.Boolean('show aja')
    # list penerimaan manual, sebelum di generate
    receive_list_operation_ids = fields.One2many(
        comodel_name='receive.list.operation', inverse_name='picking_id', string='Operations To Move Lines')
    next_serial = fields.Char('First SN', compute='_compute_next_serial')
    wood_type = fields.Selection([
        ('log', 'LOG'),
        ('square', 'Square Log'),
        ('timber', 'Sawn Timber')], string='Type', related='product_id.wood_type', store=True)
    
    container = fields.Char('Container')
    container_no = fields.Char('No. Container')
    seal_no = fields.Char('Seal No.')
    

    @api.depends('partner_id', 'partner_id.supplier_code_id', 'depart_no')
    def _compute_next_serial(self):
        local_timezone = pytz.timezone(self.env.user.tz)
        current_date = datetime.datetime.now(local_timezone)
        month = current_date.strftime('%m')
        year = current_date.strftime('%y')
        for record in self:
            for r in record.partner_id:
                if not record.next_serial:
                    if not r.supplier_code_id:
                            raise UserError("Please fill in the Supplier Code first in Vendor.")
                    record.next_serial = r.supplier_code_id.code + '-' + month + '-' + year + '-' + str(self.depart_no) + '-' 

    # @api.depends('purchaser.order')
    def _compute_cek_button(self):
        # grading = self.env['grading.summary'].search([('purchase_id','=',self.origin)])
        for r in self:
            # TODO perlu review, kenapa mencari berdasarkan origin?
            r.cek_button = r.env['grading.summary'].search([('purchase_id', '=', r.origin)], limit=1).state
            # r.cek_button = grading.state

    # NOTE set state to grading
    def button_grading(self):
        # self.write({'state': 'grading', 'grading_done': True})
        self.write({'state': 'grading', 'grading_done': False, 'show_validate': False})
        moves = self.move_ids_without_package
        if moves:
            for move in moves:
                if move.quantity_done == 0:
                    raise ValidationError(_("Data Done Empty !!!"))
                
    # NOTE tidak dipakai?
    # TODO need review
    def button_done_grading(self):
        if not self.grading_summary_ids:
            raise UserError(_(
                'Please Grading Summary First.'))
        self.state = 'assigned'
        self.grading_done = True
        self.show_validate = True
        self.is_qc = False
    
    # NOTE saat setelah grading terbuat, assign manual? agar bs validate picking
    # TODO need review, seharusnya assign default odoo
    # Grading Finish
    def done_button1(self):
        # import pdb;pdb.set_trace()
        self.write({
            'state' : 'assigned',
            'grading_done' : True,
            'show_validate' : True,
            'is_qc' : False, # ???
        })


    # * reviewed
    @api.depends('grading_summary_ids')
    def _compute_grading_summary_count(self):
        for order in self:
            order.grading_summary_count = len(order.grading_summary_ids)

    # * reviewed
    def _prepare_grading_summary(self):
        lines = []
        for move in self.move_ids_without_package:
            write_name = True
            COL_MASTER_HASIL = set(move.move_line_nosuggest_ids.mapped('master_hasil'))
            COL_WOOD_CLASS = set(move.move_line_nosuggest_ids.mapped('wood_class_id.id'))
            # COL_WOOD_CLASS.add(False) #reyhan

            # _logger.info('======COL_WOOD_CLASS================')
            # _logger.info(COL_WOOD_CLASS)
            # import pdb;pdb.set_trace()
            # print(COL_MASTER_HASIL)
            
            for col in COL_MASTER_HASIL:
                for col_w in COL_WOOD_CLASS:
                    MASTER_HASIL = move.move_line_nosuggest_ids.filtered(lambda r: r.master_hasil == col and r.wood_class_id.id == col_w)
                    # purchase_order_line = move.purchase_line_id
                    # import pdb;pdb.set_
                    if not len(MASTER_HASIL):
                        continue
                    move_line_obj = {
                        'product_id':move.product_id.id,
                        'price_unit':move.purchase_line_id.price_unit,
                        'move_id':move.id,
                        'qty_pcs' : len(MASTER_HASIL),
                        'qty_kubikasi':sum([x.qty_done for x in MASTER_HASIL]),
                        'master_hasil':col,
                        'wood_class_id':col_w,
                        # 'name':move.description_picking,
                        'name':move.name,
                        # 'product_uom_qty':move.product_u
                        # TIDAK DIPAKAI SEMENTARA
                        # 'fee':move.purchase_line_id.fee,
                        # 'taxes_id':move.purchase_line_id.taxes_id.ids,
                        # 'account_analytic_id':move.purchase_line_id.account_analytic_id.id,
                        # 'required':True
                    } 
                    
                    if write_name:
                        move_line_obj.update({'product_name': move.product_id.display_name})
                        write_name = False
                    lines.append([0,0,move_line_obj])
        return{
            'name':'New',
            'partner_id':self.partner_id.id,
            'purchase_id':self.purchase_id.id,
            'grading_summary_line_ids':lines,
            'picking_id':self.id,
            'truck':self.plat_no,
            'nota':self.nota,
            'certification_id' :self.certification_id.id,
        }

    # * reviewed
    def btn_create_grading_summary(self):
        # import pdb;pdb.set_trace()
        # self.grading_done = True
        self.write({'grading_done':True})
        res = self._prepare_grading_summary()
        grading_id = self.env['grading.summary'].create(res)
        grading_id.onchange_partner_id()
        grading_id.grading_summary_line_ids._product_id_change()
        action = self._grading_summary_action_view()
        action['res_id'] = grading_id.id
        action['view_mode'] = 'form'
        action['views'] = [(self.env.ref('jidoka_purchase.grading_summary_view_form').id, 'form')]
        # gs_sum_lines = self.env['grading.summary1.line']._create_product_line_group(grading_id.grading_summary_line_ids)
        # if gs_sum_lines:
        #     grading_id.write({
        #         'grading_summary_line1_ids': gs_sum_lines,
        #     })
        # moves = self.move_ids_without_package
        # move_lines = self.move_line_nosuggest_ids
        # if moves:
        #     for move in moves:
        #         # move.quantity_done
        #         if self.product_id:
        #             if move.product_id.wood_type == "log":
        #                 if  not move.quantity_done:
        #                     raise ValidationError(_("Data Done Empty !!!"))
        #                 elif move.product_id.wood_type == "square":
        #                     if move.quantity_done:
        #                         raise ValidationError(_("Data Done Empty !!!"))
        #                 elif move.product_id.wood_type == "timber":
        #                     if move.quantity_done:
        #                         raise ValidationError(_("Data Done Empty !!!"))

        # if move_lines:
        #     for move_line in move_lines:
        #         if self.product_id:
        #             if move_line.product_id.wood_type == "log":
        #                 # if not move_line.lot_name or not move_line.size_log_id or not move_line.master_hasil:
        #                 if not move_line.lot_name  or not move_line.master_hasil:
        #                     raise ValidationError(_("Data cannot be blank in the operation details, please fill in everything for the grading process !!!"))
        #                 elif move_line.product_id.wood_type == "square":
        #                     # if not move_line.lot_name or not move_line.size_log_id or not move_line.master_hasil:
        #                     if not move_line.lot_name or not move_line.master_hasil:
        #                         raise ValidationError(_("Data cannot be blank in the operation details, please fill in everything for the grading process !!!"))
        #                 elif move_line.product_id.wood_type == "timber":
        #                     if not move_line.lot_name or not move_line.master_hasil or not move_line.panjang or not move_line.tinggi or not move_line.lebar or not move_line.qty_received :
        #                         raise ValidationError(_("Data cannot be blank in the operation details, please fill in everything for the grading process !!!"))

        return action
    
    # * reviewed
    def _grading_summary_action_view(self):
        views = [(self.env.ref('jidoka_purchase.grading_summary_view_tree').id, 'tree'),
        (self.env.ref('jidoka_purchase.grading_summary_view_form').id, 'form')]
        action = {
            'name': _("Grading Summary of %s" % (self.display_name)),
            'type': 'ir.actions.act_window',
            'res_model': 'grading.summary',
            'view_mode': 'tree,form',
            'views': views,
            'context': {'create': False},
        }
        return action

    # * reviewed
    def action_view_grading_summary(self):
        action = self._grading_summary_action_view()
        action['domain'] = [('id','in',self.grading_summary_ids.ids)]
        return action

    def generate_operation(self):
        self.show_check_availability= False
        self.show_c = False
        self.show_validate = False
        self.ensure_one()
        if not self.partner_id.supplier_code_id:
                raise UserError("Please fill in the supplier code first.")
        self.move_line_ids_without_package.unlink()
        if self.picking_type_code != 'internal':
            if not self.partner_id.supplier_code_id:
                raise UserError("Please fill in the supplier code first.")
            if not self.partner_id:
                    raise UserError("Please input Supplier before assign serial number.")
        if not self.receive_list_operation_ids:
            return
            # raise UserError("Please input Receive List first.")
        for op in self.receive_list_operation_ids:
            if op.qty < 1:
                raise ValidationError(_('Qty is required'))
            for n in range(op.qty):
                # TODO seharusnya perlu check product apakah di tracking atau tidak
                lot_name = self.env['ir.sequence'].next_by_code('stock.lot.serial') or '/'
                serial = self.next_serial + lot_name[-5:] 
                
                _logger.info("====================serial====================")
                _logger.info(serial)

                sn = self.env['stock.production.lot'].create({
                    'name': serial,
                    'product_id': op.product_id.id,
                    'ref': op.picking_id.name,
                    'company_id':self.company_id.id
                })

                new_sml = self.move_line_ids_without_package.sudo().create({
                    'picking_id': self.id,
                    'company_id':self.company_id.id,
                    'product_uom_id': op.product_uom_id.id,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.location_dest_id.id,
                    'product_id': op.product_id.id,
                    'qty_done': op.qty_done,
                    'product_uom_qty': op.qty_done,
                    # 'product_qty': op.qty_done,
                    # serial
                    'lot_name':serial,
                    'lot_id': sn.id,
                    # kayu
                    'size_log_id': op.size_log_id.id,
                    'diameter_slog':op.diameter_slog,
                    'panjang_slog':op.panjang_slog,
                    'master_hasil':op.master_hasil,
                    'wood_class_id': op.wood_class_id.id,
                    # papan
                    'tinggi':op.tinggi,
                    'lebar':op.lebar,
                    'panjang':op.panjang,
                })


    def _create_backorder(self):
        """ This method is called when the user chose to create a backorder. It will create a new
        picking, the backorder, and move the stock.moves that are not `done` or `cancel` into it.
        """
        backorders = self.env['stock.picking']
        # skip back order
        single_picking = self and self[0] or False
        if single_picking and single_picking.picking_type_id.code == 'incoming' and single_picking.is_kayu:
            _logger.info('----- _create_backorder incoming & kayu ------')
            return backorders
        for picking in self:
            moves_to_backorder = picking.move_lines.filtered(lambda x: x.state not in ('done', 'cancel'))
            if moves_to_backorder:
                backorder_picking = picking.copy({
                    'name': '/',
                    'move_lines': [],
                    'move_line_ids': [],
                    'backorder_id': picking.id,
                    # start ADDITIONAL
                    'depart_no':str(int(picking.depart_no) + 1),
                    'nota':False,
                    'plat_no':False,
                    'qty_nota':False,
                    'cubic_nota':False,
                    'grading_done':False,
                    # end ADDITIONAL
                })
                picking.message_post(
                    body=_('The backorder <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a> has been created.') % (
                        backorder_picking.id, backorder_picking.name))
                moves_to_backorder.write({
                    'picking_id': backorder_picking.id,
                    'qc_id': False, # ADDITIONAL
                    })
                moves_to_backorder.move_line_ids.package_level_id.write({'picking_id':backorder_picking.id})
                moves_to_backorder.mapped('move_line_ids').write({'picking_id': backorder_picking.id})
                # start ADDITIONAL
                for move in moves_to_backorder:
                    for move_line in move.move_line_ids:
                        if move_line.lot_id:
                            move_line.lot_id.compute_qty_received()
                # end ADDITIONAL
                backorders |= backorder_picking
        backorders_to_assign = backorders.filtered(lambda picking: picking._needs_automatic_assign())
        # start ADDITIONAL / CHANGE comment
        # --- original ---
        # if backorders_to_assign:
        #     backorders_to_assign.action_assign()
        # return backorders
        # --- original ---
        if self.is_kayu == True:
            if backorders_to_assign:
                backorders_to_assign.action_assign()
                backorders_to_assign.sudo().write({
                    'state': 'grading' })
        elif self.is_kayu == False:
            if backorders_to_assign:
                backorders_to_assign.action_assign()
                backorders_to_assign.sudo().write({
                    'state': 'assigned' })
        # start ADDITIONAL / CHANGE comment
        return backorders
    
    def button_validate_without_backorder(self):
        self.ensure_one()
        # via Form 
        res_dict = self.button_validate()
        if type(res_dict) is dict:
            backorder_wizard = Form(self.env['stock.backorder.confirmation'].with_context(res_dict['context'])).save()
            backorder_wizard.process_cancel_backorder()


    # update lot size pxlxt jika receipt papan
    def _action_done(self):
        res = super()._action_done()
        for picking in self:
            # hanya untuk type papan
            if picking.wood_type not in ['square', 'timber']:
                continue
            for sml in picking.move_line_ids.filtered(lambda l: l.lot_id):
                sml.lot_id.write({
                    'panjang': sml.panjang,
                    'lebar': sml.lebar,
                    # 'tebal': sml.tinggi, # tebal related dari product
                })

        return res



class StockReturnPickingLine(models.TransientModel):
    _inherit = 'stock.return.picking.line'

    # lot_id = fields.Many2many('stock.production.lot', string='Lot Serial Numbers', domain="[('origin','=', origin)]")
    lot_id = fields.Many2many('stock.production.lot', string='Lot Serial Numbers', domain="[('product_id','=',product_id)]")

    # lot_id = fields.Many2one('stock.production.lot', string='Lot Serial Number', domain="[('product_id','=',product_id)]")
    qty_done = fields.Float('Quantity Done', default=0.0, digits='Product Unit of Measure',copy=False)
    quantity = fields.Float( string='Quantity', compute='_compute_quantity', store=True, required=False)
    origin = fields.Char('Origin', compute='_compute_origin', readonly=False, required=False, store=True, invisible=True)

    @api.depends('move_id.picking_id')
    def _compute_origin(self):
        for line in self:
            line.origin = line.move_id.picking_id.origin

    @api.depends('qty_done')
    def _compute_quantity(self):
        for line in self:
            line.quantity = line.qty_done

    # @api.onchange('lot_id')
    # def onchange_lot_id(self):
    #     if self.lot_id:
    #         self.qty_done = self.lot_id.product_qty

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        if self.lot_id:
            self.qty_done = sum(self.lot_id.mapped('product_qty'))

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.move_ids_without_package:
            for move in self.move_ids.filtered(lambda x: x.product_id == self.product_id):
                if move.move_line_nosuggest_ids:
                    self.lot_id = move.move_line_nosuggest_ids[0].lot_id
                    self.qty_done = move.move_line_nosuggest_ids[0].qty_done
                else:
                    self.lot_id = False
                    self.qty_done = move.product_uom_qty
                break
            else:
                self.lot_id = False
                self.qty_done = 0.0

    # def _create_returns(self):
    #     res = super(StockReturnPickingLine, self)._create_returns()
    #     for return_line in res:
    #         if return_line.lot_id:
    #             return_line.move_id.write({'lot_id': return_line.lot_id.id})
    #     return res


class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def create_returns(self):
        res = super().create_returns()
        if res:
            for return_line in res.get('product_return_moves', []):
                if return_line.get('lot_id'):
                    return_line.get('move_id').write(
                        {'lot_id': return_line.get('lot_id').id})
        return res


class ReceiveListOperation(models.Model):
    _name = 'receive.list.operation'
    _description = 'Receive List Operation'

    picking_id = fields.Many2one(
        'stock.picking', 'Transfer', help='The stock operation where the packing has been made')
    # for product filter
    related_stock_move_ids = fields.Many2many( 'product.product', 
        compute='_compute_related_stock_move_ids', string='Available Product')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company,
        index=True, required=True)
    # PAPAN
    tinggi = fields.Float('Tinggi')
    panjang = fields.Float('Panjang (cm)')
    lebar = fields.Float('Lebar (cm)')
    # LOG
    size_log_id = fields.Many2one('res.size.log', string='Size Log', default=False)
    diameter_slog = fields.Integer('Diameter', related='size_log_id.diameter_log', store=True, readonly=True)
    panjang_slog = fields.Integer('Panjang', related='size_log_id.panjang_log', store=True, readonly=True)
    ujung_keliling = fields.Integer('Ujung Keliling', related='size_log_id.ujung_keliling_log', store=True, readonly=True)
    master_hasil = fields.Selection([
        ('bagus', 'Bagus'),
        ('afkir', 'Afkir'),
        ('triming', 'Triming'),
        ('grade_a', 'Grade A'),
        ('grade_b', 'Grade B')
    ], string='Grading')
    wood_class_id = fields.Many2one(
        comodel_name='res.wood.class', string='Wood Class')
    # Qty
    qty = fields.Integer(string='Qty', default=1)
    qty_done = fields.Float('Done', digits='Product Unit of Measure', 
        compute='_compute_qty_done', store=True)
    subtotal_qty_done = fields.Float('Subtotal Done', digits='Product Unit of Measure', 
        compute='_compute_qty_done', store=True)
    kubikasi_m3 = fields.Float('Kubikasi M3', copy=False, related='size_log_id.kubikasi')
    product_id = fields.Many2one('product.product', string='Product')
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=True, 
        domain="[('category_id', '=', product_uom_category_id)]", related='product_id.uom_id')
    # TODO remove me, tidak perlu
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')


    @api.depends('picking_id.move_ids_without_package','picking_id.move_ids_without_package.product_id')
    def _compute_related_stock_move_ids(self):
        for operation in self:
            operation.related_stock_move_ids = operation.picking_id.move_ids_without_package.mapped('product_id')

    @api.depends('product_id', 'panjang', 'lebar', 'tinggi', 'qty', 'size_log_id')
    def _compute_qty_done(self):
        for rec in self:
            res = 0.00
            if rec.product_id and rec.product_id.wood_type:
                if rec.product_id.wood_type == 'log' and rec.size_log_id:
                    res = rec.size_log_id.kubikasi
                if rec.product_id.wood_type == 'square' and rec.panjang and rec.lebar and rec.tinggi:
                    kubikasi = rec.panjang * rec.lebar * rec.tinggi
                    res = kubikasi / 1000000 if kubikasi > 0 else 0.00
                if rec.product_id.wood_type == 'timber' and rec.panjang and rec.lebar and rec.tinggi:
                    # kubikasi = rec.panjang * rec.lebar * rec.tinggi * rec.qty_received
                    # tidak ada Pcs (qty_received)
                    kubikasi = rec.panjang * rec.lebar * rec.tinggi
                    res = kubikasi / 1000000 if kubikasi > 0 else 0.00
            rec.qty_done = res
            rec.subtotal_qty_done = rec.qty * res
