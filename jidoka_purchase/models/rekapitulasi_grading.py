# -*- coding: utf-8 -*-

from odoo import models, fields, api

class RekapitulasiGrading(models.Model):
    _name = 'rekapitulasi.grading'
    _description = 'Rekapitulasi Grading'

    name = fields.Char('Name',default='New')
    partner_id = fields.Many2one('res.partner', string='Vendor')
    # arrival_date = fields.Date('Arrival Date')
    # plat_no = fields.Char('Plat No')
    # nota = fields.Char('FA - KO / NOTA ANGKUTAN')
    purchase_id = fields.Many2one('purchase.order', string='Purchase')
    notes = fields.Text('Note')
    master_hasil_id = fields.Many2one('res.master.hasil', string='Master Hasil')
    line_ids = fields.One2many('rekapitulasi.grading.line', 'rekapitulasi_grading_id', string='line')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    master_hasil = fields.Selection([
        ('bagus', 'Bagus'),
        ('afkir', 'Afkir'),
        ('triming', 'Triming'),
        ('grade_a', 'Grade A'),
        ('grade_b', 'Grade B')
    ], string='Master Hasil')
    picking_id = fields.Many2one('stock.picking', string='Picking')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('seq.rekapitulasi.grading.ckwi') or '/'
        return super().create(vals)

class RekapitulasiGradingLine(models.Model):
    _name = 'rekapitulasi.grading.line'
    _description = 'Rekapitulasi Grading Line'

    rekapitulasi_grading_id = fields.Many2one('rekapitulasi.grading', string='Rekapitulasi Grading')
    product_id = fields.Many2one('product.product', string='Product')
    good_pcs = fields.Float('Bagus Pcs', digits='Product Unit of Measure', default=0.0)
    good_cubic = fields.Float('Bagus M3', digits='Product Unit of Measure', default=0.0)
    afkir_pcs = fields.Float('Afkir Pcs', digits='Product Unit of Measure', default=0.0)
    afkir_cubic = fields.Float('Afkir M3', digits='Product Unit of Measure', default=0.0)
    triming_pcs = fields.Float('Triming Pcs', digits='Product Unit of Measure', default=0.0)
    triming_cubic = fields.Float('Triming M3', digits='Product Unit of Measure', default=0.0)
    grade_a_pcs = fields.Float('Grade A Pcs', digits='Product Unit of Measure', default=0.0)
    grade_a_cubic = fields.Float('Grade A M3', digits='Product Unit of Measure', default=0.0)
    grade_b_pcs = fields.Float('Grade B Pcs', digits='Product Unit of Measure', default=0.0)
    grade_b_cubic = fields.Float('Grade B M3', digits='Product Unit of Measure', default=0.0)
    total_pcs = fields.Float('Total Pcs', compute='_compute_total_pcs', digits='Product Unit of Measure')
    total_cubic = fields.Float('Total M3', compute='_compute_total_cubic', digits='Product Unit of Measure')
    company_id = fields.Many2one(related='rekapitulasi_grading_id.company_id', string='Company', index=True)
   
    @api.depends('good_pcs','afkir_pcs','triming_pcs','grade_a_pcs','grade_b_pcs')
    def _compute_total_pcs(self):
        for rec in self:
            rec.total_pcs = rec.good_pcs + rec.afkir_pcs + rec.triming_pcs + rec.grade_a_pcs + rec.grade_b_pcs

    @api.depends('good_cubic','afkir_cubic','triming_cubic','grade_a_cubic','grade_b_cubic')
    def _compute_total_cubic(self):
        for rec in self:
            rec.total_cubic = rec.good_cubic + rec.afkir_cubic + rec.triming_cubic + rec.grade_a_cubic + rec.grade_b_cubic