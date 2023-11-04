# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import content_disposition, request
import io
import xlsxwriter
    


class InvoiceExcelReportController(http.Controller):
    @http.route([
        '/account/excel_report/<model("invoice.report"):wizard>',
    ], type='http', auth="user", csrf=False)
    def get_invoice_excel_report(self,wizard=None,**args):
        
        response = request.make_response(
                    None,
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition', content_disposition('Invoice Report in Excel Format' + '.xlsx'))
                    ]
                )

        # create workbook object from xlsxwriter library
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # create some style to set up the font type, the font size, the border, and the aligment
        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 14, 'bold': True, 'align': 'center', 'valign': 'vcenter'})
        header_style = workbook.add_format({'font_name': 'Times', 'bold': True, 'font_size': 12, 'bg_color': '#90d05a','align': 'center', 'valign': 'vcenter'})
        text_style = workbook.add_format({'font_name': 'Times',})
        number_style = workbook.add_format({'font_name': 'Times',})

        for journal in wizard.journal_id:
            sheet = workbook.add_worksheet(journal.name)
            sheet.set_landscape()
            sheet.set_paper(9)
            sheet.set_margins(0.5,0.5,0.5,0.5)

            sheet.set_column('A:A', 5)
            sheet.set_column('B:E', 15)
            sheet.set_row(0, 30)

            sheet.merge_range('A1:U1', 'Invoice Report in Excel Format', title_style)

            sheet.merge_range('A2:A3', 'Masa', header_style)
            sheet.merge_range('B2:B3', 'No.', header_style)
            sheet.merge_range('C2:D2', 'PEB', header_style)
            sheet.merge_range('E2:F2', 'Invoice', header_style)
            sheet.merge_range('G2:H2', 'B/L', header_style)
            sheet.merge_range('I2:J2', 'Pembeli', header_style)
            sheet.merge_range('K2:L2', 'Nilai', header_style)
            sheet.merge_range('M2:M3', 'Kurs', header_style)
            sheet.merge_range('N2:N3', 'Nilai', header_style)
            sheet.merge_range('O2:O3', 'Uraian Barang', header_style)
            sheet.merge_range('P2:P3', 'Qty', header_style)
            sheet.merge_range('Q2:Q3', 'Payment Term', header_style)
            sheet.merge_range('R2:U2', 'Pembayaran', header_style)
            sheet.write('C3', 'Nomor', header_style)
            sheet.write('D3', 'Tanggal', header_style)
            sheet.write('E3', 'Nomor', header_style)
            sheet.write('F3', 'Tanggal', header_style)
            sheet.write('G3', 'Nomor', header_style)
            sheet.write('H3', 'Tanggal', header_style)
            sheet.write('I3', 'Nama', header_style)
            sheet.write('J3', 'Negara', header_style)
            sheet.write('K3', 'Jumlah', header_style)
            sheet.write('L3', 'Currency', header_style)
            sheet.write('R3', "Tanggal ", header_style)
            sheet.write('S3', "No. Bukti ", header_style)
            sheet.write('T3', "Bank ", header_style)
            sheet.write('U3', "Jumlah ", header_style)

            row = 3
            number = 1
            invoices = request.env['account.move'].search([('journal_id','=',journal.id), ('invoice_date_due','>=', wizard.start_date), ('invoice_date_due','<=', wizard.end_date),('state','=','posted')])
            for inv in invoices:
                # the report content
                sheet.write(row, 0, 'none', text_style)
                sheet.write(row, 1, number, text_style)
                sheet.write(row, 2, inv.peb_no, text_style)
                sheet.write(row, 3, inv.peb_date, text_style)
                sheet.write(row, 4, inv.name, text_style)
                sheet.write(row, 5, str(inv.invoice_date), text_style)
                sheet.write(row, 6, 'none', text_style)
                sheet.write(row, 7, 'none', text_style)
                sheet.write(row, 8, inv.partner_id.name, text_style)
                sheet.write(row, 9, inv.company_id.country_id.name, text_style)
                sheet.write(row, 10, inv.amount_total, text_style)
                sheet.write(row, 11, inv.currency_id.name, text_style)
                sheet.write(row, 12, 'none', text_style)
                sheet.write(row, 13, inv.amount_total, number_style)
                sheet.write(row, 14, inv.tax_invoice, text_style)

                sheet.write(row, 16, inv.invoice_payment_term_id.name, text_style)
                sheet.write(row, 17, str(inv.date), text_style)
                sheet.write(row, 18, inv.voucher_name, text_style)
                sheet.write(row, 19, inv.bank_name, text_style)
                sheet.write(row, 20, inv.amount_total, text_style)
                # print("BANK-================>", inv.res.partner_bank_id.name)
                linesinv = inv['invoice_line_ids']
                print("line_ids =============>>> ", linesinv)
                for lines in linesinv:

                    sheet.write(row, 14, lines.name, text_style)
                    sheet.write(row, 15, lines.quantity, text_style)
                    row += 1

                row += 1
                number += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

        return response