from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class JidokaTagcard(models.Model):
    _name = 'jidoka.tagcard'
    _description = 'Tag Card for Material'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id DESC'
    _rec_name = 'name_code_gudang'

    # TODO seharusnya name di compute, code jangan related karena bisa berubah
    name_seq = fields.Char(string='Nama Sequence', store=True,)
    # TODO jika dicopy???
    name = fields.Char(string='No. Tag Card', required=True, tracking=True)
    name_code_gudang = fields.Char(string='No. Code Gudang - Tag Card', 
        compute='_compute_name_code_gudang', store=True, readonly=True, tracking=True)

    @api.depends('name', 'code_gudang')
    def _compute_name_code_gudang(self):
        for record in self:
            record.name_code_gudang = f"{record.code_gudang}{record.name}"

    sequence_id = fields.Many2one('ir.sequence', string='Sequence', copy=False)
    product_id = fields.Many2one('product.product', string='Product', required=True, tracking=True)
    tagcard_type = fields.Selection(string='TagCard Type', selection=[
        ('sawn_timber', 'SAWN TIMBER'),
        ('component', 'COMPONENT'),
        ('barang_setengah_jadi', 'BARANG SETENGAH JADI'),
        ('barang_jadi', 'BARANG JADI')], default='sawn_timber', tracking=True)
    state = fields.Selection(string='State', selection=[
        ('draft', 'Draft'),
        ('done', 'Done')],
        default='draft', tracking=True, readonly=True, required=True, copy=False)
    # locations data
    destination_location_id = fields.Many2one(comodel_name='stock.location', 
        string='Destination Location', required=True, tracking=True)
    location_id = fields.Many2one('stock.location', 'Source Location',
        help="Location where the system will stock the finished products.",
        required=True, tracking=True,)
    code_gudang = fields.Char('Code Gudang', related='location_id.code_gudang')
    # tag card details
    # NOTE quant yg bisa dipilih
    quant_ids = fields.Many2many(comodel_name='stock.quant', string='Stock Quants', copy=False)
    # NOTE result dari quant terpilih (is_selected True)
    material_count_ids = fields.One2many(comodel_name='jidoka.tagcard.material',
        inverse_name='tagcard_id', string='Materials', copy=False)
    # package result data
    quant_package_id = fields.Many2one(comodel_name='stock.quant.package', 
        string='Stock Quant Package', tracking=True, copy=False, default=False)
    picking_id = fields.Many2one('stock.picking', 'Picking', copy=False)
    # product / tag card meta data
    wood_kind_id = fields.Many2one(comodel_name='jidoka.woodkind', string='Jenis Kayu', 
        related='product_id.wood_kind_id', store=True, readonly=True)
    color_id = fields.Many2one(string='Color', comodel_name='res.fabric.colour', tracking=True)
    cushion = fields.Char(string='Cushion', tracking=True)
    note = fields.Text('Note', tracking=True)
    prod_intruction_id = fields.Many2one('mrp.production', string='Prod Intruction', tracking=True)
    bahan = fields.Selection([
        ('baku', 'Baku'),
        ('setengah_jadi', 'Setengah Jadi'),
        ('kd', 'K/D'),
        ('sertifikat', 'Bersertifikat'),
        ('moulding', 'Moulding'),
        ('ad', 'A/D'),
        ('tidak', 'Tidak'),
    ], string='Bahan', default='baku', tracking=True)
    fisik = fields.Selection([
        ('standard', 'Standard'),
        ('tipis', 'Tipis'),
        ('mata', 'Mata'),
    ], string='Fisik', default='standard', tracking=True)
    kode_beli = fields.Char('Kode Beli', tracking=True)
    kualitas = fields.Char('Kualitas', tracking=True)
    marking = fields.Char('Marking', tracking=True)
    supplier_id = fields.Many2one('res.partner', string='Supplier', tracking=True)
    it = fields.Char('IT', tracking=True)
    po_stock = fields.Char(string='PO Stock', tracking=True)
    mo_sale_order_id = fields.Many2one('sale.order', string='MO', default=False, 
        domain="[('state', 'in', ['sr', 'sale', 'done'])]", tracking=True)
    sku = fields.Char(string='SKU', tracking=True)
    
    # date
    tgl_dibuat = fields.Datetime(string='Tanggal Dibuat', default=fields.Datetime.now,
        tracking=True, required=True)
    tgl_masuk = fields.Datetime(string='Tanggal Masuk', default=fields.Datetime.now,
        required=True, tracking=True)
    # Qty & total
    total_qty = fields.Float('Total Quantity' , readonly=True, store=True, digits=(12,5),
        tracking=True, compute='_compute_total')
    total_pcs = fields.Integer(string='Total Pcs', readonly=True, store=True,
        tracking=True, compute='_compute_total')
    total_m3 = fields.Float('Total M3', digits=(12,5) , readonly=True, store=True,
        tracking=True, compute='_compute_total')
    total_m2 = fields.Float('Total M2', digits=(12,5) , readonly=True, store=True,
        tracking=True, compute='_compute_total')
    total_m = fields.Float('Total M' , digits=(12,5), readonly=True, store=True,
        tracking=True, compute='_compute_total')
    total_m3_1 = fields.Float('Total', digits=(12,5), readonly=True, store=True,
        compute='_compute_total', tracking=True)
    total_m2_1 = fields.Float('Total', digits=(12,5), readonly=True, store=True,
        compute='_compute_total', tracking=True)
    total_m_1 = fields.Float('Total', digits=(12,5), readonly=True, store=True,
        compute='_compute_total', tracking=True)
    # selection tools
    selected_count = fields.Integer(string='Selected Count', compute='_compute_selected_count', store=True)
    # transfer data
    transfer = fields.Boolean(string='Transfer', tracking=True, default=False)
    count_transfer = fields.Integer(string='Count Transfer', compute='_count_transfer')
    # dimension tools
    result_dimension_ids = fields.One2many(string='Result Dimension', 
        comodel_name='result.filters.dimension', inverse_name='tagcard_id', copy=False)
    # search quant tools
    s_tebal = fields.Float(string='Tebal')
    s_lebar = fields.Float(string='Lebar')
    s_panjang = fields.Float(string='Panjang')
    s_lot_qty = fields.Integer(string='Jumlah Lot', default=1, required=True)
    certification_id = fields.Many2one('res.certification', string='Sertifikasi')
    
    transaction_date = fields.Datetime('Transaction Date')

    # TODO revisi me, kurang benar
    @api.depends('location_id', 'code_gudang')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.location_id.name} - {record.code_gudang}"

    def show_quick_add_search_wiz(self):
        self.ensure_one()
        return {
            'name': _('Quick Search & Add Material Tag Card'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tagcard.quick.add.wizard',
            'target': 'new',
            'context': {
                'default_tag_card_id': self.id,
                'default_s_panjang': self.s_panjang,
                'default_s_lebar': self.s_lebar,
                'default_s_tebal': self.s_tebal,
                'default_s_lot_qty': self.s_lot_qty,
            }
        }
    
    # generate / set quant by s_xxxx
    def search_and_add_quant(self):
        if not self.quant_ids:
            raise UserError("Data List Material kosong, klik Search terlebih dahulu.")
        filtered_quants = self.quant_ids.filtered(lambda quant: not quant.is_selected and quant.tebal == self.s_tebal and quant.panjang == self.s_panjang and quant.lebar == self.s_lebar)
        if not filtered_quants:
            raise UserError("Data Stock tidak ditemukan dengan dimensi yang sesuai.")
        if len(filtered_quants) < self.s_lot_qty:
            raise UserError("Data Stock hanya %s ." % len(filtered_quants))
        for n in range(self.s_lot_qty):
            filtered_quants[n].is_selected = True
        self._count_materials_by_quants()

    # generate / set quant by dimension
    # def action_generate_dimension_calc_result(self):
    #     # delete first
    #     self.quant_ids.write({
    #         'is_selected': False
    #     })
    #     self.material_count_ids = False
    #     self.result_dimension_ids.write({
    #         'matched_quantity': 0
    #     })
    #     if not self.quant_ids:
    #         raise UserError("Data List Material kosong, klik Search terlebih dahulu.")
    #     if self.result_dimension_ids:
    #         for dms in self.result_dimension_ids:
    #             if self.tagcard_type == 'sawn_timber':
    #                 filtered_quants = self.quant_ids.filtered(lambda quant: not quant.is_selected and quant.tebal == dms.tebal and quant.panjang == dms.panjang and quant.lebar == dms.lebar)
    #             else:
    #                 filtered_quants = self.quant_ids.filtered(lambda quant: not quant.is_selected and quant.tebal == dms.tebal2 and quant.panjang == dms.panjang and quant.lebar == dms.lebar)
    #             # if not filtered_quants:
    #             #     continue
    #             max_quant = min([dms.quantity, len(filtered_quants)])
    #             for n in range(max_quant):
    #                 filtered_quants[n].is_selected = True
    #             dms.matched_quantity = max_quant
    #             if not filtered_quants:
    #                 raise UserError("Data quant_ids tidak ditemukan dengan dimensi yang sesuai.")
    #             if len(filtered_quants) < dms.quantity:
    #                 raise UserError("Data quant_ids tidak cukup, hanya ada %s ." % len(filtered_quants))
                
    #     self._count_materials_by_quants()

    def action_generate_dimension_calc_result(self):
        # delete first
        self.quant_ids.write({
            'is_selected': False
        })
        self.material_count_ids = False
        self.result_dimension_ids.write({
            'matched_quantity': 0
        })
        if not self.quant_ids:
            raise UserError("Data List Material kosong, klik Search terlebih dahulu.")
        if self.result_dimension_ids:
            for dms in self.result_dimension_ids:
                if self.tagcard_type == 'sawn_timber':
                    filtered_quants = self.quant_ids.filtered(lambda quant: not quant.is_selected and quant.tebal == dms.tebal and quant.panjang == dms.panjang and quant.lebar == dms.lebar)
                else:
                    filtered_quants = self.quant_ids.filtered(lambda quant: not quant.is_selected and quant.tebal == dms.tebal2 and quant.panjang == dms.panjang and quant.lebar == dms.lebar)
                max_quant = min([dms.quantity, len(filtered_quants)])
                for n in range(max_quant):
                    filtered_quants[n].is_selected = True
                if not filtered_quants:
                    dms.matched_quantity = 0
                    continue
                dms.matched_quantity = max_quant
                if len(filtered_quants) < dms.quantity:
                    raise UserError("Data quant_ids tidak cukup, hanya ada %s ." % len(filtered_quants))
        
        self._count_materials_by_quants()

    @api.depends(
        'material_count_ids',
        'material_count_ids.quantity',
        'material_count_ids.m',
        'material_count_ids.m2',
        'material_count_ids.m3',
    )
    def _compute_total(self):
        for record in self:
            record.total_pcs = sum(record.material_count_ids.mapped('total'))
            record.total_qty = sum(record.material_count_ids.mapped('quantity'))
            record.total_m3 = sum (record.material_count_ids.mapped('m3'))
            record.total_m2 = sum (record.material_count_ids.mapped('m2'))
            record.total_m = sum (record.material_count_ids.mapped('m'))
            record.total_m3_1 = record.total_qty * record.total_m3
            record.total_m2_1 = record.total_qty * record.total_m2
            record.total_m_1 = record.total_qty * record.total_m

    @api.onchange('prod_intruction_id')
    def onchange_prod_instruction_id(self):
        if self.prod_intruction_id:
            self.product_id = self.prod_intruction_id.product_id
            self.location_id= self.prod_intruction_id.location_dest_id

    # TODO revisi ini, sudah tdk relevan
    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('jidoka.tagcard') or _('New')
    #     return super(JidokaTagcard, self).create(vals)

    @api.depends('quant_ids.is_selected')
    def _compute_selected_count(self):
        for record in self:
            selected_quants = record.quant_ids.filtered(lambda quant: quant.is_selected)
            record.selected_count = len(selected_quants)
    
    # view transfer of tag card
    def button_view_transfer(self):
        self.ensure_one()
        picking = self.env['stock.picking'].search([('tagcard_id', '=', self.id)], limit=1)
        if not picking:
            raise UserError("Transfer not found")
        return {
            'type': 'ir.actions.act_window',
            'name': _('Transfer'),
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': picking.id,
            'target': 'current',
        }

    def action_confirm_transfer(self):
        self.transfer = True
        move_ids = self._prepare_moves()
        line_ids = self._prepare_move_lines()
        # Create a new stock picking of type 'internal
        picking = self.env['stock.picking'].create({
            'partner_id': self.env.company.partner_id.id, # perlu?
            'origin': self.quant_package_id.name,
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
            'location_id': self.location_id.id,
            'location_dest_id': self.destination_location_id.id,
            'move_ids_without_package': move_ids,
            'is_tagcard': True,
            'grading_done': True,
            'show_check_availability': False,
            'show_validate': False,
            # 'nota': '-',
            # 'is_qc': True,
            'tagcard_id': self.id,
            'transaction_date': self.transaction_date,
        })

        

        if not picking.exists():
            raise ValidationError(_("Transfer failed!"))
        
        picking.write({
            'move_line_ids_without_package': line_ids,
        })
        picking.action_confirm()
        picking.action_assign()
        picking.button_validate()
    
    def _prepare_moves(self):
        move_vals = []
        selected_quant_ids = self.quant_ids.filtered(lambda q: q.is_selected)
        if self.quant_package_id and selected_quant_ids:
            quants = selected_quant_ids
            # jika component bisa edit qty, gunakan quantity di material_count_ids dan normalnya tdk pakai lot
            if self.tagcard_type == 'component':
                qtys = self.material_count_ids.mapped('quantity')
                qty = sum(qtys)
            else:
                qty = sum(quants.mapped('quantity'))
            vals = {
                'name': quants[0].product_id.partner_ref, # partner_ref dari mana???
                'origin': self.quant_package_id.name,
                'product_id': quants[0].product_id.id,
                'product_uom_qty': qty,
                'product_uom': quants[0].product_id.uom_id.id,
                'wood_kind_id': quants[0].wood_kind_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.destination_location_id.id,
            }
            move_vals = [(0, 0, vals)]
        return move_vals
    
    def _prepare_move_lines(self):
        move_line_vals = []
        selected_quant_ids = self.quant_ids.filtered(lambda q: q.is_selected)
        if self.quant_package_id and selected_quant_ids:
            # jika component bisa edit qty, gunakan quantity di material_count_ids dan normalnya tdk pakai lot
            if self.tagcard_type == 'component':
                total_qty = sum(self.material_count_ids.mapped('quantity'))
            else:
                total_qty = sum(selected_quant_ids.mapped('quantity'))
            used_qty = 0
            for quant in selected_quant_ids:
                # handle if smaller
                if total_qty <= quant.quantity:
                    qty_to_process = total_qty
                else:
                    qty_to_process = quant.quantity
                available_qty = total_qty - used_qty
                if available_qty >= qty_to_process:
                    qty = qty_to_process
                else:
                    qty = available_qty
                used_qty += qty
                if qty > 0.0:
                    vals = {
                        'origin': self.quant_package_id.name,
                        'product_id': quant.product_id.id,
                        'product_uom_id': quant.product_id.uom_id.id,
                        'lot_id': quant.lot_id.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.destination_location_id.id,
                        # 'package_id': self.quant_package_id.id,
                        'result_package_id': self.quant_package_id.id, # package yg sama
                        'qty_done': qty,
                    }
                    move_line_vals += [(0, 0, vals)]
        return move_line_vals
    
    def _count_transfer(self):
        for rec in self:
            count = rec.env['stock.picking'].sudo().search_count([
                ('picking_type_code','=','internal'),
                ('tagcard_id','=',rec.id)])
            if count:
                rec.count_transfer = count
            else:
                rec.count_transfer = 0

    def write(self, values):
        result = super(JidokaTagcard, self).write(values)
        check_quant_ids = values.get('quant_ids', False)
        if check_quant_ids:
            # make sure not none
            if self.quant_ids:
                self._count_materials_by_quants()
            if not self.quant_ids:
                self.write({
                    'material_count_ids': False
                })
        return result
    
    def check_all(self):
        selected_quants = self.quant_ids.filtered(lambda q: not q.is_selected)[:40]
        selected_quants.write({'is_selected': True})
        self._count_materials_by_quants()
    
    def des_check_all(self):
        self.quant_ids.write({'is_selected': False})
        self.result_dimension_ids.write({'matched_quantity': 0})
        self._count_materials_by_quants()

    @api.depends('quant_ids.is_selected')
    def _compute_selected_count(self):
        for record in self:
            record.selected_count = len(record.quant_ids.filtered(lambda r: r.is_selected))
    
    def search_materials(self):
        """Delete & update material & list material"""
        self._delete_materials()
        if self.state != 'draft':
            raise ValidationError(_("Materials Search can only be done in the draft state."))
        quants = self.env['stock.quant'].sudo().search([
            ('product_id','=', self.product_id.id),
            ('package_id','=', False), # yang belum di tag / package
            ('location_id','=', self.location_id.id),
            ('quantity', '>', 0)
        ])
        quants = quants.filtered(lambda q: q.product_id.wood_kind_id.id == self.wood_kind_id.id)
        if quants:
            for quant in quants:
                quant.tagcard_id = self.id
            self.quant_ids = quants.ids
            self._count_materials_by_quants()
            return True
        return False
            
    def _count_materials_by_quants(self):
        """Update material_count_ids (stock yg akan di tag card) by quants"""
        self.write({
            'material_count_ids': False
        })
        quants = self.quant_ids.filtered(lambda m: m.is_selected)
        LIST_PANJANG = set(quants.mapped('panjang'))
        LIST_LEBAR = set(quants.mapped('lebar'))
        line_ids = []
        filter_mats = False
        for lp in LIST_PANJANG:
            for ll in LIST_LEBAR:
                filter_mats = quants.filtered(lambda m: m.panjang == lp and m.lebar == ll)
                if not filter_mats:
                    continue
                if filter_mats:
                    vals = {
                        'tagcard_id': self.id,
                        'product_id': filter_mats[0].product_id.id,
                        'panjang': filter_mats[0].panjang,
                        'lebar': filter_mats[0].lebar,
                        'm3': filter_mats[0].product_id.total_meter_cubic,
                        'm2': filter_mats[0].product_id.total_meter_persegi,
                        'm': filter_mats[0].product_id.total_meter,
                        'panjang': filter_mats[0].product_id.size_panjang,
                        'total': len(filter_mats),
                        'lot_ids': filter_mats.mapped('lot_id.id'),
                        'quantity': sum(filter_mats.mapped('quantity')),
                        'lebar': filter_mats[0].product_id.size_lebar,
                        'tebal': filter_mats[0].product_id.size_tebal,
                    }
                    line_ids += [(0,0,vals)]
        if line_ids:
            self.write({
                'material_count_ids': line_ids
            })

    def _delete_materials(self):
        """set False material_count_ids & quant_ids"""
        self.write({
            'quant_ids': False,
            'material_count_ids': False,
            'result_dimension_ids': False,
        })
    
    def _check_quant_selected(self):
        """Update quant_ids set hanya yg selected"""
        quants = self.quant_ids.filtered(lambda q: q.is_selected)
        if not quants:
            raise ValidationError(_('Please checklist materials before done'))

    def action_done(self):
        self._check_material_valid_location()
        self._check_quant_selected()
        new_stock_package = self.env['stock.quant.package'].sudo().create({
            'name': self.name_code_gudang,
            'tagcard_id': self.id,
            'company_id': self.env.company.id,
            'location_id': self.location_id.id,
            'transaction_date': self.transaction_date,
        })
        if not new_stock_package.exists():
            raise UserError(_("Could not validate this Tag Card"))
        # bikin variabel yang terhubung dengan stock picking yang nge create nilai baru is_tagcard
        self.write({
            'quant_package_id': new_stock_package.id,
            'state': 'done',
        })
        self.action_confirm_transfer()
        
    # TODO remove me, tidak boleh reset jika sudah transfer
    def action_reset(self):
        return False
        self.write({
            'state': 'draft',
        })
        
    def _check_material_valid_location(self):
        """Make sure quant still valid (same location)"""
        if not self.quant_ids:
            raise ValidationError(_("Materials cannot be empty."))
        if self.quant_ids:
            for mt in self.quant_ids:
                if mt.location_id.id != self.location_id.id:
                    raise ValidationError(_("The location of the material is not suitable, Please search material again."))

    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        domain = [('origin', '=', self.name)]
        action['domain'] = domain
        action['views'] = [(self.env.ref('stock.view_picking_tree').id, 'tree')]
        action['context'] = {'search_default_groupby_origin': True}
        return action


class JidokaTagcardMaterial(models.Model):
    _name = 'jidoka.tagcard.material'
    _description = 'Count material in tagcard detail'
    
    name = fields.Char(string='Name')
    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    tebal = fields.Float('T (cm)', related='product_id.tebal')
    panjang = fields.Float(string='P (cm)', default=0)
    lebar = fields.Float(string='L (cm)', default=0)
    total = fields.Integer(string='Total (Pcs)')
    package_id = fields.Many2one('stock.quant.package', string='Package')
    lot_ids = fields.Many2many(comodel_name='stock.production.lot', string='Lots')
    quantity = fields.Float(string='Quantity', digits='Product Unit of Measure', copy=False)
    uom_id = fields.Many2one("uom.uom","Unit Of Measure", store=True, related='product_id.uom_id')
    m3 = fields.Float('M3',  digits=(12,8))
    m2 = fields.Float('M2',  digits=(12,8))
    m = fields.Float('M',    digits=(12,8))
    tagcard_id = fields.Many2one('jidoka.tagcard', string='TagCard')
    tagcard_type = fields.Selection(related='tagcard_id.tagcard_type', string='TagCard Type', readonly=True)
    
    def unlink(self):
        for rec in self:
            quant_ids = rec.tagcard_id.quant_ids.filtered(lambda m: m.panjang == rec.panjang and m.lebar == rec.lebar)
            if quant_ids:
                quant_ids = list(set(rec.tagcard_id.quant_ids.ids) - set(quant_ids.ids))
                if not quant_ids:
                    quant_ids = False
                rec.tagcard_id.sudo().write({
                    'quant_ids': quant_ids
                })
        return super(JidokaTagcardMaterial, self).unlink()

    
    
class ResultFiltersDimension(models.Model):
    _name = 'result.filters.dimension'
    _description = 'show materials filter from dimension'
    
    tagcard_id = fields.Many2one('jidoka.tagcard', string='TagCard')
    product_id = fields.Many2one(comodel_name='product.product', string='Product',
        related='tagcard_id.product_id')
    tebal = fields.Float('T (cm)', related='product_id.tebal')
    tebal2 = fields.Float('T (cm)')
    panjang = fields.Float(string='P (cm)', default=0)
    lebar = fields.Float(string='L (cm)', default=0)
    quantity = fields.Integer('Jumlah Lot', default=1, required=True)
    matched_quantity = fields.Integer(string='Matched Lots', default=0, copy=False)

    # def unlink(self):
    #     for record in self:
    #         super(ResultFiltersDimension, record).unlink()
    #     return super(ResultFiltersDimension, self).unlink()