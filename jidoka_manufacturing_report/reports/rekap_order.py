# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RekapOrderView(models.TransientModel):
    _name = "rekap.view"
    _description = "Stock Card View"
    _order = "date"

    date = fields.Datetime()
    reference = fields.Char()
    cons_product_id = fields.Many2one(comodel_name="product.product")
    fg_product_id = fields.Many2one(comodel_name="product.product")
    comp_quantity = fields.Float()
    comp_quantity_done = fields.Float()
    quantity_product_fg = fields.Float()
    product_uom = fields.Many2one(comodel_name="uom.uom")
    location_id = fields.Many2one(comodel_name="stock.location")
    buyer_id = fields.Many2one(comodel_name="res.partner")
    size_panjang = fields.Float()
    size_lebar = fields.Float()
    size_tebal = fields.Float()
    colour_id = fields.Many2one(comodel_name="res.fabric.colour")
    wood_shape_id = fields.Many2one(comodel_name='jidoka.woodshape')
    wood_grade_id = fields.Many2one(comodel_name='wood.grade', string='Grade')
    # total_meter = fields.Float()
    # meter_kubik = fields.Float()
    sale_id = fields.Many2one('sale.order')

    perlu_quantity = fields.Float(compute="_compute_perlu_quantity")
    @api.depends('quantity_product_fg', 'comp_quantity')
    def _compute_perlu_quantity(self):
        for rec in self:
            rec.perlu_quantity = rec.quantity_product_fg * rec.comp_quantity

    kurang_quantity = fields.Float(compute="_compute_kurang_quantity")
    @api.depends('perlu_quantity', 'comp_quantity_done')
    def _compute_kurang_quantity(self):
        for rec in self:
            rec.kurang_quantity = rec.perlu_quantity - rec.comp_quantity_done
        

    def name_get(self):
        result = []
        for rec in self:
            name = rec.reference
            result.append((rec.id, name))
        return result

class RekapOrderReport(models.TransientModel):
    _name = "rekap.report"
    _description = "Stock Card Report"

    date_from = fields.Date()
    date_to = fields.Date()
    location_id = fields.Many2one(comodel_name="stock.location")
    sale_ids = fields.Many2many('sale.order', string='No. SC')
    results = fields.Many2many(
        comodel_name="rekap.view",
        compute="_compute_results",
        help="Use compute fields, so there is nothing store in database",
    )

    def _compute_results(self):
        self.ensure_one()
        date_from = self.date_from
        date_to = self.date_to
        locations = self.env["stock.location"].search(
            [("id", "child_of", [self.location_id.id])]
        )
        sc = self.sale_ids.ids
        
        result_list = []

        stock_move = self.env['stock.move'].search([
        ('date', '<=', date_to),
        ('date', '>=', date_from),
        ('location_id', 'in', locations.ids),
        ('raw_material_production_id.no_sc_id', 'in', sc)
            ])
     
        for move in stock_move:
            # mo = self.env['mrp.production'].search([
            #         ('name', '=', move.reference),
            #         ('no_sc_id', '=', sc),
            #         ])
            # if mo:
                # work, potongan kode 'In' manufacruting_report.py
                # parent = self.env['mrp.production'].search([('name', '=', mo.origin)], limit=1)
                # if parent:
                #     child_parent = self.env['mrp.production'].search([('name', '=', parent.origin)], limit=1)
                #     if child_parent:
                #         product_fg = child_parent.product_id.id
                #     else:
                #         product_fg = parent.product_id.id
                # else:
                #     product_fg = mo.product_id.id

                # perbedaan dengan yang diatas = unknown, potongan kode 'Out' manufacturing_report.py
            parent = self.env['mrp.production'].search([('name', '=', move.raw_material_production_id.origin)], limit=1)
            if parent:
                child_parent = self.env['mrp.production'].search([('name', '=', parent.origin)], limit=1)
                if child_parent:
                    product_fg = child_parent.product_id.id
                else:
                    product_fg = parent.product_id.id
            else:
                product_fg = move.raw_material_production_id.product_id.id


            fg_order_line = self.env['sale.order.line'].search([
                ('order_id', '=', move.raw_material_production_id.no_sc_id.id),
                ('product_id', '=', product_fg),
            ], limit=1)
            if fg_order_line:
                fg_product_qty = fg_order_line.product_uom_qty

            comp_quantity_line = self.env['mrp.bom'].search([
                ('product_tmpl_id', '=', move.product_id.product_tmpl_id.id)
            ], limit=1)
            comp_qty = comp_quantity_line.product_qty

            value = {
                'date': move.date,
                'reference': move.reference,
                'location_id': move.location_id.id,
                'product_uom': move.product_uom.id,
                'sale_id': move.raw_material_production_id.no_sc_id.id,
                'fg_product_id' : product_fg,
                'cons_product_id': move.product_id.id,
                'quantity_product_fg' : fg_product_qty,
                'size_panjang': move.product_id.size_panjang,
                'size_lebar': move.product_id.size_lebar,
                'size_tebal': move.product_id.size_tebal,
                'comp_quantity': comp_qty,
                'comp_quantity_done': move.quantity_done,
                'wood_shape_id' : move.product_id.wood_shape_id.id,
                'wood_grade_id' : move.product_id.wood_grade_id.id,
                'colour_id' : move.product_id.colour_id.id,
                # 'total_meter': move.product_id.total_meter,
                # 'meter_kubik': move.product_id.total_meter_cubic,
                'buyer_id': move.partner_id.id,
            }
            result_list.append(value)


        ReportLine = self.env['rekap.view']
        self.results = [ReportLine.new(line).id for line in result_list]

    def print_report(self, report_type="qweb"):
        self.ensure_one()
        action = (
            report_type == "xlsx"
            and self.env.ref("jidoka_manufacturing_report.action_rekap_order_xlsx")
            or self.env.ref("jidoka_manufacturing_report.action_rekap_order_pdf")
        )
        return action.report_action(self, config=False)

    def _get_html(self):
        result = {}
        rcontext = {}
        report = self.browse(self._context.get("active_id"))
        if report:
            rcontext["o"] = report
            result["html"] = self.env.ref(
                "jidoka_manufacturing_report.rekap_order_html"
            )._render(rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()