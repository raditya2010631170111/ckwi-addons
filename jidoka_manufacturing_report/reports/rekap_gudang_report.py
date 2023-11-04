from odoo import api, fields, models
from datetime import date
from datetime import datetime

class RekapGudangView(models.TransientModel):
    _name = "rekap.gudang.view"
    _description = "Rekap Gudang View"
    _order = "date"


    date = fields.Datetime()
    reference = fields.Char()
    product_tmpl_id = fields.Many2one(comodel_name="product.template", related='product_id.product_tmpl_id')
    product_id = fields.Many2one(comodel_name="product.product")
    product = fields.Many2one(comodel_name="product.product")
    product_out = fields.Float()
    product_in = fields.Float()
    is_initial = fields.Boolean()
    size_panjang = fields.Float(store=True, related='product_tmpl_id.size_panjang')
    size_lebar = fields.Float(store=True, related='product_tmpl_id.size_lebar')
    size_tebal = fields.Float(store=True, related='product_tmpl_id.size_tebal')
    product_uom_id = fields.Many2one(comodel_name="uom.uom")
    location_id = fields.Many2one(comodel_name="stock.location")
    location_dest_id = fields.Many2one(comodel_name="stock.location")
    sale_id = fields.Many2one('sale.order')
    
    
    def name_get(self):
        result = []
        for rec in self:
            name = rec.reference
            result.append((rec.id, name))
        return result


class RekapGudangReport(models.TransientModel):
    _name = "rekap.gudang.report"
    _description = "Rekap Gudang Report"


    date_from = fields.Date()
    date_to = fields.Date()
    location_id = fields.Many2one(comodel_name="stock.location")
    sale_ids = fields.Many2many('sale.order', string='No. SC')
    results = fields.Many2many(
        comodel_name="rekap.gudang.view",
        compute="_compute_results",
        help="Use compute fields, so there is nothing store in database",
    )

    def _compute_results(self):
        self.ensure_one()
        date_from = self.date_from or "0001-01-01"
        self.date_to = self.date_to or fields.Date.context_today(self)
        locations = self.env["stock.location"].search(
            [("id", "child_of", [self.location_id.id])]
        )

        self._cr.execute(
            """
            SELECT 
                line.product_id,
                line.product_uom_id,
                move.date AS date, 
                SUM(CASE WHEN line.location_dest_id in %s THEN line.qty_done END) AS product_in,
                SUM(CASE WHEN line.location_id in %s THEN line.qty_done END) AS product_out
            FROM stock_move_line line
            INNER JOIN stock_move move ON line.move_id = move.id
            LEFT JOIN uom_uom uom ON line.product_uom_id = uom.id
            WHERE 
                move.date >= %s and move.date <= %s
                AND move.state = 'done' 
                AND (line.location_id in %s OR line.location_dest_id in %s)
            GROUP BY line.product_id, line.product_uom_id, move.date 
            ORDER BY line.product_id, move.date 
            """,
            (
                tuple(locations.ids),
                tuple(locations.ids),
                date_from,
                self.date_to,
                tuple(locations.ids),
                tuple(locations.ids),
            ),
        )
        stock_card_results = self._cr.dictfetchall()
        ReportLine = self.env["rekap.gudang.view"]
        self.results = [ReportLine.new(line).id for line in stock_card_results]


    # def _compute_results(self):
    #     self.ensure_one()
    #     date_from = self.date_from
    #     date_to = self.date_to
    #     locations = self.env["stock.location"].search(
    #         [("id", "child_of", [self.location_id.id])]
    #     )
    #     sc = self.sale_ids.ids
        
    #     result_list = []
    #     stock_move_out = self.env['stock.move'].search([
    #         ('date', '<=', date_to),
    #         ('location_id', 'in', locations.ids),
    #         ('raw_material_production_id.no_sc_id', 'in', sc)])
    #     for out in stock_move_out:
    #         parent = self.env['mrp.production'].search([('name', '=', out.raw_material_production_id.origin)], limit=1)
    #         if parent:
    #             child_parent = self.env['mrp.production'].search([('name', '=', parent.origin)], limit=1)
    #             if child_parent:
    #                 product = child_parent.product_id.id
    #             else:
    #                 product = parent.product_id.id
    #         else:
    #             product = out.raw_material_production_id.product_id.id

    #         dt = datetime.combine(date_from, datetime.max.time())
    #         if out.date < dt:
    #             is_initial = True
    #         else:
    #             is_initial = False

    #         value = {
    #             'date' : out.date,
    #             'reference' : out.reference,
    #             'product_id' : out.product_id.id,
    #             'product' : product,
    #             'product_out': out.quantity_done,
    #             'product_uom' : out.product_uom.id,
    #             'is_initial': is_initial,
    #             'sale_id': out.raw_material_production_id.no_sc_id.id,
    #             'location_id': out.location_id.id,
    #             'location_dest_id': out.location_dest_id.id,
    #         }
    #         result_list.append(value)
            
    #     stock_move_in = self.env['stock.move.line'].search([
    #         ('date', '<=', date_to),
    #         ('location_dest_id', 'in', locations.ids),
    #         ])
    #     for in_ in stock_move_in:
    #         mo = self.env['mrp.production'].search([
    #             ('name', '=', in_.reference),
    #             ('no_sc_id', 'in', sc)])
    #         if mo:
    #             parent = self.env['mrp.production'].search([('name', '=', mo.origin)], limit=1)
    #             if parent:
    #                 child_parent = self.env['mrp.production'].search([('name', '=', parent.origin)], limit=1)
    #                 if child_parent:
    #                     product = child_parent.product_id.id
    #                 else:
    #                     product = parent.product_id.id
    #             else:
    #                 product = mo.product_id.id

    #             dt = datetime.combine(date_from, datetime.max.time())
    #             if in_.date < dt:
    #                 is_initial = True
    #             else:
    #                 is_initial = False

    #             value = {
    #                 'date' : in_.date,
    #                 'reference' : in_.reference,
    #                 'product_id' : in_.product_id.id,
    #                 'is_initial': is_initial,
    #                 'product' : product,
    #                 'product_in' : in_.qty_done,
    #                 'product_uom' : in_.product_uom_id.id,
    #                 'sale_id': mo.no_sc_id.id,
    #                 'location_id': in_.location_id.id,
    #                 'location_dest_id': in_.location_dest_id.id,
    #             }
    #             result_list.append(value)

    #     ReportLine = self.env['rekap.gudang.view']
    #     self.results = [ReportLine.new(line).id for line in result_list]

    def print_report(self, report_type="qweb"):
        self.ensure_one()
        action = (
            report_type == "xlsx"
            and self.env.ref("jidoka_manufacturing_report.action_rekap_gudang_report_xlsx")
            or self.env.ref("jidoka_manufacturing_report.action_rekap_gudang_report_pdf")
        )
        return action.report_action(self, config=False)
    
    def _get_initial(self, product_line):
        product_input_qty = sum(product_line.mapped("product_in"))
        product_output_qty = sum(product_line.mapped("product_out"))
        return product_input_qty - product_output_qty

    def _get_html(self):
        result = {}
        rcontext = {}
        report = self.browse(self._context.get("active_id"))
        if report:
            rcontext["o"] = report
            result["html"] = self.env.ref(
                "jidoka_manufacturing_report.report_rekap_gudang_report_html"
            )._render(rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()
