from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockPickingBatch1(models.Model):
    _inherit = "stock.picking.batch"
    
    name1 = fields.Char(string='Operation Type Name')
    
    ups_awb_no = fields.Char('UPS AWB NO ')

    location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        )

    no_kend = fields.Char('No. Kendaraan')
    tagih = fields.Selection([
        ('ya', 'YA'),
        ('tidak', 'TIDAK')
        ], string='Tagih')

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        if self.picking_type_id:
            # picking_type_name = self.picking_type_id.name
            picking_loc = self.picking_type_id.default_location_src_id
            # Ubah `picking_type_name` sesuai dengan format yang diinginkan

            # self.name1 = picking_loc
            self.location_id = picking_loc

    @api.onchange('location_id')
    def onchange_location_id(self):
        if self.location_id:
            self.name1 = self.location_id.name

    @api.model
    def create(self, vals):
        if vals.get('name1') == 'Vacuum':
            seq = self.env['ir.sequence'].next_by_code('picking.batch.gdbb') 
            vals['name'] = seq
        elif vals.get('name1') == 'Sticking':
            seq = self.env['ir.sequence'].next_by_code('picking.batch.gdbb') 
            vals['name'] = seq
        elif vals.get('name1') == 'Sawmill':
            seq = self.env['ir.sequence'].next_by_code('picking.batch.gdbb') 
            vals['name'] = seq
        elif vals.get('name1') == 'Log':
            seq = self.env['ir.sequence'].next_by_code('picking.batch.gdbb') 
            vals['name'] = seq
        elif vals.get('name1') == 'GD Kayu Basah':
            seq = self.env['ir.sequence'].next_by_code('picking.batch.gdbb') 
            vals['name'] = seq
        elif vals.get('name1') == 'GD Kayu Kering':
            seq = self.env['ir.sequence'].next_by_code('picking.batch.gdbb') 
            vals['name'] = seq
        elif vals.get('name1') == 'Oven':
            seq = self.env['ir.sequence'].next_by_code('picking.batch.gdbb') 
            vals['name'] = seq
        elif vals.get('name1') == 'GD Molding Komponen':
            seq = self.env['ir.sequence'].next_by_code('picking.batch.gmld') 
            vals['name'] = seq
        elif vals.get('name1') == 'GD Setengah Jadi':
            seq = self.env['ir.sequence'].next_by_code('picking.batch.gbsj') 
            vals['name'] = seq
        elif vals.get('name1') == 'GD Barang Jadi':
            seq = self.env['ir.sequence'].next_by_code('picking.batch.gdbj') 
            vals['name'] = seq
        elif vals.get('name1') == 'GD Aksesoris & Bahan Penolong':
            seq = self.env['ir.sequence'].next_by_code('picking.batch.gasc') 
            vals['name'] = seq
        elif vals.get('name1') == 'GD Sparepart':
            seq = self.env['ir.sequence'].next_by_code('picking.batch.gspt') 
            vals['name'] = seq
        elif vals.get('name1') == 'Maintenance':
            seq = self.env['ir.sequence'].next_by_code('picking.batch.gmtc') 
            vals['name'] = seq
            
        return super(StockPickingBatch1, self).create(vals)

    def action_confirm(self):
        """Sanity checks, confirm the pickings and mark the batch as confirmed."""
        self.ensure_one()
        if not self.picking_ids:
            raise UserError(_("You have to set some pickings to batch."))
        self.picking_ids.action_confirm()
        self._check_company()
        awb_vals = []
        awb_vals.append({
            'name': self.ups_awb_no,
            'batch_transfer_id': self.id,
            'transfer_ids': self.picking_ids,
        })
        awb = self.env['awb'].create(awb_vals)
        self.state = 'in_progress'
        return True


    # def action_confirm(self):
    #     """Sanity checks, confirm the pickings and mark the batch as confirmed."""
    #     self.ensure_one()
    #     if not self.picking_ids:
    #         raise UserError(_("You have to set some pickings to batch."))

    #     # Get sequence code based on the picking type
    #     sequence_code = False
    #     if self.picking_type_id.id == 1:
    #         sequence_code = 'stock.picking.picking.batch.sawmill'
    #     elif self.picking_type_id.id == 2:
    #         sequence_code = 'stock.picking.picking.batch.sticking'

    #     # Generate sequence if code is available
    #     if sequence_code:
    #         sequence = self.env['ir.sequence'].next_by_code(sequence_code)
    #         self.name = sequence

    #     self.picking_ids.action_confirm()
    #     self._check_company()

    #     self.state = 'in_progress'
    #     return True

