# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import date
from datetime import datetime


class StockCardView(models.TransientModel):
    _name = "manufacturing.view"
    _description = "Manufacturing View"
    _order = "date"


    date = fields.Datetime()
    reference = fields.Char()
    cons_product_id = fields.Many2one(comodel_name="product.product")
    fg_product_id = fields.Many2one(comodel_name="product.product")
    product_out = fields.Float()
    product_in = fields.Float()
    is_initial = fields.Boolean()
    product_uom = fields.Many2one(comodel_name="uom.uom")
    location_id = fields.Many2one(comodel_name="stock.location")
    location_dest_id = fields.Many2one(comodel_name="stock.location")
    sale_id = fields.Many2one('sale.order')
    

    def name_get(self):
        result = []
        for rec in self:
            name = rec.reference
            result.append((rec.id, name))
        return result


class StockCardReport(models.TransientModel):
    _name = "manufacturing.report"
    _description = "Manufacturing Report"


    date_from = fields.Date()
    date_to = fields.Date()
    location_id = fields.Many2one(comodel_name="stock.location")
    sale_ids = fields.Many2many('sale.order', string='No. SC')
    results = fields.Many2many(
        comodel_name="manufacturing.view",
        compute="_compute_results",
        help="Use compute fields, so there is nothing store in database",
    )

    def stock_move_out(self, mo):
        product_fg = False
        child_mo = self.env['mrp.production'].search([('name', '=', mo.origin)], limit=1)
        if child_mo:
            product_fg = self.stock_move_out(child_mo)
        else:
            product_fg = mo.product_id.id

        return product_fg
    
    def stock_move_in(self, mo):
        product_fg = False
        child_mo = self.env['mrp.production'].search([('name', '=', mo.origin)], limit=1)
        if child_mo:
            product_fg = self.stock_move_in(child_mo)
        else:
            product_fg = mo.product_id.id

        return product_fg

    def _compute_results(self):
        self.ensure_one()
        date_from = self.date_from
        date_to = self.date_to
        locations = self.env["stock.location"].search(
            [("id", "child_of", [self.location_id.id])]
        )
        sc = self.sale_ids.ids
        
        result_list = []
        stock_move_out = self.env['stock.move'].search([
            ('date', '<=', date_to),
            ('location_id', 'in', locations.ids),
            ('raw_material_production_id.no_sc_id', 'in', sc)])
        for out in stock_move_out:
            parent = self.env['mrp.production'].search([('name', '=', out.raw_material_production_id.origin)], limit=1)
            if parent:
                product_fg = self.stock_move_out(parent)
            else:
                product_fg = out.raw_material_production_id.product_id.id

            dt = datetime.combine(date_from, datetime.max.time())
            if out.date < dt:
                is_initial = True
            else:
                is_initial = False

            value = {
                'date' : out.date,
                'reference' : out.reference,
                'cons_product_id' : out.product_id.id,
                'fg_product_id' : product_fg,
                'product_out': out.quantity_done,
                'product_uom' : out.product_uom.id,
                'is_initial': is_initial,
                'sale_id': out.raw_material_production_id.no_sc_id.id,
                'location_id': out.location_id.id,
                'location_dest_id': out.location_dest_id.id,
            }
            result_list.append(value)

        stock_move_in = self.env['stock.move.line'].search([
            ('date', '<=', date_to),
            ('location_dest_id', 'in', locations.ids),
            ])
        for in_ in stock_move_in:
            mo = self.env['mrp.production'].search([
                ('name', '=', in_.reference),
                ('no_sc_id', 'in', sc)])
            if mo:
                parent = self.env['mrp.production'].search([('name', '=', mo.origin)], limit=1)
                if parent:
                    product_fg = self.stock_move_in(parent)
                else:
                    product_fg = mo.product_id.id

                dt = datetime.combine(date_from, datetime.max.time())
                if in_.date < dt:
                    is_initial = True
                else:
                    is_initial = False

                value = {
                    'date' : in_.date,
                    'reference' : in_.reference,
                    'cons_product_id' : in_.product_id.id,
                    'is_initial': is_initial,
                    'fg_product_id' : product_fg,
                    'product_in' : in_.qty_done,
                    'product_uom' : in_.product_uom_id.id,
                    'sale_id': mo.no_sc_id.id,
                    'location_id': in_.location_id.id,
                    'location_dest_id': in_.location_dest_id.id,
                }
                result_list.append(value)

        ReportLine = self.env['manufacturing.view']
        self.results = [ReportLine.new(line).id for line in result_list]

    def print_report(self, report_type="qweb"):
        self.ensure_one()
        action = (
            report_type == "xlsx"
            and self.env.ref("jidoka_manufacturing_report.action_manufacturing_report_xlsx")
            or self.env.ref("jidoka_manufacturing_report.action_manufacturing_report_pdf")
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
                "jidoka_manufacturing_report.manufacturing_report_html"
            )._render(rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()