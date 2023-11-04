# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    XLS_HEADERS,
)

_logger = logging.getLogger(__name__)


class ReportStockCardReportXlsx(models.AbstractModel):
    _name = "report.jidoka_manufacturing_report.manufacturing_report_xlsx"
    _description = "Stock Card Report XLSX"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, objects):
        sheet = workbook.add_worksheet('')

        text_title_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'bold': True,'text_wrap': True,
            'align': 'center'})
        text_header_style1 = workbook.add_format({'font_name': 'Arial', 'font_size': 8, 'text_wrap': True, 'align': 'center',
            'border':True})
        num_style = workbook.add_format({'num_format': '#,##0.0', 'left': 1, 'top': 1, 'right':1, 'bottom':1,
            'font_name': 'Arial', 'font_size': 8, 'align': 'center'})
        text_thead_style = workbook.add_format({'font_name': 'Arial', 'font_size': 10, 'text_wrap': True, 'align': 'center',
            'bg_color': '#92d050', 'border':True})
        
        periode = str(objects.date_from.strftime('%d %B %Y')) + ' - ' + str(objects.date_to.strftime('%d %B %Y'))
        location = 'Location ' + str(objects.location_id.display_name)
        sheet.merge_range(0, 0, 2, 6, 'Manufacturing Report Stock Move', text_title_style)
        sheet.merge_range(3, 0, 3, 6, location, text_title_style)
        sheet.merge_range(4, 0, 4, 6, periode, text_title_style)

        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 10)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 10)
        sheet.set_column('F:F', 10)
        sheet.set_column('G:G', 10)

        sheet.write_row(6, 0, ['ITEM'], text_thead_style)
        sheet.write_row(6, 1, ['MO'], text_thead_style)
        sheet.write_row(6, 2, ['PART'], text_thead_style)
        sheet.write_row(6, 3, ['JENIS KAYU'], text_thead_style)
        sheet.write_row(6, 4, ['IN'], text_thead_style)
        sheet.write_row(6, 5, ['OUT'], text_thead_style)
        sheet.write_row(6, 6, ['BALANCE'], text_thead_style)

        item_list = []
        mo_list = []
        part_list = []
        jenis_kayu_list = []
        in_list = []
        out_list = []
        balance_list = []
        for line in objects.results.filtered(lambda l: not l.is_initial):
            initial = objects._get_initial(objects.results.filtered(lambda l: l.cons_product_id == line.cons_product_id and l.is_initial))
            product_balance = initial
            product_balance = product_balance + line.product_in - line.product_out
            in_list.append(line.product_in)
            out_list.append(line.product_out)
            balance_list.append(product_balance)
            item_list.append(line.fg_product_id.display_name)
            mo_list.append(line.sale_id.display_name)
            part_list.append(line.cons_product_id.display_name)
            if line.cons_product_id.wood_kind_id:
                jenis_kayu_list.append(line.cons_product_id.wood_kind_id.display_name)
            if not line.cons_product_id.wood_kind_id:
                jenis_kayu_list.append('')


        row = 6
        row += 1
        sheet.write_column(row, 0, item_list, text_header_style1)
        sheet.write_column(row, 1, mo_list, text_header_style1)
        sheet.write_column(row, 2, part_list, text_header_style1)
        sheet.write_column(row, 3, jenis_kayu_list, text_header_style1)
        sheet.write_column(row, 4, in_list, num_style)
        sheet.write_column(row, 5, out_list, num_style)
        sheet.write_column(row, 6, balance_list, num_style)
        
