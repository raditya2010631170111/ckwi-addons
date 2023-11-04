from odoo import _,models,fields,api

class LembarPengesahanBahan(models.Model):
    _name = 'lembar.pengesahan.bahan'
    _description = "Lembar Pengesahan Bahan"

    name = fields.Char(required=True)
    categ_id = fields.Many2one('product.category', string='Category')

    componen_ids = fields.One2many('komponen.lembar.pengesahan', 'lembar_id', string='componen', copy=True)
    # point_pemeriksaan_ids = fields.One2many('point.pemeriksaan', 'lembar_id', string='Poin Pemeriksaan')
    # point_pemeriksaan_line_ids = fields.One2many('point.pemeriksaan.line', 'lembar_id', string='point_pemeriksaan_line')
    # point_pemeriksaan_id = fields.Many2one('point.pemeriksaan', string='field_name')

class KomponenLembarPengesahanBahan(models.Model):
    _name = 'komponen.lembar.pengesahan'
    _description = "Komponen Lembar Pengesahan"

    lembar_id = fields.Many2one('lembar.pengesahan.bahan', string='Lembar')
    sequence = fields.Integer(string='Sequence', default=10)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    name = fields.Char()


# class PointPemeriksaan(models.Model):
#     _name = 'point.pemeriksaan'
#     _description = "Point Pemeriksaan"

#     name = fields.Char('Name')
#     lembar_id = fields.Many2one('lembar.pengesahan.bahan', string='lembar')
#     point_pemeriksaan_line_ids = fields.One2many('point.pemeriksaan.line', 'point_pemeriksaan_id', string='point_pemeriksaan_line')
#     sequence = fields.Integer('Sequence', default=0)

#     @api.model
#     def create(self, vals):
#         # Hitung jumlah record yang sudah ada dalam database
#         record_count = self.env['point.pemeriksaan'].search_count([])
        
#         # Tambahkan satu untuk nilai sequence pada record baru yang sedang dibuat
#         vals['sequence'] = record_count + 1
        
#         # Panggil fungsi create dari superclass untuk membuat record
#         return super(PointPemeriksaan, self).create(vals)


#     def action_show_details(self):
#         self.ensure_one()
#         view = self.env.ref('qa_qc.lembar_pengesahan_line_detail')
#         return {
#             'name': _('Sample Details'),
#             'type': 'ir.actions.act_window',
#             'view_mode': 'form',
#             'res_model': 'point.pemeriksaan',
#             'views': [(view.id, 'form')],
#             'view_id': view.id,
#             'target': 'new',
#             'res_id': self.id,
#             'context': dict(
#                 self.env.context
#             ),
#         }

# class PointPemeriksaanLine(models.Model):
#     _name = 'point.pemeriksaan.line'
#     _description = "Point Pemeriksaan Line"

#     point_pemeriksaan_id = fields.Many2one('point.pemeriksaan', string='point_pemeriksaan')
#     name = fields.Char('Name')
#     status = fields.Selection([
#         ('sesuai', 'Sesuai'),
#         ('tdk_sesuai', 'Tidak Sesuai'),
#         ('na', 'N/A')
#     ], string='Status')
#     keterangan = fields.Char('Keterangan')
#     lembar_id = fields.Many2one('lembar.pengesahan.bahan', string='lembar',related='point_pemeriksaan_id.lembar_id',store=True)
#     name_pemeriksaan = fields.Char('Name Pemeriksaan', related='point_pemeriksaan_id.name')
#     sequence = fields.Integer('sequence', related='point_pemeriksaan_id.sequence')



