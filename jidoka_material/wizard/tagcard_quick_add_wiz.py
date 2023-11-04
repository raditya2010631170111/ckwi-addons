from odoo import models, fields, api, _
from odoo.exceptions import UserError



class TagcardQuickAddWizard(models.TransientModel):
    _name = 'tagcard.quick.add.wizard'
    _description = 'Tagcard Quick Add Wizard'

    tag_card_id = fields.Many2one(comodel_name='jidoka.tagcard', string='Tag Card')
    s_tebal = fields.Float(string='Tebal')
    s_lebar = fields.Float(string='Lebar')
    s_panjang = fields.Float(string='Panjang')
    s_lot_qty = fields.Integer(string='Jumlah Lot', default=1, required=True)
    selected_count = fields.Integer(string='Counted')
    tagcard_type = fields.Selection(string='TagCard Type', related="tag_card_id.tagcard_type")
    quant_ids = fields.Many2many(comodel_name='stock.quant', string='Selected Stock Quants',
        compute='_compute_quant_ids')
    tag_card_state = fields.Selection(string='Tag Card State', related="tag_card_id.state")
    
    
    @api.depends('tag_card_id.quant_ids', 'tag_card_id.is_selected')
    def _compute_quant_ids(self):
        for record in self:
            record.quant_ids = [(6, 0, record.tag_card_id.quant_ids.filtered(lambda q: q.is_selected).ids)]

    def action_confirm(self):
        tag_card = self.tag_card_id
        if not tag_card.quant_ids:
            raise UserError("Data List Material kosong, klik Search terlebih dahulu.")
        filtered_quants = tag_card.quant_ids.filtered(lambda quant: not quant.is_selected and quant.tebal == self.s_tebal and quant.panjang == self.s_panjang and quant.lebar == self.s_lebar)
        if not filtered_quants:
            raise UserError("Data Stock tidak ditemukan dengan dimensi yang sesuai.")
        if len(filtered_quants) < self.s_lot_qty:
            raise UserError("Data Stock hanya ada %s ." % len(filtered_quants))
        for n in range(self.s_lot_qty):
            filtered_quants[n].is_selected = True
        tag_card._count_materials_by_quants()
        tag_card.s_tebal = self.s_tebal
        tag_card.s_panjang = self.s_panjang
        tag_card.s_lebar = self.s_lebar
        tag_card.s_lot_qty = self.s_lot_qty
        return {
            'name': 'Quick Search & Add Material Tag Card',
            'view_mode': 'form',
            'view_id': False,
            'res_model': self._name,
            'domain': [],
            'context': dict(self._context, active_ids=self.ids),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }