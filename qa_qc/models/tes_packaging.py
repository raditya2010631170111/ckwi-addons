from odoo import _, api, fields, models
from datetime import date, datetime

class TesPackaging(models.Model):
    _name = 'tes.packaging'

    name = fields.Char(string='No', readonly=True, copy=False, required=True, 
        default=lambda self: self._generate_request_no(), tracking=True)
        
    @api.model
    def _generate_request_no(self):
        last_request = self.search([], order='id desc', limit=1)
        if last_request:
            last_no = last_request.name.split('/')[0]
            year = str(fields.Date.today().year)[-2:] 
            month = fields.Date.today().month
            new_no = int(last_no) + 1
            return f"{str(new_no).zfill(2)}/QA/ITL/{str(month).zfill(2)}/{year}"
        else:
            year = str(fields.Date.today().year)[-2:] 
            month = fields.Date.today().month
            requests = self.search([], order='id asc')
            if requests:
                return requests[0].name
            else:
                return f"01/QA/ITL/{str(month).zfill(2)}/{year}"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('repeat', 'Repeat'),
    ], default="draft")
          
    def button_confirm(self):
        self.write({
            'state' : 'confirm',
        })
        
    date = fields.Date(string='Date', default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Supplier')
    buyer_id = fields.Many2one('res.partner', string='Buyer')
    product_pembahanan_id = fields.Many2one('product.template', string='Item')
    product_tmpl_ids = fields.Many2many('product.product', 'tes_packaging_product_tmpl_rel', 'tag_id', 'product_id', string='Item Product', compute='_compute_product_tmpl_ids')
    product_id_domain_ids = fields.Many2many('product.product', 'tes_packaging_product_domain_rel_1', 'tag_id', 'product_id', readonly=False, string='Item Name')
    available_products = fields.Many2many('product.product', 'tes_packaging_product_domain_rel_2', 'tag_id', 'product_id', compute='_compute_available_products', store=True,readonly=False)
    no_mo_id = fields.Many2one('sale.order', string='No. PI/MO')
    fabric_colour_id = fields.Many2one('res.fabric.colour', string='Warna')
    line_ids = fields.One2many('tes.packaging.line', 'packaging_id', string='line')
    design_image = fields.One2many('tes.packaging.line', 'spec_id', string='line')
    cek_point_id = fields.Many2one('cek.point', string='Cek Point')
    woodkind_id = fields.Many2one('jidoka.woodkind', string='Material')
    max_line = fields.Integer(string='max_line', compute='_compute_max_line')

    @api.depends('line_ids.max_line')
    def _compute_max_line(self):
        for record in self:
            if record.line_ids:
                max_line = max(record.line_ids.mapped('max_line'))
                record.max_line = max_line
            else:
                record.max_line = 0 
    
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
                
    @api.onchange('cek_point_id')
    def _onchange_cek_point_id(self):
        vals = []
        if self.line_ids :
            self.line_ids = False
        for rec in self.cek_point_id.cek_point_line_ids.point_pemeriksaan_ids:
            vals.append((0,0,{
                'name' : rec.name,
                'cek_point_line_id': rec.cek_point_line_id.id,
                'sequence' : rec.sequence,
                'max_line' : rec.max_line,
                # 'display_type' : rec.display_type,
                # 'sequence' : rec.sequence,
            }))
        if vals:
            self.line_ids = vals
            
    unfinish_goods_ids = fields.Many2many('tes.cat.master', string="Unfinish Goods")
    finished_goods_ids = fields.Many2many('barang.jadi', string="Unfinished Goods")
    test_seq = fields.Integer(default=1, readonly=True)
    work_standard_ids = fields.Many2many('sumber.acuan',string="Work Standard")
    
    result_of_test = fields.Selection([
        ('pass','PASS'),
        ('pass2','PASS  (with repair)'),
        ('fail','FAIL')])
    pemeriksaan_selection = fields.Char('pemeriksaan_selection', compute="_compute_pemeriksaan_selection")
    hasil_pemeriksaan = fields.Char('hasil', compute='_compute_hasil')

    @api.depends('result_of_test')
    def _compute_pemeriksaan_selection(self):
        for record in self:
            if record.result_of_test == 'pass':
                record.pemeriksaan_selection = 'PASS'
            elif record.result_of_test == 'pass2':
                record.pemeriksaan_selection = 'PASS  (with repair)'
            elif record.result_of_test == 'fail':
                record.pemeriksaan_selection = 'FAIL'
            else:
                record.pemeriksaan_selection = ''
    
    @api.depends('result_of_test')
    def _compute_hasil(self):
        for record in self:
            if record.result_of_test == 'pass':
                record.hasil_pemeriksaan = 'Size / assembly / function / construction / etc. same with work standard'
            elif record.result_of_test == 'pass2':
                record.hasil_pemeriksaan = 'Size / assembly / function / construction / etc. there are not acceptable but not effect to construction'
            elif record.result_of_test == 'fail':
                record.hasil_pemeriksaan = 'Size / assembly / fuction / construction / etc. there are not acceptable and or effect to construction'
            else:
                record.hasil_pemeriksaan = ''
                
    note = fields.Text(string='Catatan',strip_style=True)
    dibuat= fields.Char(string='Prepared by')
    disetujui = fields.Char('Agreed by')
    ttd_dibuat = fields.Binary('Signature')
    ttd_disetujui = fields.Binary('Signature')
        
    def button_cancel(self):
        old_sequence = self.name
        new_doc = self.copy(default={
            'name': self._generate_request_no(),
            'test_seq': True,
            'result_of_test': self.result_of_test,
            'note': self.note,
            'design_image': [(0, 0, {
                'note': l.note,
                'attachment_img': l.attachment_img,
            }) for l in self.design_image],
            'line_ids': [(0, 0, {
                'sequence': ol.sequence,
                'name': ol.name,
                'status': ol.status,
                'keterangan': ol.keterangan,
                'req_name' : ol.req_name,
                'cek_point_line_id' : ol.cek_point_line_id.id,
            }) for ol in self.line_ids]
        })
        new_doc.write({'state': 'draft'})
        sorted_records = self.search([('name', '=', self.name)], order='test_seq DESC')
        highest_test_seq = sorted_records and sorted_records[0].test_seq or 0
        new_test_seq = highest_test_seq + 1
        new_doc.write({'test_seq': new_test_seq})
        self.write({
            'state' : 'repeat',
        })
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'tes.packaging',
            'res_id': new_doc.id,
            'view_mode': 'form',
            'target': 'current',
        }
        return action
        
