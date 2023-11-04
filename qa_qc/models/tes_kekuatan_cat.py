from odoo import _, api, fields, models
from datetime import date, datetime



class TesKekuatanCat(models.Model):
    _name = 'tes.kekuatan.cat'
    _order = 'name'
    

    name = fields.Char('Name', default=lambda self: _('New'), copy=False, readonly=True)
    partner_id = fields.Many2one('res.partner', string='Supplier')
    user_id = fields.Many2one('res.partner', string='Buyer')
    woodkind_id = fields.Many2one('jidoka.woodkind', string='Material', related='product_id.wood_kind_id')
    date = fields.Date('Date', required=True)
    colour_id = fields.Many2one('res.fabric.colour', string='Colour')
    product_id= fields.Many2one('product.product', string='Item')
    no_mo_id = fields.Many2one('sale.order', 'NO.PI/MO')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('repeat', 'Repeat'),
    ], default="draft")
    tes_cat_master_ids = fields.Many2many('tes.cat.master', string='Test Cat/Finishing')
    jenis_pengujian_ids = fields.Many2many('jenis.pengujian', string='Jenis Pengujian')
    pengujian_ke = fields.Integer('Pengujian Ke', default=1, readonly=True)
    tes_kekutan_line_ids = fields.One2many('tes.kekuatan.cat.line', 'tes_kekuatan_cat_id', string='Tes Kekuatan Cat Line')
    catatan_photo_line_ids = fields.One2many('catatan.photo.line', 'tes_kekuatan_cat_id', string='Catatan Photo Line')
    pemeriksaan = fields.Selection([
        ('sesuai', 'SESUAI'),
        ('tidak_sesuai', 'TIDAK SESUAI')
    ], string='Hasil', default='')
    pemeriksaan_selection = fields.Char('pemeriksaan_selection', compute="_compute_pemeriksaan_selection")
    # hasil_pemeriksaan = fields.Selection([
    #     ('hasil_sesuai', 'Hasil akhir pemeriksaan / pengujian / perhitungan, telah sesuai atau lebih dari nilai yang telah ditetapkan.'),
    #     ('hasil_tdk_sesuai','Hasil akhir pemeriksaan / pengujian / perhitungan, kurang dari nilai yang telah ditetapkan.')
    # ], string='hasil_pemeriksaan', compute='_compute_hasil_pemeriksaan', default='')
    petugas = fields.Char('Petugas')
    diketahui = fields.Char('Diketahui')
    dibuat= fields.Char(string='Dibuat')
    ttd_petugas = fields.Binary('TTD')
    ttd_diketahui = fields.Binary('TTD')
    ttd_dibuat = fields.Binary('TTD')
    hasil_pemeriksaan = fields.Char('hasil', compute='_compute_hasil')
    def _default_base_url(self):
        return self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    base_url = fields.Char(string='Base Url', default=_default_base_url)
    

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
    # @api.depends('pemeriksaan')
    # def _compute_hasil_pemeriksaan(self):
    #     for record in self:
    #         if record.pemeriksaan == 'sesuai':
    #             record.hasil_pemeriksaan = 'hasil_sesuai'
    #         else:
    #             record.hasil_pemeriksaan = 'hasil_tdk_sesuai'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq = self.env['ir.sequence'].next_by_code('tes.kakuatan.cek.seq') or _('New')
        vals['name'] = seq
        res = super(TesKekuatanCat, self).create(vals)
        return res
    

    # def button_draft(self):
    #     self.write({
    #         'state' : 'repeat',
    #     })

    def button_confirm(self):
        self.write({
            'state' : 'confirm',
        })

    def button_repeat(self):
        self.write({
            'state': 'repeat',
        })
        old_sequence = self.name
        new_doc = self.copy(default={
            'name': _('New'),
            'pengujian_ke': True,
            'pemeriksaan': self.pemeriksaan,
            'catatan_photo_line_ids': [(0, 0, {
                'tahap_tes': l.tahap_tes,
                'photo_hasil_test1': l.photo_hasil_test1,
                'photo_hasil_test2': l.photo_hasil_test2,
                'catatan': l.catatan,
            }) for l in self.catatan_photo_line_ids],
            'tes_kekutan_line_ids': [(0, 0, {
                'sample': ol.sample,
                'jumlah_item': ol.jumlah_item,
                'catatan': ol.catatan,
                'sample_detail_line_ids': [(0, 0, {
                    'tahapan_finisihing_id': line.tahapan_finisihing_id.id,
                    'no_1': line.no_1,
                    'no_2': line.no_2,
                    'no_3': line.no_3,
                    'no_4': line.no_4,
                    'no_5': line.no_5,
                }) for line in ol.sample_detail_line_ids]
            }) for ol in self.tes_kekutan_line_ids]
        })

        new_doc.write({'state': 'draft'})

        sorted_records = self.search([('name', '=', self.name)], order='pengujian_ke DESC')
        highest_pengujian_ke = sorted_records and sorted_records[0].pengujian_ke or 0
        new_pengujian_ke = highest_pengujian_ke + 1
        new_doc.write({'pengujian_ke': new_pengujian_ke})

        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'tes.kekuatan.cat',
            'res_id': new_doc.id,
            'view_mode': 'form',
            'target': 'current',
        }

        return action


class TesKekuatanCatLine(models.Model):
    _name = 'tes.kekuatan.cat.line'

    sample = fields.Char('Sample')
    jumlah_item = fields.Integer('Jumlah Item')
    tes_kekuatan_cat_id = fields.Many2one('tes.kekuatan.cat', string='field_name')
    catatan = fields.Text('Catatan')
    sample_detail_line_ids = fields.One2many('sample.detail.line', 'tes_kekuatan_cat_line_id', string='Sample Detail Line')


    def action_show_details(self):
        self.ensure_one()
        view = self.env.ref('qa_qc.tes_kekuatan_cat_operations')
        return {
            'name': _('Sample Details'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'tes.kekuatan.cat.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context
            ),
        }


class SampleDetailLine(models.Model):
    _name = 'sample.detail.line'

    tes_kekuatan_cat_line_id = fields.Many2one('tes.kekuatan.cat.line', string='tes_kekuatan_cat_line')
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


class CatatanPhoto(models.Model):
    _name = 'catatan.photo.line'

    tahap_tes = fields.Text('Tahap Test')
    photo_hasil_test1 = fields.Binary('Photo')
    photo_hasil_test2 = fields.Binary('Photo')
    catatan = fields.Text('Catatan')
    tes_kekuatan_cat_id = fields.Many2one('tes.kekuatan.cat', string='field_name')








