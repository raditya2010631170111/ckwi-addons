from odoo import _, api, fields, models
from datetime import date, datetime

class TesRebus(models.Model):
    _name = 'tes.rebus'
    _description = "QC Tes Rebus"

    name = fields.Char('Name', default=lambda self: _('New'), copy=False, readonly=True)
    partner_id = fields.Many2one('res.partner', string='Supplier')
    user_id = fields.Many2one('res.partner', string='Buyer')
    woodkind_id = fields.Many2one('jidoka.woodkind', string='Material', related='product_id.wood_kind_id', readonly=False)
    date = fields.Date('Date', required=True)
    colour_id = fields.Many2one('res.fabric.colour', string='Colour')
    product_id= fields.Many2one('product.product', string='Item')
    no_mo_id = fields.Many2one('sale.order', 'NO.PI/MO')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
    ], default="draft")
    # mesin_id = fields.Char(string='Mesin')
    mesin_id = fields.Many2one('jenis.mesin',string='Mesin')
    akar_masalah_id = fields.Many2one('akar.masalah', string='akar_masalah')
    quantity_sample_id = fields.Integer(string='Qty Sample', digits='1')
    quantity_def_id = fields.Many2one('uom.uom', default=lambda self: self.env['uom.uom'].search([('name', '=', 'pcs')], limit=1))
    ujike_id = fields.Integer(string='Pengujian Ke-', default="1", readonly="True")

    # laminating = fields.Selection([
    #     ('inhouse', 'Inhouse'),
    #     ('subcont', 'Subcont')
    # ])

    laminating_ids = fields.Many2many('tes.cat.master', string='Laminating')

    # is_inhouse_checked = fields.Boolean(compute='_compute_checkboxes')
    # is_subcont_checked = fields.Boolean(compute='_compute_checkboxes')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('repeat', 'Repeat'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
    ], default="draft")

    # def button_draft(self):
    #     self.write({
    #         'state' : 'repeat',
    #     })

    def button_confirm(self):
        self.write({
            'state' : 'confirm',
        })

    def button_repeat(self):
        old_sequence = self.name
        self.write({
            'state': 'repeat',
        })
        new_doc = self.copy(default={
            'name': _('New'),
            'ujike_id': True,
            'result_pict_ids': [(0, 0, {
                'rincian_kayu': l.rincian_kayu,
                'attachment_img1': l.attachment_img1,
                'attachment_img2': l.attachment_img2,
            }) for l in self.result_pict_ids],     
            'sample_pengujian_line_ids': [(0, 0, {
                'instruksi_sample': line.instruksi_sample,
                'checksatu': line.checksatu,
                'checkdua': line.checkdua,
                'checktiga': line.checktiga,
                'checkempat': line.checkempat,
                'checklima': line.checklima,
                'note' : line.note,
            }) for line in self.sample_pengujian_line_ids],
            'tahapan_pengujian_line_ids': [(0, 0, {
                'instruksi_pengujian': li.instruksi_pengujian,
                'checksatu': li.checksatu,
                'checkdua': li.checkdua,
                'checktiga': li.checktiga,
                'checkempat': li.checkempat,
                'checklima': li.checklima,
                'note': li.note,
            }) for li in self.tahapan_pengujian_line_ids],
            'hasil_pengujian_line_ids': [(0, 0, {
                'instruksi_hasil': lines.instruksi_hasil,
                'checksatu': lines.checksatu,
                'checkdua': lines.checkdua,
                'checktiga': lines.checktiga,
                'checkempat': lines.checkempat,
                'checklima': lines.checklima,
                'note' : lines.note,
            }) for lines in self.hasil_pengujian_line_ids],
        })

        new_doc.write({'state': 'draft'})

        sorted_records = self.search([('name', '=', self.name)], order='ujike_id DESC')
        highest_ujike_id = sorted_records and sorted_records[0].ujike_id or 0
        new_ujike_id = highest_ujike_id + 1
        new_doc.write({'ujike_id': new_ujike_id})

        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'tes.rebus',
            'res_id': new_doc.id,
            'view_mode': 'form',
            'target': 'current',
        }

        return action
    
    # @api.depends('laminating')
    # def _compute_checkboxes(self):
    #     for record in self:
    #         if record.laminating == 'inhouse':
    #             record.is_inhouse_checked = True
    #             record.is_subcont_checked = False
    #         elif record.laminating == 'subcont':
    #             record.is_inhouse_checked = False
    #             record.is_subcont_checked = True
    #         else:
    #             record.is_inhouse_checked = False
    #             record.is_subcont_checked = False

    
    # jenis_pengujian = fields.Selection([
    #     ('material', 'Material'),
    #     ('komponen', 'Komponen'),
    # ])

    jenis_pengujian_ids = fields.Many2many('jenis.pengujian', string='Jenis Pengujian')

    # is_material_checked = fields.Boolean(compute='_compute_checkboxes2')
    # is_komponen_checked = fields.Boolean(compute='_compute_checkboxes2')

    # @api.depends('jenis_pengujian')
    # def _compute_checkboxes2(self):
    #     for record in self:
    #         if record.jenis_pengujian == 'material':
    #             record.is_material_checked = True
    #             record.is_komponen_checked = False
    #         elif record.jenis_pengujian == 'komponen':
    #             record.is_material_checked = False
    #             record.is_komponen_checked = True
    #         else:
    #             record.is_material_checked = False
    #             record.is_komponen_checked = False
    
    internal_notes = fields.Text (string='Catatan')
    notes_attachment = fields.Binary (string='Gambar')

    hasil_uji = fields.Selection([
        ('berhasil', 'Sesuai'),
        ('gagal', 'Tidak Sesuai'),
    ])

    is_berhasil_checked = fields.Boolean(compute='_compute_checkboxes3')
    is_gagal_checked = fields.Boolean(compute='_compute_checkboxes3')

    @api.depends('hasil_uji')
    def _compute_checkboxes3(self):
        for record in self:
            if record.hasil_uji == 'berhasil':
                record.is_berhasil_checked = True
                record.is_gagal_checked = False
            elif record.hasil_uji == 'gagal':
                record.is_berhasil_checked = False
                record.is_gagal_checked = True
            else:
                record.is_berhasil_checked = False
                record.is_gagal_checked = False
    

    dibuat= fields.Char(string='Prepared by')
    penguji = fields.Char(string='Tested by')
    diketahui = fields.Char('Agreed by')
    ttd_dibuat = fields.Binary('Signature')
    ttd_penguji =  fields.Binary('Signature')
    ttd_diketahui = fields.Binary('Signature')

    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq = self.env['ir.sequence'].next_by_code('tes.rebus.seq.tes') or _('New')
        vals['name'] = seq
        res = super(TesRebus, self).create(vals)
        return res

  
    def button_confirm(self):
        self.write({
            'state' : 'confirm',
        })


    def button_cancel(self):
        self.write({
            'state' : 'draft'
        })

    result_pict_ids = fields.One2many('tes.rebus.line', 'pict_result_id')
    sample_pengujian_line_ids = fields.One2many('tes.rebus.line', 'sample_method_id', string='Sample Line')
    tahapan_pengujian_line_ids = fields.One2many('tes.rebus.line', 'tahap_method_id', string='Tahapan Line')
    hasil_pengujian_line_ids = fields.One2many('tes.rebus.line', 'hasil_method_id', string='Hasil Line')



