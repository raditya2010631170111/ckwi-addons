# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from collections import Counter, defaultdict
from lxml import etree
import json
from odoo.exceptions import UserError, RedirectWarning, ValidationError

from odoo.addons.stock.models.stock_move import StockMove


def _action_done(self, cancel_backorder=False):
    moves = self.filtered(lambda move: move.state == 'draft')._action_confirm()  # MRP allows scrapping draft moves
    moves = (self | moves).exists().filtered(lambda x: x.state not in ('done', 'cancel'))
    moves_todo = self.env['stock.move']

    # Cancel moves where necessary ; we should do it before creating the extra moves because
    # this operation could trigger a merge of moves.
    for move in moves:
        if move.quantity_done <= 0:
            if float_compare(move.product_uom_qty, 0.0, precision_rounding=move.product_uom.rounding) == 0 or cancel_backorder:
                move._action_cancel()

    # Create extra moves where necessary
    for move in moves:
        if move.state == 'cancel' or move.quantity_done <= 0:
            continue

        moves_todo |= move._create_extra_move()

    moves_todo._check_company()
    # Split moves where necessary and move quants
    backorder_moves_vals = []
    for move in moves_todo:
        # To know whether we need to create a backorder or not, round to the general product's
        # decimal precision and not the product's UOM.
        rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        if float_compare(move.quantity_done, move.product_uom_qty, precision_digits=rounding) < 0:
            # Need to do some kind of conversion here
            qty_split = move.product_uom._compute_quantity(move.product_uom_qty - move.quantity_done, move.product_id.uom_id, rounding_method='HALF-UP')
            new_move_vals = move._split(qty_split)
            backorder_moves_vals += new_move_vals
    backorder_moves = self.env['stock.move'].create(backorder_moves_vals)
    backorder_moves._action_confirm(merge=False)
    if cancel_backorder:
        backorder_moves.with_context(moves_todo=moves_todo)._action_cancel()
    moves_todo.mapped('move_line_ids').sorted()._action_done()
    # Check the consistency of the result packages; there should be an unique location across
    # the contained quants.
    # HACKED by arisnew, tanpa validasi ini
    # for result_package in moves_todo\
    #         .mapped('move_line_ids.result_package_id')\
    #         .filtered(lambda p: p.quant_ids and len(p.quant_ids) > 1):
    #     if len(result_package.quant_ids.filtered(lambda q: not float_is_zero(abs(q.quantity) + abs(q.reserved_quantity), precision_rounding=q.product_uom_id.rounding)).mapped('location_id')) > 1:
    #         raise UserError(_('You cannot move the same package content more than once in the same transfer or split the same package into two location.'))
    picking = moves_todo.mapped('picking_id')
    moves_todo.write({'state': 'done', 'date': fields.Datetime.now()})

    move_dests_per_company = defaultdict(lambda: self.env['stock.move'])
    for move_dest in moves_todo.move_dest_ids:
        move_dests_per_company[move_dest.company_id.id] |= move_dest
    for company_id, move_dests in move_dests_per_company.items():
        move_dests.sudo().with_company(company_id)._action_assign()

    # We don't want to create back order for scrap moves
    # Replace by a kwarg in master
    if self.env.context.get('is_scrap'):
        return moves_todo

    if picking and not cancel_backorder:
        picking._create_backorder()
    return moves_todo

