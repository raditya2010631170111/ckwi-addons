# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)






class StockCardView(models.TransientModel):
    _name = "manufacturing.summary.view"
    _description = "Stock Card View"
    _order = "date"

    date = fields.Datetime()
    product_id = fields.Many2one(comodel_name="product.product")
    product = fields.Many2one(comodel_name="product.product")
    product_qty = fields.Float()
    product_uom_qty = fields.Float()
    product_uom = fields.Many2one(comodel_name="uom.uom")
    reference = fields.Char()
    location_id = fields.Many2one(comodel_name="stock.location")
    location_dest_id = fields.Many2one(comodel_name="stock.location")
    is_initial = fields.Boolean()
    product_in = fields.Float()
    product_out = fields.Float()
    initial_balance = fields.Float(
        string="Initial Balance",
        help="Initial stock balance for the selected period",
    )

    picking_id = fields.Many2one(comodel_name="stock.picking")

    def name_get(self):
        result = []
        for rec in self:
            name = rec.reference
            if rec.picking_id.origin:
                name = "{} ({})".format(name, rec.picking_id.origin)
            result.append((rec.id, name))
        return result


class StockCardReport(models.TransientModel):
    _name = "manufacturing.summary.report"
    _description = "Stock Card Report"

    # Filters fields, used for data computation
    date_from = fields.Date()
    date_to = fields.Date()
    product_ids = fields.Many2many(comodel_name="product.product")
    location_id = fields.Many2one(comodel_name="stock.location")

    # Data fields, used to browse report data
    results = fields.Many2many(
        comodel_name="manufacturing.summary.view",
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
                SUM(CASE WHEN line.location_dest_id in %s THEN line.qty_done END) AS product_in,
                SUM(CASE WHEN line.location_id in %s THEN line.qty_done END) AS product_out
            FROM stock_move_line line
            INNER JOIN stock_move move ON line.move_id = move.id
            WHERE 
                move.date >= %s and move.date  <= %s
                AND move.state = 'done' 
                AND (line.location_id in %s OR line.location_dest_id in %s)
            GROUP BY line.product_id
            ORDER BY line.product_id
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

        # cari saldo awal
        self._cr.execute(
            """
            SELECT 
                line.product_id,
                (
                    SUM(CASE WHEN line.location_dest_id in %s THEN line.qty_done ELSE 0 END) - 
                    SUM(CASE WHEN line.location_id in %s THEN line.qty_done ELSE 0 END)
                ) AS initial_balance
            FROM stock_move_line line
            INNER JOIN stock_move move ON line.move_id = move.id
            WHERE 
                move.date < %s
                AND move.state = 'done' 
                AND (line.location_id in %s OR line.location_dest_id in %s)
            GROUP BY line.product_id
            ORDER BY line.product_id
            """,
            (
                tuple(locations.ids),
                tuple(locations.ids),
                date_from,
                tuple(locations.ids),
                tuple(locations.ids),
            ),
        )
        initial_results = self._cr.dictfetchall()
        # make sure combine product_id
        combined_data = []
        # update combined data with initial & transaction

        """
        {
            'product_id': 1,
            'initial_balance': 1,
            'product_in': 1,
            'product_out': 1,
        }
        """
        combined_data = []

        for product_data in stock_card_results:
            product_id = product_data['product_id']
            combined_entry = {
                'product_id': product_id,
                'product_in': product_data['product_in'],
                'product_out': product_data['product_out'],
                'initial_balance': 0, 
            }
            
            for initial_data in initial_results:
                if initial_data['product_id'] == product_id:
                    combined_entry['initial_balance'] = initial_data['initial_balance']
                    break
            
            combined_data.append(combined_entry)

        ReportLine = self.env["manufacturing.summary.view"]
        self.results = [ReportLine.new(line).id for line in combined_data]


    def _get_initial(self, product_line):
        product_input_qty = sum(product_line.mapped("product_in"))
        product_output_qty = sum(product_line.mapped("product_out"))
        return product_input_qty - product_output_qty

    def print_report(self, report_type="qweb"):
        self.ensure_one()
        action = (
            report_type == "xlsx"
            and self.env.ref("jidoka_manufacturing_report.action_manufacturing_report_summary_xlsx")
            or self.env.ref("jidoka_manufacturing_report.action_manufacturing_summary_report_pdf")
        )
        return action.report_action(self, config=False)

    def _get_html(self):
        result = {}
        rcontext = {}
        report = self.browse(self._context.get("active_id"))
        if report:
            rcontext["o"] = report
            result["html"] = self.env.ref(
                "jidoka_manufacturing_report.manufacturing_summary_html"
            )._render(rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()
