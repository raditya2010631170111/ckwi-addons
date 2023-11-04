from odoo import _, api, fields, models
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import ValidationError

class InspectionTagCard(models.Model):
    _name = 'inspection.tag.card'
    
    # # Function untuk mencegah user menghapus barang/item No.Tag Card di Inspection Tag Card
    # def _unlink(self):
    #     raise ValidationError("Tidak dapat menghapus barang dalam daftar.")

    # unlink = _unlink

    name = fields.Char('Name', default=lambda self: _('New'), copy=False, readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            sequence = self.env['ir.sequence'].next_by_code('inspection.tag.card') or _('New')
            vals['name'] = sequence
        result = super().create(vals)
        return result

    
    
    # name = fields.Char(string='', default=lambda self: self.env['ir.sequence'].next_by_code('qa_qc.seq'))
    # name = fields.Char(
    #     string='Name',
    #     # default=lambda self:self.env['ir.sequence'].next_by_code('tag_card.seq'),
    #     default='New',
    #     readonly=True,
    #     tracking=True,
    #     store=True
    # )

    # @api.model
    # def create(self, vals):
    #     if vals.get('name', 'New') == 'New':
    #         seq = self.env['ir.sequence'].next_by_code('tag_card_ids.seq') or 'New'
    #     vals['name'] = seq
    #     res = super().create(vals)
    #     return res


    # date = fields.Datetime(default=fields.Datetime.now)
    # location_id = fields.Many2one('stock.location',string='Location')
    # destination_location_id = fields.Many2one(comodel_name='stock.location', string='Location', compute='_compute_destination_location_id')  
    destination_location_id = fields.Many2one(comodel_name='stock.location', string='Location')  

    # @api.depends('tag_card_ids')
    # def _compute_destination_location_id(self):
    #     for record in self:
    #         record.destination_location_id = False
    #         if record.tag_card_ids:
    #             record.destination_location_id = record.tag_card_ids.destination_location_id

    # tag_card = fields.Many2one('jidoka.tagcard', string='No.Tag Card', store=True ) 
    
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
    )
    
    tag_card_ids = fields.Many2many('jidoka.tagcard',string='No.Tag Card', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
    ], default="draft")
    product_tmpl_ids = fields.Many2many('product.product', 'tag_card_product_tmpl_rel', 'tag_id', 'product_id', string='Item Product', compute='_compute_product_tmpl_ids')
    product_id_domain_ids = fields.Many2many('product.product', 'tag_card_product_domain_rel_1', 'tag_id', 'product_id', readonly=False, string='Item Product')
    available_products = fields.Many2many('product.product', 'tag_card_product_domain_rel_2', 'tag_id', 'product_id', compute='_compute_available_products', store=True,readonly=False)
    no_mo_id = fields.Many2one('sale.order', string='No. SC')
    product_line_ids = fields.One2many(comodel_name='inspection.tag.card.line', string='Product Detail', 
                                       inverse_name='inspection_tagcard_id')
    operation_line_ids = fields.One2many(comodel_name='inspection.tag.card.operation', string='Product Detail', 
                                       inverse_name='inspection_tagcard_id')
    # product_uom_qty = fields.Float(string='Product Quantity',compute='_compute_product_uom_qty')
    type_qc = fields.Selection([
    ('reguler', 'Reguler'),
    ('pembahanan', 'Pembahanan'),
    ('bras_component', 'Bras Component'),
    ('proses_pengiriman', 'Proses Pengiriman'),
    ('pre_finishing', 'Pre Finishing'),
    ('top_coat', 'Top Coat'),
    ('packing', 'Packing'),
    ('cushion', 'Cushion'),
    ('kawai_top_coat', 'Kawai Top Coat'),
], string='Type QC',default='reguler')

    #PEMBAHANAN
    product_pembahanan_id = fields.Many2one('product.template', string='Item', domain="[('categ_id.name', '=', 'Barang Jadi')]")

    @api.depends('product_id_domain_ids')
    def _compute_available_products(self):
        for record in self:
            record.available_products = self._get_default_available_products()

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if 'available_products' in fields_list:
            defaults['available_products'] = self._get_default_available_products()
        return defaults

    def _get_default_available_products(self):
        previous_record = self.search([], order='id desc', limit=1)
        if previous_record:
            return previous_record.available_products + self.product_id_domain_ids
        return self.product_id_domain_ids
    
    @api.depends('no_mo_id')
    def _compute_product_tmpl_ids(self):
        for record in self:
            if record.no_mo_id:
                product_ids = record.no_mo_id.order_line.mapped('product_id')
                domain = [('id', 'in', product_ids.ids), ('id', 'not in', record.available_products.ids)]
                record.product_tmpl_ids = self.env['product.product'].search(domain)
                if not record.product_tmpl_ids:
                    record.no_mo_id = False
            else:
                record.product_tmpl_ids = False

    @api.onchange('no_mo_id')
    def _onchange_no_mo_id(self):
        selected_ids = self.search([('no_mo_id', '!=', False)]).filtered(lambda r: r.state == 'sale').mapped('no_mo_id').ids
        domain = [('id', 'not in', selected_ids), ('state', '=', 'sale')]
        return {'domain': {'no_mo_id': domain}}


    

    # @api.onchange('no_mo_id')
    # def onchange_no_mo_id(self):
    #     if not self.no_mo_id:
    #         self.product_line_ids = [(5, 0, 0)]  # Remove existing lines
    #     else:
    #         self.product_line_ids = [(5, 0, 0)]
    #         lines = []
    #         for rec in self.no_mo_id.order_line.filtered(lambda r: r.product_id.type != 'service'):
    #             vals = {
    #                 'product_id': rec.product_id.id,
    #                 'product_uom_qty' : rec.product_uom_qty,
    #             }
    #             lines.append((0, 0, vals))
    #         self.product_line_ids = lines

    @api.onchange('tag_card_ids')
    def onchange_tag_card_ids(self):
        selected_ids = self.search([('tag_card_ids', '!=', False)]).mapped('tag_card_ids').ids
        domain = [('id', 'not in', selected_ids)]
        if not self.tag_card_ids:
            self.product_line_ids = [(5, 0, 0)]  # Remove existing lines
        else:
            self.product_line_ids = [(5, 0, 0)]
            lines = []
            for rec in self.tag_card_ids.material_count_ids.filtered(lambda r: r.product_id.type != 'service'):
                vals = {
                    'product_id': rec.product_id.id,
                    'product_uom_qty' : rec.quantity,
                }
                lines.append((0, 0, vals))
            self.product_line_ids = lines
        return {'domain': {'tag_card_ids': domain}}
    
            
    # @api.depends('sale_order_line_id')
    # def _compute_product_uom_qty(self):
    #     for record in self:
    #         record.product_uom_qty = sum(record.sale_order_line_id.mapped('product_uom_qty'))

    # @api.depends('sale_order_line_id')
    # def _compute_product_id(self):
    #     for record in self:
    #         record.product_id = ', '.join(record.sale_order_line_id.mapped('product_id.name'))
                

    # no_mo_id = fields.Many2one('sale.order', string='No. CR')
    # product_id = fields.Many2one('product.product', string='Item', compute='_compute_product_id')
    # sale_order_line_id = fields.Many2many('sale.order.line', string='Product', compute='_compute_sale_order_line_id')

    # @api.depends('no_mo_id')
    # def _compute_sale_order_line_id(self):
    #     for record in self:
    #         record.sale_order_line_id = False
    #         if record.no_mo_id:
    #             record.sale_order_line_id = record.no_mo_id.order_line.ids

    # @api.depends('sale_order_line_id')
    # def _compute_product_id(self):
    #     for record in self:
    #         if record.sale_order_line_id:
    #             products = self.env['product.product'].search([('product_id', 'in', record.sale_order_line_id.mapped('product_id').ids)])
    #             record.product_id = products.ids
    #         else:
    #             record.product_id = False

   
              


   
    # product_uom_qty = fields.Float(string='Quantity', compute='_compute_product_fields')
    # no_mo_id = fields.Many2one('sale.order', string='No. MO', compute='_compute_product_fields')

    # @api.depends('sale_order_line_id.product_id', 'sale_order_line_id.product_uom_qty', 'sale_order_line_id.order_id')
    # def _compute_product_fields(self):
    #     for tag_card in self:
    #         tag_card.product_id = tag_card.sale_order_line_id.product_id
    #         tag_card.product_uom_qty = tag_card.sale_order_line_id.product_uom_qty
    #         tag_card.no_mo_id = tag_card.sale_order_line_id.order_id.id
   
    

    partner_id = fields.Many2one('res.partner', string='Supplier')
    user_id = fields.Many2one('res.partner', string='Buyer')
    categ_id = fields.Many2one('product.category', string='Category')

    # total_qty = fields.Float(store=True, compute='_compute_quantity', string="Quantity", digits = (12,5))

    # @api.depends('tag_card_ids')
    # def _compute_quantity(self):
    #     for record in self:
    #         record.total_qty = False
    #         if record.tag_card_ids:
    #             record.total_qty = record.tag_card_ids.total_qty

    status_pemeriksaan = fields.Selection([
        ('terima', 'Terima'),
        ('tolak', 'Tolak'),
        ('hold', 'Hold'),
    ])
    metode_pemeriksaan = fields.Selection([
        ('random', 'Random'),
        ('pc', 'Pc by PC'),
        ('lima_pcs', 'Lima (5) pcs'),
    ])
    qc_id = fields.Many2one('quality.check', string='QC')
    # name = fields.Char('QC Sequence', default="New", required=True)
    no_pi = fields.Char('No. Pi')
    tindakan_pemeriksaan = fields.Selection([
        ('rework', 'Rework'),
        ('reuse', 'Reuse'),
        ('konsesi', 'Konsesi'),
        ('stock', 'Stock'),
        ('scrap', 'Scrap'),
        ('return', 'Return'),
    ])
    note = fields.Text()

    #PEMBAHANAN
    sum_total_kirim = fields.Integer('SUM Total Kirim', compute="_sum_total_kirim")
    sum_no_su = fields.Integer('SUM Total Defect', compute="_sum_no_su")
    persentase_harian = fields.Float('% Harian', compute="_persentase_harian")

    @api.depends('sum_no_su', 'sum_total_kirim')
    def _persentase_harian(self):
        for record in self:
            if record.sum_total_kirim != 0:
                record.persentase_harian = (record.sum_no_su / record.sum_total_kirim) * 100
            else:
                record.persentase_harian = 0.0
                
    @api.depends('product_line_ids.no_su')
    def _sum_no_su(self):
        for record in self:
            subtotal_qty = sum(record.product_line_ids.mapped('no_su'))
            record.sum_no_su = subtotal_qty

    @api.depends('product_line_ids.tk_pembahanan')
    def _sum_total_kirim(self):
        for record in self:
            subtotal_qty = sum(record.product_line_ids.mapped('tk_pembahanan'))
            record.sum_total_kirim = subtotal_qty


    #PROSES PENGIRIMAN 
    sum_tk_pengiriman = fields.Integer('SUM Total Kirim', compute="_sum_tk_pengiriman")
    sum_su_proses = fields.Integer('SUM SU Proses', compute="_sum_tk_pengiriman")
    sum_su_material = fields.Integer('SUM SU Material', compute="_sum_tk_pengiriman")
    persentase_harian_pengiriman = fields.Float('% Harian', compute="_persentase_harian_pengiriman")

    @api.depends('sum_tk_pengiriman', 'sum_su_proses','sum_su_material')
    def _persentase_harian_pengiriman(self):
        for record in self:
            if record.sum_tk_pengiriman != 0:
                record.persentase_harian_pengiriman = ((record.sum_su_proses + record.sum_su_material) / record.sum_tk_pengiriman) * 100
            else:
                record.persentase_harian_pengiriman = 0.0
    
    @api.depends('product_line_ids.tk_pengiriman','product_line_ids.no_su_proses','product_line_ids.no_su_material')
    def _sum_tk_pengiriman(self):
        for record in self:
            subtotal_qty = sum(record.product_line_ids.mapped('tk_pengiriman'))
            subtotal_su_proses = sum(record.product_line_ids.mapped('no_su_proses'))
            subtotal_su_material = sum(record.product_line_ids.mapped('no_su_material'))
            record.sum_tk_pengiriman = subtotal_qty
            record.sum_su_proses = subtotal_su_proses
            record.sum_su_material = subtotal_su_material

    #PRE FINISHING
    sum_tk_finishing = fields.Integer('SUM Total Kirim', compute="_sum_tk_finishing")
    sum_su_prodution = fields.Integer('SU Produksi', compute='_sum_tk_finishing')
    sum_su_pre_finishing = fields.Integer('SU Pre Finishing', compute='_sum_tk_finishing')
    sum_su_kbl = fields.Integer('SU KBL', compute='_sum_tk_finishing')
    persentase_harian_finishing = fields.Float('% Harian', compute="_persentase_harian_finishing")

   
    @api.depends('sum_tk_finishing', 'sum_su_prodution','sum_su_pre_finishing','sum_su_kbl')
    def _persentase_harian_finishing(self):
        for record in self:
            if record.sum_tk_finishing != 0:
                record.persentase_harian_finishing = ((record.sum_su_prodution + record.sum_su_pre_finishing + record.sum_su_kbl) / record.sum_tk_finishing) * 100
            else:
                record.persentase_harian_finishing = 0.0

    @api.depends('product_line_ids.tk_finishing','product_line_ids.su_prodution','product_line_ids.su_pre_finishing','product_line_ids.su_kbl')
    def _sum_tk_finishing(self):
        for record in self:
            subtotal_qty = sum(record.product_line_ids.mapped('tk_finishing'))
            subtotal_su_prodution= sum(record.product_line_ids.mapped('su_prodution'))
            subtotal_su_pre_finishing= sum(record.product_line_ids.mapped('su_pre_finishing'))
            subtotal_su_kbl = sum(record.product_line_ids.mapped('su_kbl'))
            record.sum_tk_finishing = subtotal_qty
            record.sum_su_prodution = subtotal_su_prodution
            record.sum_su_pre_finishing = subtotal_su_pre_finishing
            record.sum_su_kbl = subtotal_su_kbl

    #TOP COAT
    sum_tk_coat = fields.Integer('SUM Total Kirim', compute="_sum_tk_coat")
    sum_su_proses_coat = fields.Integer('SUM SU Proses', compute='_sum_tk_coat')
    sum_su_pre_finishing_coat = fields.Integer('SUM SU Pre Finishing', compute='_sum_tk_coat')
    sum_su_coat_finishing  = fields.Integer('SUM SU Top Coat Finishing', compute='_sum_tk_coat')
    persentase_harian_coat = fields.Float('% Harian', compute="_persentase_harian_coat")

    @api.depends('sum_tk_coat', 'sum_su_proses_coat','sum_su_pre_finishing_coat','sum_su_coat_finishing')
    def _persentase_harian_coat(self):
        for record in self:
            if record.sum_tk_coat != 0:
                record.persentase_harian_coat = ((record.sum_su_proses_coat + record.sum_su_pre_finishing_coat + record.sum_su_coat_finishing) / record.sum_tk_coat) * 100
            else:
                record.persentase_harian_coat = 0.0

   
    @api.depends('product_line_ids.tk_coat','product_line_ids.su_proses_coat','product_line_ids.su_pre_finishing_coat','product_line_ids.su_coat_finishing')
    def _sum_tk_coat(self):
        for record in self:
            subtotal_qty = sum(record.product_line_ids.mapped('tk_coat'))
            subtotal_su_proses_coat= sum(record.product_line_ids.mapped('su_proses_coat'))
            subtotal_su_pre_finishing_coat= sum(record.product_line_ids.mapped('su_pre_finishing_coat'))
            subtotal_su_coat_finishing = sum(record.product_line_ids.mapped('su_coat_finishing'))
            record.sum_tk_coat = subtotal_qty
            record.sum_su_proses_coat = subtotal_su_proses_coat
            record.sum_su_pre_finishing_coat = subtotal_su_pre_finishing_coat
            record.sum_su_coat_finishing = subtotal_su_coat_finishing

    #PACKING
    sum_tk_packing = fields.Integer('SUM Total Kirim', compute="_sum_tk_packing")
    sum_su_proses_packing = fields.Integer('SU Proses' ,compute='_sum_tk_packing')
    sum_su_pre_finishing_packing = fields.Integer('SU Pre Finishing' ,compute='_sum_tk_packing')
    sum_su_packing_finishing = fields.Integer('SU Top packing Finishing' ,compute='_sum_tk_packing')
    persentase_harian_packing = fields.Float('% Harian', compute="_persentase_harian_packing")

    @api.depends('sum_tk_packing', 'sum_su_proses_packing','sum_su_pre_finishing_packing','sum_su_packing_finishing')
    def _persentase_harian_packing(self):
        for record in self:
            if record.sum_tk_packing != 0:
                record.persentase_harian_packing = ((record.sum_su_proses_packing + record.sum_su_pre_finishing_packing + record.sum_su_packing_finishing) / record.sum_tk_packing) * 100
            else:
                record.persentase_harian_packing = 0.0

    @api.depends('product_line_ids.su_proses_packing','product_line_ids.su_pre_finishing_packing','product_line_ids.su_packing_finishing','product_line_ids.tk_packing')
    def _sum_tk_packing(self):
        for record in self:
            subtotal_qty = sum(record.product_line_ids.mapped('tk_packing'))
            subtotal_sum_su_proses_packing= sum(record.product_line_ids.mapped('su_proses_packing'))
            subtotal_su_pre_finishing_coat= sum(record.product_line_ids.mapped('su_pre_finishing_packing'))
            subtotal_su_packing_finishing = sum(record.product_line_ids.mapped('su_packing_finishing'))
            record.sum_tk_packing = subtotal_qty
            record.sum_su_proses_packing = subtotal_sum_su_proses_packing
            record.sum_su_pre_finishing_packing = subtotal_su_pre_finishing_coat
            record.sum_su_packing_finishing = subtotal_su_packing_finishing

    #BRAS COMPONENT
    sum_tk_component = fields.Integer('SUM Total Kirim', compute='_sum_tk_component')
    sum_su_proses_component = fields.Integer('SU Proses', compute='_sum_tk_component')
    sum_su_component_material = fields.Integer('SU Proses' ,compute='_sum_tk_component')
    persentase_harian_component = fields.Float('% Harian', compute="_persentase_harian_component")


    @api.depends('sum_tk_component', 'sum_su_proses_component','sum_su_component_material')
    def _persentase_harian_component(self):
        for record in self:
            if record.sum_tk_component != 0:
                record.persentase_harian_component = ((record.sum_su_proses_component + record.sum_su_component_material) / record.sum_tk_component) * 100
            else:
                record.persentase_harian_component = 0.0

    @api.depends('product_line_ids.tk_component','product_line_ids.su_proses_component','product_line_ids.su_component_material')
    def _sum_tk_component(self):
        for record in self:
            subtotal_qty = sum(record.product_line_ids.mapped('tk_component'))
            subtotal_sum_su_proses_component= sum(record.product_line_ids.mapped('su_proses_component'))
            subtotal_su_component_material= sum(record.product_line_ids.mapped('su_component_material'))
            record.sum_tk_component = subtotal_qty
            record.sum_su_proses_component = subtotal_sum_su_proses_component
            record.sum_su_component_material = subtotal_su_component_material

    #CUSHION
    sum_tk_cushion = fields.Integer('SUM Total Kirim', compute="_sum_tk_cushion")
    sum_jumlah_cushion = fields.Integer('SUM Defect', compute="_sum_tk_cushion")
    persentase_harian_cushion = fields.Float('% Harian',compute='_compute_harian_cushion')

    @api.depends('sum_tk_cushion', 'sum_jumlah_cushion')
    def _compute_harian_cushion(self):
        for record in self:
            if record.sum_tk_cushion != 0:
                record.persentase_harian_cushion = (record.sum_jumlah_cushion / record.sum_tk_cushion) * 100
            else:
                record.persentase_harian_cushion = 0.0
    
    @api.depends('product_line_ids.tk_cushion','product_line_ids.jumlah_cushion')
    def _sum_tk_cushion(self):
        for record in self:
            subtotal_qty = sum(record.product_line_ids.mapped('tk_cushion'))
            subtotal_jumlah_cushion= sum(record.product_line_ids.mapped('jumlah_cushion'))
            record.sum_tk_cushion = subtotal_qty
            record.sum_jumlah_cushion = subtotal_jumlah_cushion

    #KAWAI TOP
    sum_tk_kawai_top = fields.Integer('SUM Total Kirim', compute='_compute_sum_tk_kawai')
    sum_su_kawai_top = fields.Integer('SUM Defect', compute='_compute_sum_tk_kawai')
    persentase_harian_kawai_top = fields.Float('% Harian', compute='_compute_persentase_harian_kawai')

    @api.depends('product_line_ids.tk_kawai_top','product_line_ids.su_kawai_top')
    def _compute_sum_tk_kawai(self):
        for record in self:
            subtotal_qty = sum(record.product_line_ids.mapped('tk_kawai_top'))
            subtotal_su_kawai_top= sum(record.product_line_ids.mapped('su_kawai_top'))
            record.sum_tk_kawai_top = subtotal_qty
            record.sum_su_kawai_top = subtotal_su_kawai_top

    @api.depends('sum_tk_kawai_top', 'sum_su_kawai_top')
    def _compute_persentase_harian_kawai(self):
        for record in self:
            if record.sum_tk_kawai_top != 0:
                record.persentase_harian_kawai_top = (record.sum_su_kawai_top / record.sum_tk_kawai_top) * 100
            else:
                record.persentase_harian_kawai_top = 0.0


    def button_confirm(self):
        self.write({
            'state' : 'confirm',
        })


    def button_cancel(self):
        self.write({
            'state' : 'draft'
        })

    def unlink(self):
        confirmed_records = self.filtered(lambda record: record.state == 'confirm')
        if confirmed_records:
            raise ValidationError("You cannot delete confirmed records.")
        return super().unlink()
    
    # def button_defect(self):
    #     master_defect_obj = self.env['master.defect']
    #     master_defects = []

    #     for product_line in self.product_line_ids:
    #         master_defect_values = {
    #             'product_id': product_line.product_id.id,
    #             'no_inspection_id': self.id,
    #             'no_su': product_line.no_su,
    #             'code_id': product_line.code_id.id,
    #             'ket_ids': [(6, 0, product_line.ket_ids.ids)],
    #         }

    #         master_defect = master_defect_obj.create(master_defect_values)
    #         master_defects.append(master_defect.id)

    #     button_data = {
    #         'type': 'ir.actions.act_window',
    #         'name': _('Packing List'),
    #         'res_model': 'master.defect',
    #         'view_mode': 'tree,form',
    #         'target': 'current',
    #         'search_view_id': False,
    #         'domain': [('id', 'in', master_defects)],  # Menampilkan hanya master.defect yang baru dibuat
    #     }
    #     return button_data




