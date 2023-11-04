from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    grading_done = fields.Boolean('Grading Done', default=False, related='picking_id.grading_done')
    wood_kind_id = fields.Many2one(comodel_name='jidoka.woodkind', string='Jenis Kayu')
    is_kayu = fields.Boolean('Is Kayu', related='picking_id.is_kayu', readonly=True, store=True)
    is_qc_id = fields.Boolean('Is QC', related='picking_id.is_qc_id', readonly=True, store=True)
    

    @api.depends('has_tracking', 'picking_type_id.use_create_lots', 'picking_type_id.use_existing_lots', 'state')
    def _compute_display_assign_serial(self):
        for move in self:
            move.display_assign_serial = (
                # NOTE has_tracking diubah ke lot & serial, sebelumnya hanya serial
                move.has_tracking in ('lot','serial') and
                move.state in ('partially_available', 'assigned', 'confirmed') and
                move.picking_type_id.use_create_lots and
                not move.picking_type_id.use_existing_lots
                and not move.origin_returned_move_id.id
            )

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    lot_name_old = fields.Char(string='Lot Name Old', store=True)

    @api.onchange('size_log_id')
    def _onchange_size_log_id(self):
        for rec in self:
            if rec.lot_name_old == False:
                rec.lot_name_old = rec.lot_name

            if rec.lot_name_old:
                rec.lot_name = rec.lot_name_old + '-' + str(rec.size_log_id.name)