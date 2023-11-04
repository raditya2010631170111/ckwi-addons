from email.policy import default
from odoo import _,fields,api,models

class TesCatMaster(models.Model):

    _name = 'tes.cat.master'
    _description = ''
    
    name = fields.Char(required=True)


class JenisPengujian(models.Model):

    _name = 'jenis.pengujian'
    _description = ''
    
    name = fields.Char(required=True)

class TahapanFinishingMaster(models.Model):

    _name = 'tahapan.finishing.master'
    _description = ''
    
    name = fields.Char(required=True)

class BarangJadi(models.Model):

    _name = 'barang.jadi'
    _description = ''
    
    name = fields.Char(required=True)

class SumberAcuan(models.Model):

    _name = 'sumber.acuan'
    _description = ''
    
    name = fields.Char(required=True)

class JenisMesin(models.Model):

    _name = 'jenis.mesin'
    _description = ''
    
    name = fields.Char(required=True)

class CekPoint(models.Model):

    _name = 'cek.point'
    _description = ''
    
    name = fields.Char('Name', required=True)
    cek_point_line_ids = fields.One2many('cek.point.line', 'cek_point_id', string='cek_ponit_line', copy=True)
    point_pemeriksaan_ids = fields.One2many('point.pemeriksaan.line', 'cek_point_id', string='point_pemeriksaan')

    

class CekPointLine(models.Model):

    _name = 'cek.point.line'
    _description = ''
    
    name = fields.Char('Name', required=True)
    sequence = fields.Integer('sequence')
    cek_point_id = fields.Many2one('cek.point', string='Cek Point')
    point_pemeriksaan_ids = fields.One2many('point.pemeriksaan.line', 'cek_point_line_id', string='point_pemeriksaan', copy=True)
    max_line = fields.Integer('max_line', compute="_compute_max_line")

    @api.depends('point_pemeriksaan_ids')
    def _compute_max_line(self):
        for record in self:
            record.max_line = len(record.point_pemeriksaan_ids)
    @api.model
    def create(self, vals):
        record_count = self.env['cek.point.line'].search_count([])
        vals['sequence'] = record_count + 1
        return super(CekPointLine, self).create(vals)


    def action_show_details(self):
        self.ensure_one()
        view = self.env.ref('qa_qc.point_pemeriksaan_detail')
        return {
            'name': _('Cek Point Details'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cek.point.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context
            ),
        }

class PointPemeriksaanLine(models.Model):
    _name = 'point.pemeriksaan.line'
    _description = "Point Pemeriksaan Line"

    cek_point_line_id = fields.Many2one('cek.point.line', string='point_pemeriksaan')
    name = fields.Char('Name')
    cek_point_id = fields.Many2one('cek.point', string='cek point',related='cek_point_line_id.cek_point_id',store=True)
    max_line = fields.Integer('max_line', related='cek_point_line_id.max_line')
    name_pemeriksaan = fields.Char('Name Pemeriksaan', related='cek_point_line_id.name')
    sequence = fields.Integer('sequence', related='cek_point_line_id.sequence')
   