class InspectionTagCard(models.Model):
    _name = 'inspection.tag.card.line'
    
    inspection_tagcard_id = fields.Many2one(comodel_name='inspection.tag.card', string='Inspection Tagcard')
    product_tmpl_id = fields.Many2one('product.template', string='Product', related='product_id.product_tmpl_id')
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Jenis Komponen',
        required=True,)

    no_tk = fields.Integer('TK (PCS)', store=True)
    no_lp = fields.Integer('LP (PCS)', store=True,)
    no_su = fields.Integer('SU (PCS)', store=True,compute='_compute_no_su')
    # code_id = fields.Many2one('jidoka.ketmasalah', string='Code Masalah')
    # ket_masalah_ids = fields.Many2many('jidoka.isi.defect', string='ket_masalah', related='code_id.description_ids', readonly=False)
    # ket_ids= fields.Many2many('jidoka.isi.defect', string='KET. Masalah')
    # code1_id = fields.Many2one('jidoka.ketmasalah', string='Code Masalah')
    # ket_masalah1_ids = fields.Many2many(confirm'jidoka.isi.defect', string='ket_masalah', related='code1_id.description_ids', readonly=False)
    # ket1_ids= fields.Many2many('jidoka.isi.defect', string='KET. Masalah')
    code_id = fields.Many2one('jidoka.ketmasalah', string='Code Masalah')
    ket_masalah_id = fields.Many2one('jidoka.isi.defect', string='ket_masalah', readonly=False)
    # ket_ids = fields.Many2many('jidoka.isi.defect', string='KET. Masalah')
    code1_id = fields.Many2one('jidoka.ketmasalah', string='Code Masalah 1')
    ket_masalah1_id = fields.Many2one('jidoka.isi.defect', string='ket_masalah 1', readonly=False)
    # ket1_ids = fields.Many2many('jidoka.isi.defect', string='KET. Masalah 1')
    ket_id = fields.Many2one('jidoka.isi.defect',  string='KET. Masalah')
    ket1_id = fields.Many2one('jidoka.isi.defect', string='KET. Masalah 1')
    no_kbl = fields.Integer('KBL (PCS)', store=True,compute='_compute_no_kbl')
    product_uom_qty = fields.Float('Quantity')
    master_defect_ids = fields.One2many('inspection.tag.card.operation', 'inspection_tag_card_line_id', string='Master Defects')

    #PEMBAHANAN
    size_tebal = fields.Float("Size Tebal", related = 'product_id.size_tebal')
    size_lebar = fields.Float("Size Lebar", related = 'product_id.size_lebar')
    size_panjang = fields.Float("Size Panjang", related = 'product_id.size_panjang')
    ukuran_pembahanan = fields.Text('Ukuran', compute="_compute_ukuran")
    jenis_kayu_pembahanan_id = fields.Many2one('jidoka.woodkind', string='Jenis Kayu', related='product_id.wood_kind_id')
    tk_pembahanan = fields.Integer('TK (Quantity)', compute='_compute_tk_pembahanan')
    product_code = fields.Char('Code', related='product_tmpl_id.product_code')
    persentase = fields.Float('%',compute="_compute_persentase")

    
    @api.depends('no_lp', 'no_su')
    def _compute_tk_pembahanan(self):
        for record in self:
            record.tk_pembahanan = (record.no_lp + record.no_su)
           


    @api.depends('no_su', 'inspection_tagcard_id.sum_total_kirim')
    def _compute_persentase(self):
        for record in self:
            if record.inspection_tagcard_id.sum_total_kirim != 0:
                record.persentase = (record.no_su / record.inspection_tagcard_id.sum_total_kirim) * 100
            else:
                record.persentase = 0.0


    @api.depends('size_tebal', 'size_lebar', 'size_panjang')
    def _compute_ukuran(self):
        for r in self:
            size_tebal = r.size_tebal
            size_lebar = r.size_lebar
            size_panjang = r.size_panjang
            if size_tebal == False:
                size_tebal = ''
            if size_lebar == False:
                size_lebar = ''
            if size_panjang == False:
                size_panjang = ''
            r.ukuran_pembahanan = "%s x %s x %s" % (size_tebal, size_lebar, size_panjang)


    #PROSES PENGIRIMAN
    no_su_proses = fields.Integer('SU Proses', compute='_no_su_proses')
    no_su_material = fields.Integer('SU Material', compute='_no_su_material')
    persentase_proses = fields.Float('% Proses', compute='_compute_persentase_proses')
    persentase_material = fields.Float('% Material',compute='_compute_persentase_material')
    tk_pengiriman = fields.Integer('TK (Quantity)', compute='_compute_tk_pengiriman')

    @api.depends('no_lp', 'no_su_proses','no_su_material')
    def _compute_tk_pengiriman(self):
        for record in self:
            record.tk_pengiriman = (record.no_lp + record.no_su_proses  + record.no_su_material)

    @api.depends('no_su_material', 'inspection_tagcard_id.sum_tk_pengiriman')
    def _compute_persentase_material(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_pengiriman:
                line.persentase_material = (line.no_su_material / line.inspection_tagcard_id.sum_tk_pengiriman) * 100
            else:
                line.persentase_material = 0.0

    @api.depends('no_su_proses', 'inspection_tagcard_id.sum_tk_pengiriman')
    def _compute_persentase_proses(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_pengiriman:
                line.persentase_proses = (line.no_su_proses / line.inspection_tagcard_id.sum_tk_pengiriman) * 100
            else:
                line.persentase_proses = 0.0

    #PRE FINISHING
    su_prodution = fields.Integer('SU Produksi', compute='_su_prodution')
    su_pre_finishing = fields.Integer('SU Pre Finishing', compute='_su_pre_finishing')
    su_kbl = fields.Integer('SU KBL', compute='_su_kbl')
    tk_finishing = fields.Integer('TK (Quantity)', compute='_compute_tk_finishing')
    persentase_production = fields.Float('% Produksi', compute='_compute_persentase_production')
    persentase_pre_finishing = fields.Float('% Pre Finishing',compute='_compute_persentase_pre_finishing')
    persentase_kbl= fields.Float('% KBL',compute='_compute_persentase_kbl')


    @api.depends('su_kbl', 'inspection_tagcard_id.sum_tk_finishing')
    def _compute_persentase_kbl(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_finishing:
                line.persentase_kbl = (line.su_kbl / line.inspection_tagcard_id.sum_tk_finishing) * 100
            else:
                line.persentase_kbl = 0.0

    @api.depends('su_pre_finishing', 'inspection_tagcard_id.sum_tk_finishing')
    def _compute_persentase_pre_finishing(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_finishing:
                line.persentase_pre_finishing = (line.su_pre_finishing / line.inspection_tagcard_id.sum_tk_finishing) * 100
            else:
                line.persentase_pre_finishing = 0.0

    @api.depends('su_prodution', 'inspection_tagcard_id.sum_tk_finishing')
    def _compute_persentase_production(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_finishing:
                line.persentase_production = (line.su_prodution / line.inspection_tagcard_id.sum_tk_finishing) * 100
            else:
                line.persentase_production = 0.0

    @api.depends('no_lp', 'su_prodution','su_pre_finishing','su_kbl')
    def _compute_tk_finishing(self):
        for record in self:
            record.tk_finishing = (record.no_lp + record.su_prodution + record.su_pre_finishing + record.su_kbl)


    #TOP COAT
    su_proses_coat = fields.Integer('SU Proses' ,compute='_su_proses_coat')
    su_pre_finishing_coat = fields.Integer('SU Pre Finishing' ,compute='_su_pre_finishing_coat')
    su_coat_finishing = fields.Integer('SU Top Coat Finishing' ,compute='_su_coat_finishing')
    tk_coat = fields.Integer('TK (Quantity)', compute='_compute_tk_coat')
    persentase_proeses = fields.Float('% Proses', compute='_compute_persentase_proses_coat')
    persentase_pre_finishing_coat = fields.Float('% Pre Finishing',compute='_compute_persentase_proses_coat')
    persentase_coat_finishing= fields.Float('% Top Coat Finishing',compute='_compute_persentase_proses_coat')


    @api.depends('su_proses_coat','su_pre_finishing_coat','su_coat_finishing', 'inspection_tagcard_id.sum_tk_coat')
    def _compute_persentase_proses_coat(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_coat:
                line.persentase_proeses = (line.su_proses_coat / line.inspection_tagcard_id.sum_tk_coat) * 100
                line.persentase_pre_finishing_coat = (line.su_pre_finishing_coat / line.inspection_tagcard_id.sum_tk_coat) * 100
                line.persentase_coat_finishing = (line.su_coat_finishing / line.inspection_tagcard_id.sum_tk_coat) * 100
            else:
                line.persentase_proeses = 0.0
                line.persentase_pre_finishing_coat = 0.0
                line.persentase_coat_finishing = 0.0


    @api.depends('no_lp', 'su_proses_coat','su_pre_finishing_coat','su_coat_finishing')
    def _compute_tk_coat(self):
        for record in self:
            record.tk_coat = (record.no_lp + record.su_proses_coat + record.su_pre_finishing_coat + record.su_coat_finishing)


    @api.depends('inspection_tagcard_id.operation_line_ids.su_proses_coat')
    def _su_proses_coat(self):
        for line in self:
            total_no_su = 0
            for operation_line in line.inspection_tagcard_id.operation_line_ids:
                if operation_line.product_id == line.product_id:
                    total_no_su += operation_line.su_proses_coat
            line.su_proses_coat = total_no_su

    @api.depends('inspection_tagcard_id.operation_line_ids.su_pre_finishing_coat')
    def _su_pre_finishing_coat(self):
        for line in self:
            total_no_su = 0
            for operation_line in line.inspection_tagcard_id.operation_line_ids:
                if operation_line.product_id == line.product_id:
                    total_no_su += operation_line.su_pre_finishing_coat
            line.su_pre_finishing_coat = total_no_su

    @api.depends('inspection_tagcard_id.operation_line_ids.su_coat_finishing')
    def _su_coat_finishing(self):
        for line in self:
            total_no_su = 0
            for operation_line in line.inspection_tagcard_id.operation_line_ids:
                if operation_line.product_id == line.product_id:
                    total_no_su += operation_line.su_coat_finishing
            line.su_coat_finishing = total_no_su


    #PACKING    
    su_proses_packing = fields.Integer('SU Produksi' ,compute='_su_proses_packing')
    su_pre_finishing_packing = fields.Integer('SU Pre Finishing' ,compute='_su_proses_packing')
    su_packing_finishing = fields.Integer('SU Top packing Finishing' ,compute='_su_proses_packing')
    tk_packing = fields.Integer('TK (Quantity)', compute='_compute_tk_packing')
    persentase_proeses_packing = fields.Float('% Produksi', compute='_compute_persentase_proeses_packing')
    persentase_pre_finishing_packing = fields.Float('% Pre Finishing',compute='_compute_persentase_proeses_packing')
    persentase_packing_finishing= fields.Float('% Top packing Finishing',compute='_compute_persentase_proeses_packing')


    @api.depends('su_proses_packing','su_pre_finishing_packing','su_packing_finishing', 'inspection_tagcard_id.sum_tk_packing')
    def _compute_persentase_proeses_packing(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_packing:
                line.persentase_proeses_packing = (line.su_proses_packing / line.inspection_tagcard_id.sum_tk_packing) * 100
                line.persentase_pre_finishing_packing = (line.su_pre_finishing_packing / line.inspection_tagcard_id.sum_tk_packing) * 100
                line.persentase_packing_finishing = (line.su_packing_finishing / line.inspection_tagcard_id.sum_tk_packing) * 100
            else:
                line.persentase_proeses_packing = 0.0
                line.persentase_pre_finishing_packing = 0.0
                line.persentase_packing_finishing = 0.0

    @api.depends('inspection_tagcard_id.operation_line_ids.su_proses_packing','inspection_tagcard_id.operation_line_ids.su_pre_finishing_packing','inspection_tagcard_id.operation_line_ids.su_packing_finishing')
    def _su_proses_packing(self):
        for line in self:
            total_su_proses_packing = 0
            total_su_pre_finishing_packing = 0
            total_su_packing_finishing = 0
            for operation_line in line.inspection_tagcard_id.operation_line_ids:
                if operation_line.product_id == line.product_id:
                    total_su_proses_packing += operation_line.su_proses_packing
                    total_su_pre_finishing_packing += operation_line.su_pre_finishing_packing
                    total_su_packing_finishing += operation_line.su_packing_finishing
            line.su_proses_packing = total_su_proses_packing
            line.su_pre_finishing_packing = total_su_pre_finishing_packing
            line.su_packing_finishing = total_su_packing_finishing

    @api.depends('no_lp', 'su_proses_packing','su_pre_finishing_packing','su_packing_finishing')
    def _compute_tk_packing(self):
        for record in self:
            record.tk_packing = (record.no_lp + record.su_proses_packing + record.su_pre_finishing_packing + record.su_packing_finishing)


    #BRAS COMPONENT
    tk_component= fields.Integer('TK (Quantity)', compute='_compute_tk_component')
    su_proses_component = fields.Integer('SU Proses', compute='_compute_su_component')
    su_component_material = fields.Integer('SU Material', compute='_compute_su_component')
    persentase_proses_component = fields.Float('% Proses', compute='_compute_persentase_proses_component')
    persentase_component_material = fields.Float('% Material', compute='_compute_persentase_proses_component')

    @api.depends('su_proses_component','su_component_material','inspection_tagcard_id.sum_tk_component')
    def _compute_persentase_proses_component(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_component:
                line.persentase_proses_component = (line.su_proses_component / line.inspection_tagcard_id.sum_tk_component) * 100
                line.persentase_component_material = (line.su_component_material / line.inspection_tagcard_id.sum_tk_component) * 100
            else:
                line.persentase_proses_component = 0.0
                line.persentase_component_material = 0.0


    @api.depends('inspection_tagcard_id.operation_line_ids.su_proses_component','inspection_tagcard_id.operation_line_ids.su_component_material')
    def _compute_su_component(self):
        for line in self:
            total_su_proses_component = 0
            total_su_component_material  = 0
            for operation_line in line.inspection_tagcard_id.operation_line_ids:
                if operation_line.product_id == line.product_id:
                    total_su_proses_component += operation_line.su_proses_component
                    total_su_component_material  += operation_line.su_component_material 
            line.su_proses_component = total_su_proses_component
            line.su_component_material  = total_su_component_material 



    @api.depends('no_lp', 'su_proses_component','su_component_material')
    def _compute_tk_component(self):
        for record in self:
            record.tk_component = (record.no_lp + record.su_proses_component + record.su_component_material)


    #CUSHION
    tk_cushion = fields.Integer('TK (Quantity)', compute='_compute_tk_cushion')
    jumlah_cushion = fields.Integer('Jumlah', compute="_compute_jumlah_cushion") 
    persentase_cushion = fields.Float('% Defect', compute='_compute_persentase_cushion')

    @api.depends('jumlah_cushion','inspection_tagcard_id.sum_tk_cushion')
    def _compute_persentase_cushion(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_cushion:
                line.persentase_cushion = (line.jumlah_cushion / line.inspection_tagcard_id.sum_tk_cushion) * 100
            else:
                line.persentase_cushion = 0.0
 
    @api.depends('inspection_tagcard_id.operation_line_ids.jumlah_cushion')
    def _compute_jumlah_cushion(self):
        for line in self:
            total_jumlah_cushion = 0
            for operation_line in line.inspection_tagcard_id.operation_line_ids:
                if operation_line.product_id == line.product_id:
                    total_jumlah_cushion += operation_line.jumlah_cushion
            line.jumlah_cushion = total_jumlah_cushion


    @api.depends('no_lp','jumlah_cushion')
    def _compute_tk_cushion(self):
        for record in self:
            record.tk_cushion = (record.no_lp + record.jumlah_cushion)


    #KAWAI TOP COAT
    top_coat_id = fields.Many2one('top.coat', string='Top Coat')
    su_kawai_top = fields.Integer('SU (PCS)', compute='_compute_su_kawai_top')
    tk_kawai_top = fields.Integer('TK (Quantity)', compute='_compute_tk_kawai_top')
    persentese_kawai = fields.Float('%', compute='_compute_persentase_kawai')

    @api.depends('su_kawai_top','inspection_tagcard_id.sum_tk_kawai_top')
    def _compute_persentase_kawai(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_kawai_top:
                line.persentese_kawai = (line.su_kawai_top / line.inspection_tagcard_id.sum_tk_kawai_top) * 100
            else:
                line.persentese_kawai = 0.0
    
    @api.depends('no_lp','su_kawai_top')
    def _compute_tk_kawai_top(self):
        for record in self:
            record.tk_kawai_top = (record.no_lp + record.su_kawai_top)

    @api.depends('inspection_tagcard_id.operation_line_ids.su_kawai_top')
    def _compute_su_kawai_top(self):
        for line in self:
            total_su_kawai_top = 0
            for operation_line in line.inspection_tagcard_id.operation_line_ids:
                if operation_line.product_id == line.product_id:
                    total_su_kawai_top += operation_line.su_kawai_top
            line.su_kawai_top = total_su_kawai_top

    

    @api.depends('inspection_tagcard_id.operation_line_ids.su_kbl')
    def _su_kbl(self):
        for line in self:
            total_no_su = 0
            for operation_line in line.inspection_tagcard_id.operation_line_ids:
                if operation_line.product_id == line.product_id:
                    total_no_su += operation_line.su_kbl
            line.su_kbl = total_no_su
    
    @api.depends('inspection_tagcard_id.operation_line_ids.su_pre_finishing')
    def _su_pre_finishing(self):
        for line in self:
            total_no_su = 0
            for operation_line in line.inspection_tagcard_id.operation_line_ids:
                if operation_line.product_id == line.product_id:
                    total_no_su += operation_line.su_pre_finishing
            line.su_pre_finishing = total_no_su

    @api.depends('inspection_tagcard_id.operation_line_ids.su_prodution')
    def _su_prodution(self):
        for line in self:
            total_no_su = 0
            for operation_line in line.inspection_tagcard_id.operation_line_ids:
                if operation_line.product_id == line.product_id:
                    total_no_su += operation_line.su_prodution
            line.su_prodution = total_no_su

    @api.depends('inspection_tagcard_id.operation_line_ids.no_su_material')
    def _no_su_material(self):
        for line in self:
            total_no_su = 0
            for operation_line in line.inspection_tagcard_id.operation_line_ids:
                if operation_line.product_id == line.product_id:
                    total_no_su += operation_line.no_su_material
            line.no_su_material = total_no_su

    @api.depends('inspection_tagcard_id.operation_line_ids.no_su_proses')
    def _no_su_proses(self):
        for line in self:
            total_no_su = 0
            for operation_line in line.inspection_tagcard_id.operation_line_ids:
                if operation_line.product_id == line.product_id:
                    total_no_su += operation_line.no_su_proses
            line.no_su_proses = total_no_su

    # @api.constrains('no_su')
    # def _check_no_su(self):
    #     for line in self:
    #         if line.no_su > line.product_uom_qty:
    #             raise ValidationError("SU cannot be greater than Quantity.")
            
    # @api.constrains('no_kbl')
    # def _check_no_kbl(self):
    #     for line in self:
    #         if line.no_kbl > line.product_uom_qty:
    #             raise ValidationError("KBL cannot be greater than Quantity.")
   

    @api.depends('inspection_tagcard_id.operation_line_ids.no_su')
    def _compute_no_su(self):
        for line in self:
            total_no_su = 0
            for operation_line in line.inspection_tagcard_id.operation_line_ids:
                if operation_line.product_id == line.product_id:
                    total_no_su += operation_line.no_su
            line.no_su = total_no_su
    # @api.depends('inspection_tagcard_id.operation_line_ids.no_su')
    # def _compute_no_su(self):
    #     for line in self:
    #         total_no_su = 0
    #         sorted_operation_lines = line.inspection_tagcard_id.operation_line_ids.sorted(key=lambda x: x.id, reverse=True)
    #         for operation_line in sorted_operation_lines:
    #             if operation_line.product_id == line.product_id:
    #                 total_no_su = operation_line.no_su
    #                 break
    #         line.no_su = total_no_su


    @api.depends('inspection_tagcard_id.operation_line_ids.no_kbl')
    def _compute_no_kbl(self):
        for line in self:
            total_no_kbl = 0
            for operation_line in line.inspection_tagcard_id.operation_line_ids:
                if operation_line.product_id == line.product_id:
                    total_no_kbl += operation_line.no_kbl
            line.no_kbl = total_no_kbl

    # @api.onchange('no_su')
    # def _check_no_su(self):
    #     for line in self:
    #         if line.no_su > line.product_uom_qty:
    #             raise ValidationError("No SU cannot be greater than the Quantity.")
   
class MasterDefect(models.Model):
    _name = 'inspection.tag.card.operation'

    product_id = fields.Many2one(
            comodel_name='product.product',
            string='Jenis Komponen',
            required=True,domain="[('id', 'in', tes_ids)]"
    )
    fabric_colour_id = fields.Many2one('res.fabric.colour', string='Colour')
    inspection_tag_card_line_id = fields.Many2one('inspection.tag.card.line', string='Inspection Tagcard Line',)

    inspection_tagcard_id = fields.Many2one(comodel_name='inspection.tag.card', string='Inspection Tagcard')
    code_id = fields.Many2one('jidoka.ketmasalah', string='Code Masalah')
    ket_masalah_id= fields.Many2one('jidoka.isi.defect', string='Defect', readonly=False)
    code1_id = fields.Many2one('jidoka.ketmasalah', string='Code Masalah ')
    ket_masalah1_id = fields.Many2one('jidoka.isi.defect', string='Defect', readonly=False)
    ket_id = fields.Many2one('jidoka.isi.defect',  string='KET. Masalah')
    ket1_id = fields.Many2one('jidoka.isi.defect', string='KET. Masalah ')
    no_kbl = fields.Integer('KBL (PCS)', store=True)
    # filtered_product_ids = fields.Many2many(comodel_name='product.product', string='Filtered Products', compute='_compute_filtered_product_ids')
    #PEMBAHANAN
    persentase = fields.Float('%',compute="_compute_persentase")
    no_su = fields.Integer('SU (PCS)', store=True)

    @api.depends('no_su', 'inspection_tagcard_id.sum_total_kirim')
    def _compute_persentase(self):
        for record in self:
            if record.inspection_tagcard_id.sum_total_kirim != 0:
                record.persentase = (record.no_su / record.inspection_tagcard_id.sum_total_kirim) * 100
            else:
                record.persentase = 0.0

    #PROSES PENGIRIMAN
    defect_proses_id = fields.Many2one('jidoka.isi.defect', string='Defect Proses')
    defect_material_id = fields.Many2one('jidoka.isi.defect', string='Defect Material')
    no_su_proses = fields.Integer('SU Proses')
    no_su_material = fields.Integer('SU Material')
    persentase_proses = fields.Float('% Proses', compute='_compute_persentase_proses')
    persentase_material = fields.Float('% Material',compute='_compute_persentase_material')

    @api.depends('no_su_material', 'inspection_tagcard_id.sum_tk_pengiriman')
    def _compute_persentase_material(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_pengiriman:
                line.persentase_material = (line.no_su_material / line.inspection_tagcard_id.sum_tk_pengiriman) * 100
            else:
                line.persentase_material = 0.0

    @api.depends('no_su_proses', 'inspection_tagcard_id.sum_tk_pengiriman')
    def _compute_persentase_proses(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_pengiriman:
                line.persentase_proses = (line.no_su_proses / line.inspection_tagcard_id.sum_tk_pengiriman) * 100
            else:
                line.persentase_proses = 0.0

    #PRE FINISHING
    defect_production_id = fields.Many2one('jidoka.isi.defect', string='Defect Produksi')
    defect_pre_finishing_id = fields.Many2one('jidoka.isi.defect', string='Defect Pre Finishing')
    defect_kbl_id = fields.Many2one('jidoka.isi.defect', string='Defect KBL')
    su_prodution = fields.Integer('SU Produksi')
    su_pre_finishing = fields.Integer('SU Pre Finishing')
    su_kbl = fields.Integer('SU KBL')
    persentase_production = fields.Float('% Produksi', compute='_compute_persentase_production')
    persentase_pre_finishing = fields.Float('% Pre Finishing',compute='_compute_persentase_pre_finishing')
    persentase_kbl= fields.Float('% KBL',compute='_compute_persentase_kbl')

    @api.depends('su_kbl', 'inspection_tagcard_id.sum_tk_finishing')
    def _compute_persentase_kbl(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_finishing:
                line.persentase_kbl = (line.su_kbl / line.inspection_tagcard_id.sum_tk_finishing) * 100
            else:
                line.persentase_kbl = 0.0

    @api.depends('su_pre_finishing', 'inspection_tagcard_id.sum_tk_finishing')
    def _compute_persentase_pre_finishing(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_finishing:
                line.persentase_pre_finishing = (line.su_pre_finishing / line.inspection_tagcard_id.sum_tk_finishing) * 100
            else:
                line.persentase_pre_finishing = 0.0

    @api.depends('su_prodution', 'inspection_tagcard_id.sum_tk_finishing')
    def _compute_persentase_production(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_finishing:
                line.persentase_production = (line.su_prodution / line.inspection_tagcard_id.sum_tk_finishing) * 100
            else:
                line.persentase_production = 0.0

    #TOP COAT
    defect_proses_coat_id = fields.Many2one('jidoka.isi.defect', string='Defect Proses')
    defect_pre_finishing_coat_id = fields.Many2one('jidoka.isi.defect', string='Defect Pre Finishing')
    defect_coat_finishing_id = fields.Many2one('jidoka.isi.defect', string='Defect Top Coat Finishing')
    su_proses_coat = fields.Integer('SU Proses')
    su_pre_finishing_coat = fields.Integer('SU Pre Finishing')
    su_coat_finishing = fields.Integer('SU Top Coat Finishing')
    persentase_proeses = fields.Float('% Proses', compute='_compute_persentase_proses_coat')
    persentase_pre_finishing_coat = fields.Float('% Pre Finishing',compute='_compute_persentase_proses_coat')
    persentase_coat_finishing= fields.Float('% Top Coat Finishing',compute='_compute_persentase_proses_coat')

    @api.depends('su_proses_coat','su_pre_finishing_coat','su_coat_finishing', 'inspection_tagcard_id.sum_tk_coat')
    def _compute_persentase_proses_coat(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_coat:
                line.persentase_proeses = (line.su_proses_coat / line.inspection_tagcard_id.sum_tk_coat) * 100
                line.persentase_pre_finishing_coat = (line.su_pre_finishing_coat / line.inspection_tagcard_id.sum_tk_coat) * 100
                line.persentase_coat_finishing = (line.su_coat_finishing / line.inspection_tagcard_id.sum_tk_coat) * 100
            else:
                line.persentase_proeses = 0.0
                line.persentase_pre_finishing_coat = 0.0
                line.persentase_coat_finishing = 0.0

    #PACKING
    defect_proses_packing_id = fields.Many2one('jidoka.isi.defect', string='Defect Produksi')
    defect_pre_finishing_packing_id = fields.Many2one('jidoka.isi.defect', string='Defect Pre Finishing')
    defect_packing_finishing_id = fields.Many2one('jidoka.isi.defect', string='Defect Top Coat Finishing')
    su_proses_packing = fields.Integer('SU Produksi')
    su_pre_finishing_packing = fields.Integer('SU Pre Finishing')
    su_packing_finishing = fields.Integer('SU Top Coat Finishing')
    persentase_proeses_packing = fields.Float('% Produksi', compute='_compute_persentase_proeses_packing')
    persentase_pre_finishing_packing = fields.Float('% Pre Finishing',compute='_compute_persentase_proeses_packing')
    persentase_packing_finishing= fields.Float('% Top packing Finishing',compute='_compute_persentase_proeses_packing')

    @api.depends('su_proses_packing','su_pre_finishing_packing','su_packing_finishing', 'inspection_tagcard_id.sum_tk_packing')
    def _compute_persentase_proeses_packing(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_packing:
                line.persentase_proeses_packing = (line.su_proses_packing / line.inspection_tagcard_id.sum_tk_packing) * 100
                line.persentase_pre_finishing_packing = (line.su_pre_finishing_packing / line.inspection_tagcard_id.sum_tk_packing) * 100
                line.persentase_packing_finishing = (line.su_packing_finishing / line.inspection_tagcard_id.sum_tk_packing) * 100
            else:
                line.persentase_proeses_packing = 0.0
                line.persentase_pre_finishing_packing = 0.0
                line.persentase_packing_finishing = 0.0

    #BRAS COMPONENT
    defect_proses_component_id = fields.Many2one('jidoka.isi.defect', string='Defect Proses')
    defect_material_component_id = fields.Many2one('jidoka.isi.defect', string='Defect Material')
    su_proses_component = fields.Integer('SU Proses')
    su_component_material = fields.Integer('SU Material')
    persentase_proses_component = fields.Float('% Proses', compute='_compute_persentase_proses_component')
    persentase_component_material = fields.Float('% Material', compute='_compute_persentase_proses_component')

    @api.depends('su_proses_component','su_component_material','inspection_tagcard_id.sum_tk_component')
    def _compute_persentase_proses_component(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_component:
                line.persentase_proses_component = (line.su_proses_component / line.inspection_tagcard_id.sum_tk_component) * 100
                line.persentase_component_material = (line.su_component_material / line.inspection_tagcard_id.sum_tk_component) * 100
            else:
                line.persentase_proses_component = 0.0
                line.persentase_component_material = 0.0


    #CUSHION
    defect_cushion_id = fields.Many2one('jidoka.isi.defect', string='Defect')
    jumlah_cushion = fields.Integer('Jumlah')  
    persentase_cushion = fields.Float('% Defect', compute='_compute_persentase_cushion')

    @api.depends('jumlah_cushion','inspection_tagcard_id.sum_tk_cushion')
    def _compute_persentase_cushion(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_cushion:
                line.persentase_cushion = (line.jumlah_cushion / line.inspection_tagcard_id.sum_tk_cushion) * 100
            else:
                line.persentase_cushion = 0.0  

    #KAWAI TOP
    defect_kawai_id = fields.Many2one('jidoka.isi.defect', string='Defect')
    su_kawai_top = fields.Integer('SU (PCS)')
    persentese_kawai = fields.Float('%', compute='_compute_persentase_kawai')

    @api.depends('su_kawai_top','inspection_tagcard_id.sum_tk_kawai_top')
    def _compute_persentase_kawai(self):
        for line in self:
            if line.inspection_tagcard_id.sum_tk_kawai_top:
                line.persentese_kawai = (line.su_kawai_top / line.inspection_tagcard_id.sum_tk_kawai_top) * 100
            else:
                line.persentese_kawai = 0.0

    tes_ids = fields.Many2many('inspection.tag.card.line', string='tes', compute='_compute_tes_ids')
    @api.depends('inspection_tagcard_id.product_line_ids')
    def _compute_tes_ids(self):
        for record in self:
            tes_lines = record.inspection_tagcard_id.product_line_ids
            record.tes_ids = [(6, 0, tes_lines.mapped('product_id').ids)]

  