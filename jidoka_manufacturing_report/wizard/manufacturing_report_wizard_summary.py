from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class ManufacturingReportWizardSummary(models.TransientModel):
    _name = "manufacturing.report.wizard.summary"
    _description = "Manufacturing Report Wizard Summary"

    date_range_id = fields.Many2one(comodel_name="date.range", string="Period")
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    location_id = fields.Many2one(comodel_name='stock.location', string='Location')
    product_ids = fields.Many2many(comodel_name="product.product")

    @api.onchange("date_range_id")
    def _onchange_date_range_id(self):
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end


    def button_export_html_summary(self):
        self.ensure_one()
        action = self.env.ref("jidoka_manufacturing_report.action_manufacturing_summary_html")
        vals = action.sudo().read()[0]
        context = vals.get("context", {})
        if context:
            context = safe_eval(context)
        model = self.env["manufacturing.summary.report"]
        report = model.create(self._prepare_manufacturing_report())
        context["active_id"] = report.id
        context["active_ids"] = report.ids
        vals["context"] = context
        return vals
    

    def button_export_pdf(self):
        self.ensure_one()
        report_type = "qweb-pdf"
        return self._export(report_type)

    def button_export_xlsx(self):
        self.ensure_one()
        report_type = "xlsx"
        return self._export(report_type)

    def _prepare_manufacturing_report(self):
        self.ensure_one()
        return {
            "date_from": self.date_from,
            "date_to": self.date_to,
            "product_ids": [(6, 0, self.product_ids.ids)],
            "location_id": self.location_id.id,
        }

    def _export(self, report_type):
        model = self.env["manufacturing.summary.report"]
        report = model.create(self._prepare_manufacturing_report())
        return report.print_report(report_type)
