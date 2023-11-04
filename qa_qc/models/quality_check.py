from email.policy import default
import string
from odoo import _,fields,api,models
from datetime import datetime

class QualityCheck(models.Model):
    _name = 'quality.check'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Quality Check"
    _rec_name = 'name'

    name = fields.Char(default="New", required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    lembar_pengesahan_bahan_id = fields.Many2one('lembar.pengesahan.bahan',)
    date = fields.Date(default=datetime.now())
    product_id = fields.Many2one('product.product', string='Product', required=True)
    # categ_id = fields.Many2one(string='Categori Product', comodel_name='product.product', related='product_id.categ_id')
    categ_id = fields.Many2one('product.category', string='Category Product' , compute='_compute_categ', store=True,)
    stts = fields.Selection(string='Status', selection=[('final', 'Final'),('re', 'Re-Inspek')])
    color_id = fields.Many2one(string='Warna', comodel_name='res.fabric.colour', tracking=True)
    # apabila kena tolak
    akar_masalah_ids = fields.Many2many('akar.masalah', string="Akar Masalah")
    attachment_doc = fields.Binary()
    tindakan_perbaikan_ids = fields.Many2many('tindakan.perbaikan', string="Tindakan Perbaikan")
    # attachment_docs = fields.One2many('my.attach', 'q', string='Attachment Docs')
    # attachment_img = fields.Binary()
    attachment_imgs = fields.One2many('img.att', 'parent_field_name' )

    # @api.onchange('product_id')
    # def onchange_product_id(self):
    #     if self.product_id:
    #         self.categ_id = self.product_id.categ_id.id
    
    @api.depends('product_id')
    def _compute_categ(self):
        for record in self:
            if record.product_id:
                record.categ_id = record.product_id.categ_id.id
    
    
    
            
    state = fields.Selection([
        ('draft', 'Draft'),
        ('check', 'Checking'),
        ('confirm', 'Confirm'),
        ('reject', 'Rejected'),
        ('done', 'Done'),
    ], default="draft")
    no_kendaraan = fields.Char()
    supplier_id = fields.Many2one('res.partner', string='Supplier/Jasa Oven')
    buyer_id = fields.Many2one('res.partner', string='Buyer')
    delivery_date = fields.Date()
    quantity_received = fields.Float()
    std_pembelian = fields.Char()
    level_id = fields.Many2one(
        'level.aql',
        string='Level AQL', default=False, domain=[('type', '=', 'bj')]
        )
    level2_id = fields.Many2one(
        'level.aql',
        string='Level AQL',  domain=[('type', '=', 'bpc')]
        )

    level3_id = fields.Many2one(
        'level.aql',
        string='Level AQL', domain=[('type', '=', 'bpsj')]
        )

    fix_lev = fields.Char(string='Fix')
    categ_name = fields.Char(string='Category NaME')
   
    @api.onchange('level_id')
    def onchange_level_id(self):
        if self.level_id:
           self.fix_lev = self.level_id.name


    @api.onchange('level2_id')
    def onchange_level2_id(self):
        if self.level2_id:
           self.fix_lev = self.level2_id.name


    @api.onchange('level3_id')
    def onchange_level3_id(self):
        if self.level3_id:
           self.fix_lev = self.level3_id.name

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        if self.categ_id:
            self.categ_name = self.categ_id.lev_aql_id
        else:
            self.categ_name = False
    

        # ,domain=[('level_id.categ_id', '=', 'other')]
    no_pi = fields.Char('No. PO')
    wood_kind_id = fields.Many2one(comodel_name='jidoka.woodkind', string='Jenis Kayu')
    line_ids = fields.One2many('quality.check.line', 'quality_id', string='line')
    actual_quantity = fields.Float('Jumlah yang ada', related="quantity_received", readonly=False, store=True,)
    quantity_checked = fields.Float('Jumlah yang diperiksa', compute="get_quantity_check", store=True)
    quantity_match = fields.Float('Jumlah yang sesuai')
    quantity_unmatch = fields.Float('Jumlah Ketidak Sesuaian', compute="_get_quantity_unmacth")
    keputusan = fields.Selection([
        ('terima', 'Terima'),
        ('tolak', 'Tolak'),
    ], compute="get_keputusan", readonly=True)
    uraian_ketidaksesuaian_ids = fields.One2many('uraian.ketidaksesuaian', 'quality_id')
    note = fields.Text()
    move_id = fields.Many2one('stock.move', string='Move',)
    picking_id = fields.Many2one('stock.picking', string='Move',)

    # data ttd QC
    disetujui = fields.Char('Disetujui')
    diperiksa = fields.Char('Diperiksa')
    dibuat= fields.Char(string='Dibuat')
    ttd_disetujui = fields.Binary('ttd_disetujui')
    ttd_diperiksa = fields.Binary('ttd_diperiksa')
    ttd_dibuat = fields.Binary('ttd_dibuat')
    
    @api.depends('quantity_unmatch')
    def get_keputusan(self):
        for rec in self:
            aql_id = self.get_aql(rec.quantity_received, self.product_id)
            if aql_id:
                if rec.quantity_unmatch == 0.0:
                    rec.keputusan = 'terima'
                elif rec.quantity_unmatch >= aql_id.re:
                    rec.keputusan = 'tolak'
                # elif rec.quantity_unmatch > aql_id.re:
                #     rec.keputusan = 'tolak'
                else : 
                    rec.keputusan = 'terima'

                # elif rec.quantity_unmatch == aql_id.ac:
                #     rec.keputusan = 'terima'
                # elif rec.quantity_unmatch != aql_id.ac:
                #     rec.keputusan = 'tolak'
                # elif rec.quantity_unmatch < 0.0:
                #     rec.keputusan = 'tolak'
                 #tergantung approval hold/tolak
                # elif rec.quantity_unmatch == aql_id.ac:
                #     rec.keputusan = 'terima'
                # elif rec.quantity_unmatch != aql_id.re:
                #     rec.keputusan = 'terima'

            else:
                rec.keputusan = False
                

    @api.depends('quantity_match', 'quantity_checked')
    def _get_quantity_unmacth(self):
        for rec in self:
            rec.quantity_unmatch = rec.quantity_checked - rec.quantity_match
    
    def get_aql(self, qty, product):
        aql_id = self.env['qc.aql.data'].search([
            ('min_lot', '<=', qty),
            # ('categ_id', '=', product.categ_id.id),
            ('max_lot', '>=', qty),
            ('name_lev','=', self.fix_lev)
        ], limit=1)
        return aql_id

    @api.onchange('fix_lev')
    @api.depends('quantity_received', 'product_id', 'fix_lev')
    def get_quantity_check(self):
        for rec in self:
            aql_id = self.get_aql(rec.quantity_received, self.product_id)
            if aql_id:
                rec.quantity_checked = aql_id.sample_size
            else:
                matching_aql_ids = self.env['qc.aql.data'].search([('name_lev', '=', rec.fix_lev)])
                if matching_aql_ids:
                    rec.quantity_checked = matching_aql_ids[0].sample_size
                else:
                    rec.quantity_checked = 0


    # @api.depends('quantity_received', 'product_id')
    # def get_quantity_check(self):
    #     for rec in self:
    #         aql_id = self.get_aql(rec.quantity_received,self.product_id)
    #         if aql_id:
    #             rec.quantity_checked = aql_id.sample_size
    #         else:
    #             rec.quantity_checked = 0
    @api.onchange('lembar_pengesahan_bahan_id')
    def _onchange_lembar_pengesahan_bahan_id(self):
        vals = []
        if self.line_ids :
            self.line_ids = False
        for rec in self.lembar_pengesahan_bahan_id.componen_ids:
            vals.append((0,0,{
                'name' : rec.name,
                'display_type' : rec.display_type,
                'sequence' : rec.sequence,
            }))
        if vals:
            self.line_ids = vals

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq = self.env['ir.sequence'].next_by_code('quality.check.seq') or 'New'
        vals['name'] = seq
        res = super(QualityCheck, self).create(vals)
        return res

    def action_view_inspection_tag_card(self):
        action = self.env["ir.actions.actions"]._for_xml_id("qa_qc.inspection_tag_card_action")
        return action

    def prepare_inspection_tag_card(self):
        vals = {
            'partner_id' : self.supplier_id.id,
            'user_id' : self.buyer_id.id,
            'product_id' : self.product_id.id,
            'categ_id' : self.product_id.categ_id.id,
            'date' : datetime.now(),
            'quantity' : self.actual_quantity,
            'status_pemeriksaan' : self.keputusan,
            'note' : self.note,
            'name' : self.name,
            'no_pi' : self.no_pi,
        }
        return vals

    def inspection_tag_card_action(self):
        """Create Inspection Tag Card via button inspection_tag_card_action"""
        action = self.action_view_inspection_tag_card()
        vals = self.prepare_inspection_tag_card()
        inspection_obj = self.env['inspection.tag.card']
        inspection_id = inspection_obj.create(vals)
        action['res_id'] = inspection_id.id
        action['views'] = [(self.env.ref('qa_qc.inspection_tag_card_view_form').id, 'form')]
        return action


    def check_button(self):
        self.write({
            'state' : 'check'
        })

    def confirm_button(self):
        self.write({
            'state' : 'confirm'
        })

    def done_button(self):
        self.write({
            'state' : 'done'
        })

    def reject_button(self):
        self.write({
            'state' : 'reject'
        })

    def set_to_draft_button(self):
        self.write({
            'state' : 'draft'
        })

class QualityCheckLine(models.Model):
    _name = 'quality.check.line'
    _description = "Quality Check Line"

    quality_id = fields.Many2one('quality.check', string='quality')
    name = fields.Char('Point Pemeriksaan')
    status = fields.Selection([
        ('sesuai', 'Sesuai'),
        ('tidak_sesuai', 'Tidak Sesuai'),
        ('n/a', 'N/A')
    ])
    sequence = fields.Integer(string='Sequence', default=10)
    keterangan = fields.Char()
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    # @api.depends('name')
    # def get_status(self):
    #     for rec in self:
    #         stl_id = self.get_aql(rec.quantity_received, self.product_id)
    #         if stl_id:
    #             if rec.name <= stl_id.ac:
    #                 rec.status = 'sesuai'
    #             elif rec.name >= stl_id.ac:
    #                 rec.status = 'n/a' #tergantung approval hold/tolak
    #             elif rec.name == stl_id.ac:
    #                 rec.status = 'sesuai'
    #         else:
    #             rec.status = False
                
class UraianKetidakSesuaian(models.Model):
    _name = 'uraian.ketidaksesuaian'
    _description = "Uraian Ketidaksesuaian"

    quality_id = fields.Many2one('quality.check', string='quality')
    name = fields.Char('Uraian Ketidaksesuaian')
    jumlah = fields.Float('Jumlah')

