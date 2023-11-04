from odoo import models, fields, api,  _
from odoo.exceptions import UserError, ValidationError
from re import findall as regex_findall
from re import split as regex_split
from odoo.tools.float_utils import float_compare
import datetime
import pytz

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    nota = fields.Char('No. Nota')
    plat_no = fields.Char('No. Mobil')
    qty_nota = fields.Float('Surat Jalan (PCS)')
    cubic_nota = fields.Float('Surat Jalan (M3)')
    depart_no = fields.Integer('No. Kedatangan')
    fee_location_id = fields.Many2one('res.location', string='Lokasi')
    wood_type = fields.Selection([
        ('akasia', 'AKASIA'),
        ('gamelina', 'GAMELINA'),
        ('jati', 'JATI'),
        ('jati p', 'JATI P'),
        ('mahoni', 'MAHONI'),
        ('rawa', 'RAWA'),
        ('sq jati', 'SQ jati'),
        ('sq mahoni', 'SQ MAHONI')
    ], string='Jenis Kayu')
    certification_id = fields.Many2one('res.certification', string='Sertifikasi' ,compute='_compute_certification_id')
    is_tagcard = fields.Boolean('Is Tagcard', default=False)
    type_operation = fields.Selection([
        ('incoming', 'Receipt'),
        ('outgoing', 'Delivery'),
        ('internal', 'Internal Transfer')],
        'Type of Operation', required=True, related='picking_type_id.code') #invisible
    is_delivery = fields.Boolean('Is Delivery', default=False, store=True, compute='_compute_is_delivery')
    no_kend = fields.Char('No. Kendaraan')
    tagih = fields.Selection([
        ('ya', 'YA'),
        ('tidak', 'TIDAK')
        ], string='Tagih')
    transaction_date = fields.Datetime('Transaction Date')
    
    # TODO seharusnya jangan lookup pakai name
    def _compute_certification_id(self):
        for picking in self:
            sale_order = self.env['purchase.order'].search([('name', '=', picking.origin)], limit=1)
            picking.certification_id = sale_order.certification_id

    def action_print_session(self):
        return self.env.ref('jidoka_inventory.report_stock_picking_action').report_action(self)   

    @api.depends('type_operation')
    def _compute_is_delivery(self):
        for r in self:
            if r.type_operation == 'outgoing':
                r.is_delivery = True
            else:
                r.is_delivery = False
    
    def _compute_certification(self):
        for rec in self:
            res = False
            res_ids = rec.move_ids_without_package.mapped('product_id').mapped('certification')
            if res_ids and len(res_ids) > 0:
                res = res_ids[0]
            rec.certification = res

    def _needs_automatic_assign(self):
        self.ensure_one()
        if self.sale_id:
            return False
        return True
     
    def generate_multi_product(self):
        return {
            'name': _('Generate Detailed Operations Purchase '),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wiz.generate.purchase',
            'target': 'new',
            'context': {'default_purchase_id': self.id}
        }
    
    
