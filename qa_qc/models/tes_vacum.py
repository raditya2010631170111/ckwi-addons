from odoo import _, api, fields, models
from datetime import date, datetime

class TesVacum(models.Model):
    _name = 'tes.vacum'
    
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
            return f"{str(new_no).zfill(2)}/ITL/QA/{str(month).zfill(2)}/{year}"
        else:
            year = str(fields.Date.today().year)[-2:] 
            month = fields.Date.today().month
            requests = self.search([], order='id asc')
            if requests:
                return requests[0].name
            else:
                return f"01/ITL/QA/{str(month).zfill(2)}/{year}"
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('repeat', 'Repeat'),
    ], default="draft")
          
    def button_confirm(self):
        self.write({
            'state' : 'confirm',
        })
        
    date = fields.Date(string='Tanggal', default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Supplier')
    buyer_id = fields.Many2one('res.partner', string='Buyer')
    product_id= fields.Many2one('product.product', string='No.Item')
    quantity_sample_id = fields.Integer(string='Qty Sample', digits='1')
    quantity_def_id = fields.Many2one('uom.uom', default=lambda self: self.env['uom.uom'].search([('name', '=', 'pcs')], limit=1))
    no_mo_id = fields.Many2one('sale.order', string='No. PI/MO')
    woodkind_id = fields.Many2one('jidoka.woodkind', string='Material')
    line_ids = fields.One2many('tes.kontruksi.line', 'konstruksi_id', string='line')
    design_image = fields.One2many('tes.kontruksi.line', 'spec_id', string='line')
    barang_baku_ids = fields.Many2many('tes.cat.master',string='Barang Baku')
    jenis_pengujian_ids = fields.Many2many('jenis.pengujian', string='Jenis Pengujian')
    pengujian = fields.Integer('Pengujian Ke', default=1, readonly=True)
    tes_vacum_line_ids = fields.One2many('tes.vacum.line', 'tes_vacum_id', string='Tes Kekuatan Cat Line')
    catatan_vacum_line_ids = fields.One2many('catatan.vacum.line', 'tes_vacum_id', string='Catatan Photo Line')
    pemeriksaan = fields.Selection([
        ('sesuai', 'SESUAI'),
        ('tidak_sesuai', 'TIDAK SESUAI')
    ], string='Hasil', default='')
    pemeriksaan_selection = fields.Char('pemeriksaan_selection', compute="_compute_pemeriksaan_selection")
    hasil_pemeriksaan = fields.Char('hasil', compute='_compute_hasil')

    @api.depends('pemeriksaan')
    def _compute_pemeriksaan_selection(self):
        for record in self:
            if record.pemeriksaan == 'sesuai':
                record.pemeriksaan_selection = 'SESUAI'
            elif record.pemeriksaan == 'tidak_sesuai':
                record.pemeriksaan_selection = 'TIDAK SESUAI'
            else:
                record.pemeriksaan_selection = ''
    
    @api.depends('pemeriksaan')
    def _compute_hasil(self):
        for record in self:
            if record.pemeriksaan == 'sesuai':
                record.hasil_pemeriksaan = 'Hasil akhir pemeriksaan / pengujian / perhitungan, telah sesuai atau lebih dari nilai yang telah ditetapkan.'
            elif record.pemeriksaan == 'tidak_sesuai':
                record.hasil_pemeriksaan = 'Hasil akhir pemeriksaan / pengujian / perhitungan, kurang dari nilai yang telah ditetapkan.'
            else:
                record.hasil_pemeriksaan = ''
    petugas = fields.Char('Petugas Pengujian')
    diketahui = fields.Char('Diketahui')
    dibuat= fields.Char(string='Dibuat')
    ttd_petugas = fields.Binary('TTD')
    ttd_diketahui = fields.Binary('TTD')
    ttd_dibuat = fields.Binary('TTD')
    
    def button_cancel(self):
        old_sequence = self.name
        new_doc = self.copy(default={
            'name': self._generate_request_no(),
            'pengujian': True,
            'pemeriksaan': self.pemeriksaan,
            'catatan_vacum_line_ids': [(0, 0, {
                'photo_hasil_test1': l.photo_hasil_test1,
                'photo_hasil_test2': l.photo_hasil_test2,
                'catatan': l.catatan,
            }) for l in self.catatan_vacum_line_ids],
            'tes_vacum_line_ids': [(0, 0, {
                'sample': ol.sample,
                'jumlah_item': ol.jumlah_item,
                'catatan': ol.catatan,
                'sample_vacum_line_ids': [(0, 0, {
                    'tahapan_finisihing_id': line.tahapan_finisihing_id.id,
                    'no_1': line.no_1,
                    'no_2': line.no_2,
                    'no_3': line.no_3,
                    'no_4': line.no_4,
                    'no_5': line.no_5,
                    'no_6': line.no_6,
                }) for line in ol.sample_vacum_line_ids]
            }) for ol in self.tes_vacum_line_ids]
        })
        new_doc.write({'state': 'draft'})
        sorted_records = self.search([('name', '=', self.name)], order='pengujian DESC')
        highest_pengujian = sorted_records and sorted_records[0].pengujian or 0
        new_pengujian = highest_pengujian + 1
        new_doc.write({'pengujian': new_pengujian})
        self.write({
            'state' : 'repeat',
        })
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'tes.vacum',
            'res_id': new_doc.id,
            'view_mode': 'form',
            'target': 'current',
        }
        return action
        
class TesVacumLine(models.Model):
    _name = 'tes.vacum.line'

    sample = fields.Char('Sample')
    jumlah_item = fields.Integer('Jumlah Item')
    tes_vacum_id = fields.Many2one('tes.vacum', string='field_name')
    catatan = fields.Text('Catatan')
    sample_vacum_line_ids = fields.One2many('sample.vacum.line', 'tes_vacum_line_id', string='Sample Detail Line')


    def action_show_details(self):
        self.ensure_one()
        view = self.env.ref('qa_qc.tes_vacum_operations')
        return {
            'name': _('Sample Details'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'tes.vacum.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context
            ),
        }
        
class SampleVacumLine(models.Model):
    _name = 'sample.vacum.line'

    tes_vacum_line_id = fields.Many2one('tes.vacum.line', string='tes_kekuatan_cat_line')
    tahapan_finisihing_id = fields.Many2one('tahapan.finishing.master', string='Tahapan Finishing')
    no_1 = fields.Selection([
    ('V', 'V'),
    ('X', 'X'),
    ('-', '-')])
    no_2 = fields.Selection([
    ('V', 'V'),
    ('X', 'X'),
    ('-', '-')])
    no_3 = fields.Selection([
    ('V', 'V'),
    ('X', 'X'),
    ('-', '-')])
    no_4 = fields.Selection([
    ('V', 'V'),
    ('X', 'X'),
    ('-', '-')])
    no_5 = fields.Selection([
    ('V', 'V'),
    ('X', 'X'),
    ('-', '-')])
    no_6 = fields.Selection([
    ('V', 'V'),
    ('X', 'X'),
    ('-', '-')])


class CatatanVacum(models.Model):
    _name = 'catatan.vacum.line'

    photo_hasil_test1 = fields.Binary('Photo')
    photo_hasil_test2 = fields.Binary('Photo')
    catatan = fields.Text(string='Catatan', strip_style=True)
    tes_vacum_id = fields.Many2one('tes.vacum', string='field_name')