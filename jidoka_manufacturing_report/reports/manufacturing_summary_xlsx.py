# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models
import datetime

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    XLS_HEADERS,
)

_logger = logging.getLogger(__name__)


class ReportStockCardReportXlsx(models.AbstractModel):
    _name = "report.jidoka_manufacturing_report.manufacturing_summary_xlsx"
    _description = "Stock Card Report XLSX"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, objects):
        sheet = workbook.add_worksheet('')

        text_title_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'bold': True,'text_wrap': True,
            'align': 'center'})
        text_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'text_wrap': True, 'align': 'right',
            })
        text_buttom_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'text_wrap': True, 'align': 'right',
            'bg_color': '#4682b4'})
        currency_style = workbook.add_format({'num_format': '#,##0.00', 'left': 1, 'top': 1, 'right':1, 'bottom':1,
            'font_name': 'Arial', 'font_size': 6, 'align': 'right'})
        num_style = workbook.add_format({'num_format': '#,##0.00', 'left': 1, 'top': 1, 'right':1, 'bottom':1,
            'font_name': 'Arial', 'font_size': 6, 'align': 'left'})
        text_thead_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'text_wrap': True, 'align': 'center',
            'bg_color': '#4682b4', 'border':True})
        
        periode = str(objects.date_from.strftime('%d %B %Y')) + ' - ' + str(objects.date_to.strftime('%d %B %Y'))
        sheet.merge_range(0, 0, 2, 8, 'LAPORAN STOCK BARANG DEPT. PROCESSING (WIP ASSEMBLING SETENGAH JADI)', text_title_style)
        sheet.merge_range(3, 0, 3, 8, periode, text_title_style)
        date_from_str = objects.date_from.strftime('%d %B %Y')
        date_to_str = objects.date_to.strftime('%d %B %Y')
        date_from = datetime.datetime.strptime(date_from_str, '%d %B %Y')
        date_to = datetime.datetime.strptime(date_to_str, '%d %B %Y')
        domain = [
            ('date', '>=', date_from.strftime('%Y-%m-%d 00:00:00')),
            ('date', '<=', date_to.strftime('%Y-%m-%d 23:59:59')),
            ('location_id', '=', objects.location_id.id),
            ('state', '=', 'done')
        ]
        summary_obj = self.env['stock.move.line']
        summary = summary_obj.search(domain, order="date asc")

        len_item = "ITEM"
        awal_bulan_pcs = 'BALANCE AWAL BULAN (PCS)'
        awal_bulan_m3 = 'BALANCE AWAL BULAN (M3)'
        len_hasil_pcs = 'HASIL (PCS)'
        len_hasil_m3 = 'HASIL (M3)'
        len_kirim_pcs = 'KIRIM (PCS)'
        len_kirim_m3 = 'KIRIM (M3)'
        len_sisa_barang_pcs = 'SISA BARANG (PCS)'
        len_sisa_barang_m3 = 'SISA BARANG (M3)'
        
        item = len (len_item) + 6
        lebar_kolom_pcs = len(awal_bulan_pcs) + 6 
        lebar_kolom_m3 = len(awal_bulan_m3) + 6 
        hasil_pcs = len(len_hasil_pcs) + 6 
        hasil_m3 = len(len_hasil_m3) + 6 
        kirim_pcs = len(len_kirim_pcs) + 6 
        kirim_m3 = len(len_kirim_m3) + 6 
        sisa_barang_pcs = len(len_sisa_barang_pcs) + 6 
        sisa_barang_m3 = len(len_sisa_barang_m3) + 6 
        
        sheet.set_column('A:A', item)
        sheet.set_column('B:B', lebar_kolom_pcs)
        sheet.set_column('C:C', lebar_kolom_m3)
        sheet.set_column('D:D', hasil_pcs)
        sheet.set_column('E:E', hasil_m3)
        sheet.set_column('F:F', kirim_pcs)
        sheet.set_column('G:G', kirim_m3)
        sheet.set_column('H:H', sisa_barang_pcs)
        sheet.set_column('I:I', sisa_barang_m3)

        sheet.write_row(5, 0, [len_item], text_thead_style)
        sheet.write_row(5, 1, [awal_bulan_pcs], text_thead_style)
        sheet.write_row(5, 2, [awal_bulan_m3], text_thead_style)
        sheet.write_row(5, 3, [len_hasil_pcs], text_thead_style)
        sheet.write_row(5, 4, [len_hasil_m3], text_thead_style)
        sheet.write_row(5, 5, [len_kirim_pcs], text_thead_style)
        sheet.write_row(5, 6, [len_kirim_m3], text_thead_style)
        sheet.write_row(5, 7, [len_sisa_barang_pcs], text_thead_style)
        sheet.write_row(5, 8, [len_sisa_barang_m3], text_thead_style)

        product_list = []
        balance_awal_pcs_list = []
        balance_awal_m3_list = []
        in_product_pcs_list = []
        in_product_m3_list = []
        out_product_pcs_list = []
        out_product_m3_list = []
        sisa_barang_pcs_list = []
        sisa_barang_m3_list = []
        row = 6
        for line in objects.results.filtered(lambda l: not l.is_initial and l.product_id.uom_id.name.lower() in ["pcs", "m³"]):
            initial = objects._get_initial(objects.results.filtered(lambda l: l.product_id == line.product_id and l.is_initial))
            product_balance = initial
            product_balance = product_balance + line.product_in - line.product_out
            product_list.append(line.product_id.name)
            balance_awal_pcs_list.append(line.initial_balance if line.product_id.uom_id.name.lower() == "pcs" else 0)
            in_product_pcs_list.append(line.product_in if line.product_id.uom_id.name.lower() == "pcs" else 0)
            out_product_pcs_list.append(line.product_out if line.product_id.uom_id.name.lower() == "pcs" else 0)
            sisa_barang_pcs_list.append(product_balance if line.product_id.uom_id.name.lower() == "pcs" else 0)
            balance_awal_m3_list.append(line.initial_balance if line.product_id.uom_id.name.lower() == "m³" else 0)
            in_product_m3_list.append(line.product_in if line.product_id.uom_id.name.lower() == "m³" else 0)
            out_product_m3_list.append(line.product_out if line.product_id.uom_id.name.lower() == "m³" else 0)
            sisa_barang_m3_list.append(product_balance if line.product_id.uom_id.name.lower() == "m³" else 0)
            grand_total_balance_awal_pcs = sum(balance_awal_pcs_list)
            grand_total_balance_awal_m3 = sum (balance_awal_m3_list)
            grand_total_in_pcs = sum(in_product_pcs_list)
            grand_total_in_m3 = sum(in_product_m3_list)
            grand_total_out_pcs = sum(out_product_pcs_list)
            grand_total_out_m3 = sum(out_product_m3_list)
            grand_sisa_barang_pcs = sum(sisa_barang_pcs_list)
            grand_sisa_barang_m3 = sum(sisa_barang_m3_list)

            row += 1
            sheet.write(row, 0, line.product_id.name, text_style)
            sheet.write(row, 1, line.initial_balance if line.product_id.uom_id.name.lower() == "pcs" else 0, text_style)
            sheet.write(row, 2, line.initial_balance if line.product_id.uom_id.name.lower() == "m³" else 0, text_style)
            sheet.write(row, 3, line.product_in if line.product_id.uom_id.name.lower() == "pcs" else 0, text_style)
            sheet.write(row, 4, line.product_in if line.product_id.uom_id.name.lower() == "m³" else 0, text_style)
            sheet.write(row, 5, line.product_out if line.product_id.uom_id.name.lower() == "pcs" else 0, text_style)
            sheet.write(row, 6, line.product_out if line.product_id.uom_id.name.lower() == "m³" else 0, text_style)
            sheet.write(row, 7, product_balance if line.product_id.uom_id.name.lower() == "pcs" else 0, text_style)
            sheet.write(row, 8, product_balance if line.product_id.uom_id.name.lower() == "m³" else 0, text_style)

        row += 1
        sheet.write(row, 0, 'GRAND TOTAL', text_thead_style)
        sheet.write(row, 1, grand_total_balance_awal_pcs, text_thead_style)
        sheet.write(row, 2, grand_total_balance_awal_m3, text_thead_style)
        sheet.write(row, 3, grand_total_in_pcs, text_thead_style)
        sheet.write(row, 4, grand_total_in_m3, text_thead_style)
        sheet.write(row, 5, grand_total_out_pcs, text_thead_style)
        sheet.write(row, 6, grand_total_out_m3, text_thead_style)
        sheet.write(row, 7, grand_sisa_barang_pcs, text_thead_style)
        sheet.write(row, 8, grand_sisa_barang_m3, text_thead_style)

        # sheet.write(row, 0, 'GRAND TOTAL', text_thead_style)
        # sheet.write(row, 1, balance_total_pcs, text_buttom_style)
        # sheet.write(row, 2, "{:.2f}".format(balance_total_m3), text_buttom_style)
        # sheet.write(row, 3, incoming_total_pcs, text_buttom_style)
        # sheet.write(row, 4, "{:.2f}".format(incoming_total_m3), text_buttom_style)
        # sheet.write(row, 5, outgoing_total_pcs, text_buttom_style)
        # sheet.write(row, 6, "{:.2f}".format(outgoing_total_m3), text_buttom_style)
        # sheet.write(row, 7, sisa_barang_total_pcs, text_buttom_style)
        # sheet.write(row, 8, "{:.2f}".format(sisa_barang_total_m3), text_buttom_style)
