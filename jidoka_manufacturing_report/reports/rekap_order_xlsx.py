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
    _name = "report.jidoka_manufacturing_report.rekap_order_xlsx"
    _description = "Rekap Order Report XLSX"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, objects):
        sheet = workbook.add_worksheet('')

        text_title_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'bold': True,'text_wrap': True,
            'align': 'center'})
        text_header_style1 = workbook.add_format({'font_name': 'Arial', 'font_size': 8, 'text_wrap': True, 'align': 'center',
            'border':True})
        num_style = workbook.add_format({'num_format': '#,##0.00', 'left': 1, 'top': 1, 'right':1, 'bottom':1,
            'font_name': 'Arial', 'font_size': 8, 'align': 'center'})
        text_thead_style = workbook.add_format({'font_name': 'Arial', 'font_size': 10, 'text_wrap': True, 'align': 'center',
            'bg_color': '#92d050', 'border':True})
        
        periode = str(objects.date_from.strftime('%d %B %Y')) + ' - ' + str(objects.date_to.strftime('%d %B %Y'))
        location = 'Location ' + str(objects.location_id.display_name)
        sheet.merge_range(0, 0, 2, 9, 'Rencana Proses Produksi', text_title_style)
        sheet.merge_range(3, 0, 3, 9, location, text_title_style)
        sheet.merge_range(4, 0, 4, 9, periode, text_title_style)

        # filter = []
        # order_obj = self.env['stock.move']
        # rekap = order_obj.search(filter, order="date asc")

        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 10)
        # sheet.set_column('E:E', 10)
        # sheet.set_column('F:F', 10)
        # sheet.set_column('G:G', 10)
        # sheet.set_column('H:H', 10)
        # sheet.set_column('I:I', 10)
        # sheet.set_column('J:J', 10)
        # sheet.set_column('K:K', 10)
        # sheet.set_column('L:L', 10)
        # sheet.set_column('M:M', 10)
        sheet.set_column('O:O', 20)


        sheet.write_row(6, 0, ['PO'], text_thead_style)
        sheet.write_row(6, 1, ['ITEM'], text_thead_style)
        sheet.write_row(6, 2, ['COMPONENT'], text_thead_style)
        sheet.write_row(6, 3, ['QUANTITY SC'], text_thead_style)
        sheet.write_row(6, 4, ['TBL'], text_thead_style)
        sheet.write_row(6, 5, ['LBR'], text_thead_style)
        sheet.write_row(6, 6, ['PNJG'], text_thead_style)
        sheet.write_row(6, 7, ['PCS'], text_thead_style)
        # sheet.write_row(6, 8, ['1:1'], text_thead_style)
        sheet.write_row(6, 8, ['PERLU'], text_thead_style)
        sheet.write_row(6, 9, ['KURANG'], text_thead_style)
        sheet.write_row(6, 10, ['HASIL'], text_thead_style)
        # sheet.write_row(6, 12, ['KET'], text_thead_style)
        sheet.write_row(6, 11, ['BENTUK'], text_thead_style)
        sheet.write_row(6, 12, ['GRADE'], text_thead_style)
        # sheet.write_row(6, 15, ['PROSES'], text_thead_style)
        sheet.write_row(6, 13, ['WARNA'], text_thead_style)
        # sheet.write_row(6, 17, ['HASIL SET'], text_thead_style)
        # sheet.write_row(6, 18, ['Min Set'], text_thead_style)
        # sheet.write_row(6, 19, ['METER'], text_thead_style)
        # sheet.write_row(6, 20, ['M3'], text_thead_style)
        # sheet.write_row(6, 21, ['???'], text_thead_style)
        sheet.write_row(6, 14, ['BUYER'], text_thead_style)
        
        po_list = []
        item_list = []
        comp_list = []
        itemqty_list = []
        tbl_list = []
        lbr_list = []
        pnjg_list = []
        pcs_list = []
        perlu_list = []
        kurang_list = []
        hasil_list = []
        bentuk_list = []
        grade_list = []
        warna_list = []
        buyer_list = []
        for move in objects.results:
            po_list.append(move.sale_id.display_name)
            item_list.append(move.fg_product_id.display_name)
            comp_list.append(move.cons_product_id.display_name)
            itemqty_list.append(move.quantity_product_fg)
            tbl_list.append(move.size_tebal)
            lbr_list.append(move.size_lebar)
            pnjg_list.append(move.size_panjang)
            pcs_list.append(move.comp_quantity)

            perlu_list.append(move.perlu_quantity)
            kurang_list.append(move.kurang_quantity)
            hasil_list.append(move.comp_quantity_done)

            if move.cons_product_id.wood_shape_id:
                bentuk_list.append(move.cons_product_id.wood_shape_id.display_name)
            if not move.cons_product_id.wood_shape_id:
                bentuk_list.append('')

            if move.cons_product_id.wood_grade_id:
                grade_list.append(move.cons_product_id.wood_grade_id.display_name)
            if not move.cons_product_id.wood_grade_id:
                grade_list.append('')

            if move.cons_product_id.colour_id:
                warna_list.append(move.cons_product_id.colour_id.display_name)
            if not move.cons_product_id.colour_id:
                warna_list.append('')

            if move.sale_id.partner_id:
                buyer_list.append(move.sale_id.partner_id.display_name)
            if not move.sale_id.partner_id:
                buyer_list.append('')


        row = 6
        row += 1
        sheet.write_column(row, 0, po_list, text_header_style1)
        sheet.write_column(row, 1, item_list, text_header_style1)
        sheet.write_column(row, 2, comp_list, text_header_style1)
        sheet.write_column(row, 3, itemqty_list, text_header_style1)
        sheet.write_column(row, 4, tbl_list, text_header_style1)
        sheet.write_column(row, 5, lbr_list, text_header_style1)
        sheet.write_column(row, 6, pnjg_list, text_header_style1)
        sheet.write_column(row, 7, pcs_list, text_header_style1)
        sheet.write_column(row, 8, perlu_list, text_header_style1)
        sheet.write_column(row, 9, kurang_list, text_header_style1)
        sheet.write_column(row, 10, hasil_list, text_header_style1)
        sheet.write_column(row, 11, bentuk_list, text_header_style1)
        sheet.write_column(row, 12, grade_list, text_header_style1)
        sheet.write_column(row, 13, warna_list, text_header_style1)
        sheet.write_column(row, 14, buyer_list, text_header_style1)
        