class TesRebusline(models.Model):
    _name = "tes.rebus.line"
    _description = "Tes Rebus Sample"

    pict_result_id = fields.Many2one('tes.rebus',string='Metode Gambar')
    sample_method_id = fields.Many2one('tes.rebus',string='Metode Pengujian')
    tahap_method_id = fields.Many2one('tes.rebus',string='Metode Pengujian')
    hasil_method_id = fields.Many2one('tes.rebus',string='Metode Pengujian')
    name = fields.Char('Instruksi Kegiatan')  
    note = fields.Char(string='Catatan')
    
    rincian_kayu = fields.Text(string='Rincian Kayu')
    attachment_img1 = fields.Binary('Gambar 1')
    attachment_img2 = fields.Binary('Gambar 2')
    instruksi_sample = fields.Text(string='Rincian Sample')
    
    checksatu = fields.Selection([('v', 'V'), ('x','X')], string='1')
    checkdua = fields.Selection([('v', 'V'), ('x','X')], string='2')
    checktiga = fields.Selection([('v', 'V'), ('x','X')], string='3')
    checkempat = fields.Selection([('v', 'V'), ('x','X')], string='4')
    checklima = fields.Selection([('v', 'V'), ('x','X')], string='5')
    
    instruksi_pengujian = fields.Text(string='Rincian Pengujian')

    instruksi_hasil = fields.Text(string='Rincian Hasil')