class QualityCheckLine(models.Model):
    _name = 'tes.packaging.line'
    _description = "Tes Packaging Line"
    
    packaging_id = fields.Many2one('tes.packaging', string='packaging')
    spec_id = fields.Many2one('tes.packaging', string='konstruksi')
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
    note = fields.Text("Name")
    attachment_img = fields.Many2many('ir.attachment', string='Attachments', relation='tes_line_attachment_rel', column1='line_id', column2='attachment_id')
    first_attachment_img = fields.Binary("First Attachment Image", compute="_compute_first_attachment_img")
    second_attachment_img = fields.Binary("Second Attachment Image", compute="_compute_second_attachment_img")
    third_attachment_img = fields.Binary("Third Attachment Image", compute="_compute_third_attachment_img")

    @api.depends('attachment_img')
    def _compute_first_attachment_img(self):
        for line in self:
            first_attachment = line.attachment_img and line.attachment_img[0] or False
            line.first_attachment_img = first_attachment.datas if first_attachment else False

    @api.depends('attachment_img')
    def _compute_second_attachment_img(self):
        for line in self:
            second_attachment = line.attachment_img and line.attachment_img[1] if len(line.attachment_img) >= 2 else False
            line.second_attachment_img = second_attachment.datas if second_attachment else False

    @api.depends('attachment_img')
    def _compute_third_attachment_img(self):
        for line in self:
            third_attachment = line.attachment_img and line.attachment_img[2] if len(line.attachment_img) >= 3 else False
            line.third_attachment_img = third_attachment.datas if third_attachment else False
            
    cek_point_line_id = fields.Many2one('cek.point.line', string="Cek Point Details")
    req_name = fields.Char(string="Name", compute='_compute_req_name', store=True)
    is_computed = fields.Boolean('is_computed')
    max_line = fields.Integer('max_line')

    @api.depends('cek_point_line_id', 'sequence')
    def _compute_req_name(self):
        sequence_dict = {} 
        for record in self:
            if record.sequence in sequence_dict:
                record.is_computed = False  
            else:
                record.is_computed = True 
                sequence_dict[record.sequence] = True
            if record.is_computed and record.cek_point_line_id:
                record.req_name = record.cek_point_line_id.name
            else:
                record.req_name = ''