# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    XLS_HEADERS,
)

_logger = logging.getLogger(__name__)


class ReportRekapGudangReportXlsx(models.AbstractModel):
    _name = "report.jidoka_manufacturing_report.rekap_gudang_report_xlsx"
    _description = "Rekap Gudang Report XLSX"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, objects):
        sheet = workbook.add_worksheet('')
        
        text_title_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'bold': True,'text_wrap': True,
            'align': 'center'})
        text_header_style = workbook.add_format({'font_name': 'Arial', 'font_size': 10, 'text_wrap': True, 'align': 'Center',
            'border':True})
        num_style = workbook.add_format({'num_format': '#,##0.0', 'left': 1, 'top': 1, 'right':1, 'bottom':1,
            'font_name': 'Arial', 'font_size': 8, 'align': 'center'})
        text_thead_style = workbook.add_format({'font_name': 'Arial', 'font_size': 8, 'text_wrap': True, 'align': 'center',
            'bg_color': '#B0E0E6', 'border':True,'valign': 'vcenter', 'bold': True})
        text_thead_style2 = workbook.add_format({'font_name': 'Arial', 'font_size': 8, 'text_wrap': True, 'align': 'center',
            'bg_color': 'yellow', 'border':True,'valign': 'vcenter', 'bold': True})
            
        periode = str(objects.date_from.strftime('%d %B %Y')) + ' - ' + str(objects.date_to.strftime('%d %B %Y'))
        location = 'Location ' + str(objects.location_id.display_name)
        sheet.merge_range(0, 0, 2, 8, 'Report Rekap Gudang', text_title_style)
        sheet.merge_range(3, 0, 3, 8, location, text_title_style)
        sheet.merge_range(4, 0, 4, 8, periode, text_title_style)
        
        sheet.set_column('A:A', 8.5)
        sheet.set_column('B:B', 6.2)
        sheet.set_column('C:C', 13)
        sheet.set_column('D:D', 10.7)
        sheet.set_column('E:E', 9.3)
        sheet.set_column('F:F', 6.6)
        sheet.set_column('G:G', 8.1)
        sheet.set_column('H:H', 9.1)
        sheet.set_column('I:I', 9.7)
        
        sheet.write_row(6, 0, ['TANGGAL TRANSAKSI'], text_thead_style2)
        # sheet.write_row(6, 1, ['ITEM'], text_thead_style2)
        sheet.write_row(6, 1, ['KOMPONEN'], text_thead_style2)
        sheet.write_row(6, 2, ['UNIT OF MEASURE'], text_thead_style)
        sheet.write_row(6, 3, ['UKURAN'], text_thead_style)
        sheet.write_row(6, 4, ['JENIS KAYU'], text_thead_style)
        sheet.write_row(6, 5, ['INCOMING'], text_thead_style)
        sheet.write_row(6, 6, ['OUTGOING'], text_thead_style)
        sheet.write_row(6, 7, ['STOCK AKHIR'], text_thead_style)
            
        date_list = []
        item_list = []
        part_list = []
        uom_list = []
        size_panjang_list = []
        size_lebar_list = []
        size_tebal_list = []
        jenis_kayu_list = []
        in_list = []
        out_list = []
        size_list = []
        balance_list = []
        for line in objects.results.filtered(lambda l: not l.is_initial):
            initial = objects._get_initial(objects.results.filtered(lambda l: l.product_id == line.product_id and l.is_initial))
            product_balance = initial
            product_balance = product_balance + line.product_in - line.product_out
            in_list.append(line.product_in)
            out_list.append(line.product_out)
            date_list.append(str(line.date.strftime('%d-%b-%y')))
            balance_list.append(product_balance)
            # item_list.append(line.product_id.display_name)
            part_list.append(line.product_id.display_name)
            uom_list.append(line.product_uom_id.display_name)
            size_panjang_list.append(line.size_panjang)
            size_lebar_list.append(line.size_lebar)
            size_tebal_list.append(line.size_tebal)
            for i in range(len(size_panjang_list)):
                size = f"{size_panjang_list[i]} x {size_lebar_list[i]} x {size_tebal_list[i]}"
                size_list.append(size)
            if line.product_id.wood_kind_id:
                jenis_kayu_list.append(line.product_id.wood_kind_id.display_name)
            if not line.product_id.wood_kind_id:
                jenis_kayu_list.append('')
                

        row = 6
        row += 1
        sheet.write_column(row, 0, date_list,text_header_style)
        # sheet.write_column(row, 1, item_list, text_header_style)
        sheet.write_column(row, 1, part_list, text_header_style)
        sheet.write_column(row, 2, uom_list,text_header_style)
        sheet.write_column(row, 3, size_list,text_header_style) 
        sheet.write_column(row, 4, jenis_kayu_list,text_header_style)
        sheet.write_column(row, 5, in_list,num_style)
        sheet.write_column(row, 6, out_list,num_style)
        sheet.write_column(row, 7, balance_list,num_style)
        
