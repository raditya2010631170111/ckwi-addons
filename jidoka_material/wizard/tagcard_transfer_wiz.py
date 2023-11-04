from odoo import models, fields, api, _
from odoo.exceptions import UserError

# Define your class
class TagcardTransferWizard(models.TransientModel):
    _name = 'tagcard.transfer.wizard'
    _description = 'Tag Card transfer wizard'

    quant_package_ids = fields.Many2many(comodel_name='stock.quant.package', string='Tag Cards')
    source_location_id = fields.Many2one(comodel_name='stock.location', string='Source Location',
        required=True)
    destination_location_id = fields.Many2one(comodel_name='stock.location',
        string='Destination Location', required=True)
    transfer_date = fields.Date(string='Scheduled Date', default=fields.Date.today)
    
    transaction_date = fields.Datetime('Transaction Date', related='quant_package_ids.transaction_date', readonly=False)
    
    
    @api.model
    def default_get(self, fields):
        res = super(TagcardTransferWizard, self).default_get(fields)
        res_ids = self._context.get('active_ids')

        sqps = self.env['stock.quant.package'].browse(res_ids)
        if not sqps:
            raise UserError(_("Nothing to transfer."))
        for p in sqps:
            if not p.quant_ids or not p.location_id:
                raise UserError(_("Package %s not valid") % p.name)
        single_sqp = sqps[0]
        for p in sqps:
            if p.location_id.id != single_sqp.location_id.id:
                raise UserError(_("Location of package %s is not valid") % p.name)
        res.update({
            'quant_package_ids': res_ids,
            'source_location_id': single_sqp.location_id.id,
        })
        return res


    def action_confirm_transfer(self):
        self.ensure_one()
        if not self.quant_package_ids:
            raise UserError(_("Required package to transfer"))
        if not self.source_location_id or not self.destination_location_id:
            raise UserError(_("Required location to transfer"))
        if self.source_location_id == self.destination_location_id:
            raise UserError(_("Nothing to transfer, same location"))
        # move_ids = self._prepare_moves()
        line_ids = self._prepare_move_lines()
        # Create a new stock picking of type 'internal
        origin = ','.join(self.quant_package_ids.mapped('name'))
        picking = self.env['stock.picking'].create({
            'partner_id': self.env.company.partner_id.id,
            'origin': origin,
            'scheduled_date': self.transfer_date,
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
            'location_id': self.source_location_id.id,
            'location_dest_id': self.destination_location_id.id,
            'transaction_date': self.transaction_date,
            # 'move_ids_without_package': move_ids, # tanpa stock move (auto)
            'move_line_ids_without_package': line_ids,
            'is_tagcard': True,
            'grading_done': True,
            # 'nota': '-',
            # 'show_validate': True,
            # 'is_qc': True,
        })
        # Confirm the stock picking
        picking.action_confirm()
        picking.button_validate()
    
    def _prepare_moves(self):
        line_ids = []
        # TODO : per product
        # products = 
        # if self.quant_package_id and self.quant_package_id.quant_ids:
        #     quants = self.quant_package_id.quant_ids
        #     vals = {
        #         'name': quants[0].product_id.partner_ref,
        #         'origin': self.quant_package_id.name,
        #         'product_id': quants[0].product_id.id,
        #         'product_uom_qty': sum(quants.mapped('quantity')),
        #         'product_uom': quants[0].product_id.uom_id.id,
        #         'wood_kind_id': quants[0].wood_kind_id.id,
        #         'location_id': self.source_location_id.id,
        #         'location_dest_id': self.destination_location_id.id,
        #     }
        #     line_ids += [(0, 0, vals)]
        return line_ids
    
    def _prepare_move_lines(self):
        line_ids = []
        for pack in self.quant_package_ids:
            for quant in pack.quant_ids:
                vals = {
                    # 'origin': pack.name,
                    'product_id': quant.product_id.id,
                    'product_uom_id': quant.product_id.uom_id.id,
                    'lot_id': quant.lot_id.id,
                    'location_id': self.source_location_id.id,
                    'location_dest_id': self.destination_location_id.id,
                    'package_id': pack.id,
                    'result_package_id': pack.id,
                    'qty_done': quant.quantity,
                }
                line_ids += [(0, 0, vals)]
        return line_ids