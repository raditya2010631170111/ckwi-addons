# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockAssignTagCard(models.TransientModel):
    _name = 'stock.assign.tag.card'
    _description = 'Stock Assign Tag Cards'

    # def _default_next_serial_count(self):
    #     move = self.env['stock.move'].browse(self.env.context.get('default_move_id'))
    #     if move.exists():
    #         filtered_move_lines = move.move_line_ids.filtered(lambda l: not l.lot_name and not l.lot_id)
    #         return len(filtered_move_lines)

    product_id = fields.Many2one('product.product', 'Product',
        related='move_id.product_id', required=True)
    move_id = fields.Many2one('stock.move', required=True)
    next_serial_number = fields.Char('First SN', required=True)
    packaging_id = fields.Many2one(
        'product.packaging', 'Package Type', index=True, check_company=True)
    next_serial_count = fields.Integer('Number of SN',compute='_compute_next_serial_count', required=True)
    line_ids = fields.One2many('stock.assign.tag.card.line', 'tag_card_id', string='line')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True)    
    
    @api.depends('line_ids')
    def _compute_next_serial_count(self):
        for rec in self:
            rec.next_serial_count = len(rec.line_ids)
    
    @api.constrains('next_serial_count')
    def _check_next_serial_count(self):
        for wizard in self:
            if wizard.next_serial_count < 1:
                raise ValidationError(_("The number of Serial Numbers to generate must greater than zero."))

    def generate_tag_card(self):
        self.ensure_one()
        self.move_id.next_serial = self.next_serial_number or ""
        lines = []
        result_package_id = False
        if self.packaging_id:
            result_package_id = self.env['stock.quant.package'].create({'packaging_id':self.packaging_id.id})
        for line in self.line_ids:
            vals = {
                'panjang':line.panjang,
                'lebar':line.lebar,
                'tinggi':line.tinggi,
                'qty_received':line.qty_received,
                'master_hasil':line.master_hasil
            }
            if result_package_id:
                vals['result_package_id'] = result_package_id.id
            lines.append(vals)
        return self.move_id._generate_serial_numbers(next_serial_count=self.next_serial_count,lines=lines)


class StockAssignTagCardLine(models.TransientModel):
    _name = 'stock.assign.tag.card.line'
    _description = 'Stock Assign Tag Cards Line'

    tag_card_id = fields.Many2one('stock.assign.tag.card', string='Tag Card')
    panjang = fields.Float('Panjang')
    lebar = fields.Float('Lebar')
    tinggi = fields.Float('Tinggi')
    qty_received = fields.Float('Pcs')
    master_hasil = fields.Selection([
        ('bagus', 'Bagus'),
        ('afkir', 'Afkir'),
        ('triming', 'Triming'),
        ('grade_a', 'Grade A'),
        ('grade_b', 'Grade B')
    ], string='Grading')