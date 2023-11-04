# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class ManufacturingReportWizard(models.TransientModel):
    _name = "manufacturing.report.wizard"
    _description = "Manufacturing Report Wizard"


    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    sale_ids = fields.Many2many('sale.order', string='No. SC')
    location_id = fields.Many2one(comodel_name='stock.location', string='Source Location')


    def button_export_html(self):
        self.ensure_one()
        action = self.env.ref("jidoka_manufacturing_report.action_manufacturing_report_html")
        vals = action.sudo().read()[0]
        context = vals.get("context", {})
        if context:
            context = safe_eval(context)
        model = self.env["manufacturing.report"]
        report = model.create(self._prepare_manufacturing_report())
        context["active_id"] = report.id
        context["active_ids"] = report.ids
        vals["context"] = context
        print (vals)
        return vals

    def button_export_pdf(self):
        self.ensure_one()
        report_type = "qweb-pdf"
        return self._export(report_type)
        print("=================>>>")

    def button_export_xlsx(self):
        self.ensure_one()
        report_type = "xlsx"
        return self._export(report_type)

    def _prepare_manufacturing_report(self):
        self.ensure_one()
        sale_ids = self.env['mrp.production'].search([]).mapped('no_sc_id')
        if self.sale_ids:
            sale_ids = self.sale_ids
        return {
            "sale_ids": [(6, 0, sale_ids.ids)],
            "date_from": self.date_from,
            "date_to": self.date_to,
            "location_id": self.location_id.id,
        }

    def _export(self, report_type):
        model = self.env["manufacturing.report"]
        report = model.create(self._prepare_manufacturing_report())
        return report.print_report(report_type)