class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    mo_id = fields.Many2one('mrp.production', string='Kode Prod &amp; Item')

    def _generate_serial_move_line_commands(self, lot_names, origin_move_line=None, lines=None):
        """Return a list of commands to update the move lines (write on
        existing ones or create new ones).
        Called when user want to create and assign multiple serial numbers in
        one time (using the button/wizard or copy-paste a list in the field).

        :param lot_names: A list containing all serial number to assign.
        :type lot_names: list
        :param origin_move_line: A move line to duplicate the value from, default to None
        :type origin_move_line: record of :class:`stock.move.line`
        :return: A list of commands to create/update :class:`stock.move.line`
        :rtype: list
        """
        self.ensure_one()

        # Select the right move lines depending of the picking type configuration.
        move_lines = self.env['stock.move.line']
        if self.picking_type_id.show_reserved:
            move_lines = self.move_line_ids.filtered(lambda ml: not ml.lot_id and not ml.lot_name)
        else:
            move_lines = self.move_line_nosuggest_ids.filtered(lambda ml: not ml.lot_id and not ml.lot_name)

        if origin_move_line:
            location_dest = origin_move_line.location_dest_id
        else:
            location_dest = self.location_dest_id._get_putaway_strategy(self.product_id)
        move_line_vals = {
            'picking_id': self.picking_id.id,
            'location_dest_id': location_dest.id or self.location_dest_id.id,
            'location_id': self.location_id.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_id.id,
            'qty_done': 0,
        }
        if origin_move_line:
            # `owner_id` and `package_id` are taken only in the case we create
            # new move lines from an existing move line. Also, updates the
            # `qty_done` because it could be usefull for products tracked by lot.
            move_line_vals.update({
                'owner_id': origin_move_line.owner_id.id,
                'package_id': origin_move_line.package_id.id,
                'qty_done': origin_move_line.qty_done or 1,
            })

        move_lines_commands = []
        count = 0
        for lot_name in lot_names:
            # We write the lot name on an existing move line (if we have still one)...
            if move_lines:
                move_lines_commands.append((1, move_lines[0].id, {
                    'lot_name': lot_name,
                    'qty_done': 1,
                }))
                move_lines = move_lines[1:]
            # ... or create a new move line with the serial name.
            else:
                move_line_cmd = dict(move_line_vals, lot_name=lot_name)
                if lines:
                    move_line_cmd.update({
                        'panjang':lines[count].get('panjang') or 0.00, 
                        'lebar':lines[count].get('lebar') or 0.00, 
                        'tinggi':lines[count].get('tinggi') or 0.00, 
                        'qty_received':lines[count].get('qty_received') or 0.00,
                        'result_package_id':lines[count].get('result_package_id') or 0.00,
                        'master_hasil':lines[count].get('master_hasil') or 0.00
                    })
                move_lines_commands.append((0, 0, move_line_cmd))
                count = count + 1
        return move_lines_commands
    
    def _generate_serial_numbers(self, next_serial_count=False, lines = None):
        """ This method will generate `lot_name` from a string (field
        `next_serial`) and create a move line for each generated `lot_name`.
        """
        self.ensure_one()

        if not next_serial_count:
            next_serial_count = self.next_serial_count
        # We look if the serial number contains at least one digit.
        caught_initial_number = regex_findall("\d+", self.next_serial)
        if not caught_initial_number:
            raise UserError(_('The serial number must contain at least one digit.'))
        # We base the serie on the last number find in the base serial number.
        initial_number = caught_initial_number[-1]
        padding = len(initial_number)
        # We split the serial number to get the prefix and suffix.
        splitted = regex_split(initial_number, self.next_serial)
        # initial_number could appear several times in the SN, e.g. BAV023B00001S00001
        prefix = initial_number.join(splitted[:-1])
        suffix = splitted[-1]
        initial_number = int(initial_number)

        lot_names = []
        for i in range(0, next_serial_count):
            # if i == 0:
            #     lot_names.append('%s%s%s' % (
            #         prefix,
            #         str(initial_number).zfill(padding),
            #         suffix
            #     ))
            # else:
            lot_names.append('%s%s%s' % (
                    prefix,
                    self.env['ir.sequence'].next_by_code('stock.lot.serial'),
                    suffix
                ))
        move_lines_commands = self._generate_serial_move_line_commands(lot_names=lot_names, lines=lines)
        self.write({'move_line_ids': move_lines_commands})
        return True
    

    def action_show_details(self):
        self.ensure_one()
        action = super().action_show_details()
        if self.picking_id.picking_type_code == 'internal':
            action['context']['wood_type'] = self.wood_type
            return action
        if self.state not in ('done','cancel'):
            if self.picking_id:
                # if not self.picking_id.nota:
                #     raise UserError("Please input Nota Number before assign serial number.")
                if self.picking_id.picking_type_code != 'internal':
                    if not self.picking_id.partner_id.supplier_code_id:
                        raise UserError("Please fill in the supplier code first.")
                    if not self.picking_id.partner_id:
                        raise UserError("Please input Supplier before assign serial number.")
                if self.next_serial:
                    local_timezone = pytz.timezone(self.env.user.tz)
                    current_date = datetime.datetime.now(local_timezone)
                    month = current_date.strftime('%m')
                    year = current_date.strftime('%y')
                    self.next_serial = self.picking_id.partner_id.supplier_code_id.code + '-' + month + '-' + year + '-' + str(self.picking_id.depart_no) + '-' + '00000'
      
                if not self.next_serial:
                    local_timezone = pytz.timezone(self.env.user.tz)
                    current_date = datetime.datetime.now(local_timezone)
                    month = current_date.strftime('%m')
                    year = current_date.strftime('%y')
                    self.next_serial = self.picking_id.partner_id.supplier_code_id.code + '-' + month + '-' + year + '-' + str(self.picking_id.depart_no) + '-' + '00000'
        action['context']['wood_type'] = self.wood_type
        return action


    def action_assign_tag_cards(self):
        self.ensure_one()
        serial_number = ''
        if self.next_serial:
            serial_number = self.next_serial
        elif self.picking_id:
            # if not self.picking_id.nota:
                # raise UserError("Please input Nota Number before assign serial number.")
            if self.picking_id.picking_type_code != 'internal':
                if not self.picking_id.partner_id.supplier_code_id:
                    raise UserError("Please fill in the supplier code first.")
                if not self.picking_id.partner_id:
                        raise UserError("Please input Supplier before assign serial number.")
            if not self.next_serial:
                local_timezone = pytz.timezone(self.env.user.tz)
                current_date = datetime.datetime.now(local_timezone)
                month = current_date.strftime('%m')
                year = current_date.strftime('%y')
                serial_number = self.picking_id.partner_id.supplier_code_id.code + '-' + month + '-' + year + '-' + str(self.picking_id.depart_no) + '-' + '00000'
        # action['context']['wood_type'] = self.wood_type
        action = self.env["ir.actions.actions"]._for_xml_id("jidoka_inventory.act_assign_tag_card")
        action['context'] = {
            'default_product_id': self.product_id.id,
            'default_move_id': self.id,
            'default_company_id': self.company_id.id,
            'default_next_serial_number': serial_number,
            'wood_type':self.wood_type
        }
        return action
    
    @api.depends('has_tracking', 'picking_type_id.use_create_lots', 'picking_type_id.use_existing_lots', 'state')
    def _compute_display_assign_serial(self):
        for move in self:
            move.display_assign_serial = (
                move.has_tracking in ['serial', 'lot'] and
                move.state in ('partially_available', 'assigned', 'confirmed') and
                move.picking_type_id.use_create_lots and
                not move.picking_type_id.use_existing_lots
                and not move.origin_returned_move_id.id
            )