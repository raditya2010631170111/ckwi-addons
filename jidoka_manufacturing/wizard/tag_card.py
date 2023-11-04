# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TagCardWizard(models.TransientModel):
    _name = 'tag.card.wizard'
    _description = 'Tag Card Wizard'

    def _default_items_ids(self):
        return self.env['mrp.workorder'].browse(self._context.get('active_ids'))

    name = fields.Char('No Tag')
    prod_intruction_id = fields.Many2one('mrp.production', string='Prod Intruction')
    bahan = fields.Selection([
        ('baku', 'Baku'),
        ('setengah_jadi', 'Setengah Jadi'),
        ('kd', 'K/D'),
        ('sertifikat', 'Bersertifikat'),
        ('moulding', 'Moulding'),
        ('ad', 'A/D'),
        ('tidak', 'Tidak'),
    ], string='Bahan', default='baku')
    fisik = fields.Selection([
        ('standard', 'Standard'),
        ('tipis', 'Tipis'),
        ('mata', 'Mata'),
    ], string='Fisik', default='standard')
    kode_beli = fields.Char('Kode Beli')
    kualitas = fields.Char('Kualitas')
    stage = fields.Char('Proses')
    marking = fields.Char('Marking')
    tgl_masuk = fields.Date('Tgl Masuk', required=True)
    jenis_kayu = fields.Selection([
        ('jati', 'Jati'),
        ('non_jati', 'Non Jati'),
    ], string='jenis_kayu', default='jati')
    supplier_id = fields.Many2one('res.partner', string='Supplier')
    total_pcs = fields.Float('Total Pcs')
    total_m3 = fields.Float('Total M3')
    location_id = fields.Many2one('stock.location', string='Location', required=True)
    it = fields.Char('IT')
    items_ids = fields.Many2many('mrp.workorder', string='Items', default=_default_items_ids)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        state = self.env["mrp.workorder"].browse(self._context.get('active_ids'))

        for line in state:
            res['stage'] = line.state
            if line.state != 'done':
                raise ValidationError(_("Workorder %s statusnya belum Done") % line.name)
        return res

    def create_tag_card(self):
        ref = self.env['ir.sequence'].next_by_code('tag.card')
        tag_card = self.env['tag.card']
        tag_card_line = self.env['tag.card.line']
        line_ids = []

        for values in self.items_ids:
            exis = tag_card_line.search([('production_id', '=', values.production_id.id)])
            if exis:
                raise ValidationError(_('Nomor Manufacture Order %s ini sudah dibuatkan Tag Card') % exis.production_id.name)
            else:
                line_ids.append((0, 0, {
                    'tag_card_id': tag_card.id,
                    'name': values.production_id.product_id.name,
                    'ukuran': 12345,
                    'quantity': values.production_id.product_qty,
                    'uom_id': values.production_id.product_uom_id.id,
                    'note': values.state,
                    'volume': values.production_id.product_id.volume,
                    'production_id': values.production_id.id
                }))

        # total_pcs = 0
        # for s in line_ids:
        #     for i in s:
        #         if i != 0:
        #             print('===================', i)

        tag_card.create({
            'id': self.id,
            'name': ref,
            'bahan': self.bahan,
            'fisik': self.fisik,
            'kode_beli': self.kode_beli,
            'kualitas': self.kualitas,
            'stage': self.stage,
            # 'total_pcs': total_pcs,
            'marking': self.marking,
            'tgl_masuk': self.tgl_masuk,
            'supplier_id': self.supplier_id.id,
            'location_id': self.location_id.id,
            'card_line_ids': line_ids
        })