# override
StockMove._action_done = _action_done


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    is_qc_id = fields.Boolean('Is QC ?', default=False)
    # grading_done = fields.Boolean('Grading Done', default=False, related='product_id.grading_done')
    wood_type = fields.Selection([
        ('log', 'LOG'),
        ('square', 'Square Log'),
        ('timber', 'Sawn Timber')
    ], string='Type',related='product_id.wood_type')
    mo_id = fields.Many2one('mrp.production', string='Manufacture')
    qty_afkir = fields.Float(compute='_compute_qty_afkir', digits='Product Unit of Measure', string='Qty Afkir')
    
    transaction_date = fields.Datetime('Transaction Date', related='picking_id.transaction_date')
    
    @api.depends('move_line_ids.qty_done', 'move_line_ids.product_uom_id', 'move_line_nosuggest_ids.qty_done', 'picking_type_id')
    def _compute_qty_afkir(self):
        for rec in self:
            res = 0.00
            for move_line in rec.move_line_nosuggest_ids.filtered(lambda r:r.master_hasil == 'afkir'):
                res = res + move_line.qty_done
            rec.qty_afkir = res


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    is_jati = fields.Boolean('Is Jati?',related='product_id.product_tmpl_id.is_jati')
    size_log_id = fields.Many2one('res.size.log', string='Size Log',domain="[('is_jati','=',is_jati)]")
    panjang = fields.Float('Panjang (cm)')
    lebar = fields.Float('Lebar (cm)')
    tinggi = fields.Float('Tinggi')
    # TODO remove me, tidak ada Pcs di detail
    qty_received = fields.Float('Pcs')
    origin = fields.Char('Origin')
    master_hasil = fields.Selection([
        ('bagus', 'Bagus'),
        ('afkir', 'Afkir'),
        ('triming', 'Triming'),
        ('grade_a', 'Grade A'),
        ('grade_b', 'Grade B')
    ], string='Grading')
    wood_class_id = fields.Many2one(comodel_name='res.wood.class', string='Wood Class')
    diameter_slog = fields.Integer('Diameter', related='size_log_id.diameter_log', 
        readonly=False, store=True)
    panjang_slog = fields.Integer('Panjang', related='size_log_id.panjang_log',
        readonly=False, store=True)
    kubikasi_slog = fields.Float('Kubikasi Size log', 
        related='size_log_id.kubikasi', digits='Product Unit of Measure', store=True)

    #! DANGER! qty_done tidak boleh compute, karena dipakai dibanyak modul!
    # qty_done = fields.Float('Done', default=0.0,
    #     compute='_compute_qty_done', store=True )
    
    #! TODO silahkan gunakan on change
    # @api.depends('kubikasi_slog')
    # def _compute_qty_done(self):
    #     for r in self:
    #         r.qty_done = r.kubikasi_slog
    
    @api.onchange('kubikasi_slog')
    def onchange_field(self):
        self.qty_done = self.kubikasi_slog
    
    @api.onchange(
        'move_id.product_id',
        'size_log_id',
        'panjang',
        'lebar',
        'tinggi',
        'qty_received'
        )
    def _onchange_qty_done_from_wood_type(self):
        for rec in self:
            res = 0.00
            if rec.move_id.product_id and rec.move_id.product_id.wood_type:
                if rec.move_id.product_id.wood_type == 'log' and rec.size_log_id:
                    res = rec.size_log_id.kubikasi
                if rec.move_id.product_id.wood_type == 'square' and rec.panjang and rec.lebar and rec.tinggi:
                    kubikasi = rec.panjang * rec.lebar * rec.tinggi
                    res = kubikasi / 1000000 if kubikasi > 0 else 0.00
                if rec.move_id.product_id.wood_type == 'timber' and rec.panjang and rec.lebar and rec.tinggi:
                    # kubikasi = rec.panjang * rec.lebar * rec.tinggi * rec.qty_received
                    # tidak ada Pcs (qty_received)
                    kubikasi = rec.panjang * rec.lebar * rec.tinggi
                    res = kubikasi / 1000000 if kubikasi > 0 else 0.00
            rec.qty_done = res
            
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(StockMoveLine, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        fields = res.get('fields')
        wood_type = self._context.get('wood_type')
        if fields and fields.get('tinggi'):
            if wood_type and wood_type == 'timber':
                res['fields']['tinggi']['string'] = 'Tebal (cm)'
        doc = etree.fromstring(res['arch'])
        for field in doc.xpath('//field[@name="master_hasil"]'):
            modifiers = json.loads(field.get('modifiers', '{}'))
            params = self._context.get('params')
            if params and params.get('model') and params.get('model') != 'stock.picking':
                # modifiers['column_invisible'] = True
                field.set('modifiers', json.dumps(modifiers))
        for field in doc.xpath('//field[@name="panjang"]'):
            modifiers = json.loads(field.get('modifiers', '{}'))
            params = self._context.get('params')
            if params and params.get('model') and params.get('model') != 'stock.picking':
                modifiers['column_invisible'] = True
                field.set('modifiers', json.dumps(modifiers))
        for field in doc.xpath('//field[@name="lebar"]'):
            modifiers = json.loads(field.get('modifiers', '{}'))
            params = self._context.get('params')
            if params and params.get('model') and params.get('model') != 'stock.picking':
                modifiers['column_invisible'] = True
                field.set('modifiers', json.dumps(modifiers))
        for field in doc.xpath('//field[@name="tinggi"]'):
            modifiers = json.loads(field.get('modifiers', '{}'))
            params = self._context.get('params')
            if params and params.get('model') and params.get('model') != 'stock.picking':
                modifiers['column_invisible'] = True
                field.set('modifiers', json.dumps(modifiers))
        res['arch'] = etree.tostring(doc)
        return res