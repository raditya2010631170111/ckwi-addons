from odoo import models, fields, _
import xlwt
import locale
import datetime

class ReportGradingSummaryXLSX(models.AbstractModel):
    _name = 'report.jidoka_purchase.report_grading_summary_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        for obj in objects:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet('GL')
            sheet.set_column(0, 0, 5.1)
            sheet.set_column(1, 1, 25)
            sheet.set_column(2, 2, 11.30)
            sheet.set_column(3, 3, 6.3)
            sheet.set_column(6, 6, 5.1)
            sheet.set_column(7, 7, 20)
            sheet.set_column(8, 8, 5.1)
            sheet.set_column(9, 9, 20)
            locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
            bold_header = workbook.add_format({'bold':True,'align':'center','valign':'vcenter','underline':True})
            bold_bottom_header = workbook.add_format({'font_size':10,'bold':True,'align':'center','valign':'vcenter','underline':True})
            date_format = workbook.add_format({'num_format':'dd-MMM-yyyy','font_size':10})
            currency_body_format = workbook.add_format({'num_format':'[$Rp-421]#,##0.00','font_size':10,'align':'center','valign':'vcenter'})
            currency_header_format = workbook.add_format({'bold':True,'num_format':'[$Rp-421]#,##0.00','font_size':10,'align':'center','valign':'vcenter'})
            currency_header_format.set_bottom(1)
            currency_header_format.set_top(1)
            table_header = workbook.add_format({'bold':True,'align':'center','valign':'vcenter','text_wrap':True,'font_size':10})
            table_h2 = workbook.add_format({'bold':True,'align':'right','valign':'vcenter','text_wrap':True,'font_size':10})
            table_header.set_bottom(1)
            table_header.set_top(1)
            body_header = workbook.add_format({'align':'center','valign':'vcenter','text_wrap':True,'font_size':10})
            header = workbook.add_format({'font_size':10})

            note = workbook.add_format({
                'font_size': 10,
            })

            header_center = workbook.add_format({'font_size':10,'align':'center','valign':'vcenter'})
            sheet.write('A1', obj.env.company.name, header)
            sheet.merge_range('A3:J3', 'G R A D I N G  -  S U M M A R Y', bold_header)
            sheet.write('A6', 'No.', header)
            sheet.write('A7', 'Supplier', header)
            sheet.write('A8', 'Commence', header)
            sheet.write('A9', 'Species', header)
            sheet.write('A10', 'Shipping Marks', header)
            sheet.write('C6', '%s %s' %(': ',obj.name or ''), header)
            sheet.write('C7', '%s %s' %(': ',obj.partner_id.display_name or''), header)
            # sheet.write('C8', '%s %s' %(': ',obj.commence or ''), header)
            formatted_commence = obj.commence.strftime('%d %B %Y')
            sheet.write('C8', ': ' + formatted_commence, header)

            sheet.write('C9', '%s %s' %(': ',obj.species_id.name or ''), header)
            sheet.write('C10', '%s %s' %(': ',obj.shipping_marks or''), header)
            sheet.write('G6', 'Date', header)
            sheet.write('G7', 'Our Code', header)
            sheet.write('G8', 'Complete', header)
            sheet.write('G9', 'Grade', header)
            sheet.write('G10', 'End Tally', header)
            sheet.write('G11', 'Sertifikasi', header)

            formatted_date = obj.date.strftime('%d %B %Y')
            sheet.write('I6', ': ' + formatted_date, header)

            sheet.write('I7', ': ' + (obj.our_code or ''), header)

            formatted_complete_date = obj.complete_date.strftime('%d %B %Y')
            sheet.write('I8', ': ' + formatted_complete_date, header)

            sheet.write('I9', ': ' + (obj.grade or ''), header)

            formatted_end_tally = obj.end_tally.strftime('%d %B %Y')
            sheet.write('I10', ': ' + formatted_end_tally, header)
            # sheet.write('I6', '%s %s' %(': ',obj.date or''), date_format)
            # sheet.write('I7', '%s %s' %(': ',obj.our_code or ''),header)
            # sheet.write('I8', '%s %s' %(': ',obj.complete_date or ''), date_format)
            # sheet.write('I9', '%s %s' %(': ',obj.grade or ''), header)
            # sheet.write('I10', '%s %s' %(': ',obj.end_tally or ''), date_format)
            sheet.write('I11', '%s %s' %(': ',obj.certification_id.name or ''), header)

            sheet.write('A12', 'NO', table_header)
            sheet.write('B12', 'U K U R A N', table_header)
            sheet.write('C12', 'GRADE', table_header)
            sheet.write('D12', 'KELAS', table_header)
            sheet.write('E12', 'PCS', table_header)
            sheet.write('F12', 'M3 ', table_header)
            sheet.merge_range('G12:J12', 'TOTAL',table_header)
            row = 12
            count = 1
            total_pcs = total_kubikasi = 0
            for line in obj.grading_summary_line_ids:
                if line.product_name:
                    sheet.write(row,0,str(count),body_header)
                    sheet.write(row,1,line.product_name or '',body_header)
                    # sheet.write_string(row,3,'=',body_header)
                    # row = row + 1
                    count = count + 1
                master_hasil = ''
                if line.master_hasil:
                    master_hasil = dict(line._fields['master_hasil'].selection).get(line.master_hasil)
                sheet.write(row,3,line.wood_class_id.name or '',body_header)
                sheet.write_string(row,2,master_hasil,body_header)
                sheet.write(row,4,line.qty_pcs or '0',body_header)
                sheet.write(row,5,line.qty_kubikasi or '0',body_header)
                sheet.write_string(row,6,'x',body_header)
                sheet.write(row,7,line.price_unit or '0',currency_body_format)
                sheet.write_string(row,8,'=',body_header)
                sheet.write(row,9,line.price_subtotal or '0',currency_body_format)
                row = row + 1
                total_pcs = total_pcs + line.qty_pcs
                total_kubikasi = total_kubikasi + line.qty_kubikasi
            row = row + 1
            sheet.merge_range(row, 0, row , 2, 'TOTAL',table_header)
            sheet.write_string(row,3,'=',table_header)
            sheet.write(row,4,total_pcs,table_header)
            sheet.write(row,5,total_kubikasi,table_header)
            sheet.write(row,6,'',table_header)
            sheet.write(row,7,'',table_header)
            sheet.write_string(row,8,'=',table_header)
            sheet.write(row,9,obj.amount_total or '0',currency_header_format)

            
            # text = obj.information or ''
            # text_length = len(text)
            # row_start = row
            # row_end = row + 5 - max(0, (text_length // 50) - 1)

            # sheet.merge_range('C%s:J%s' % (row_start, row_end), text, header)

            row = row + 4
            #sheet.merge_range('C%s:J%s' % (row, row + 5), obj.information or '', header)
            information_lines = obj.information.splitlines() if obj.information else []
            equal_lines = obj.equal_symbol.splitlines() if obj.equal_symbol else []

            max_lines = max(len(information_lines), len(equal_lines))

            for i in range(max_lines):
                information = information_lines[i] if i < len(information_lines) else ""
                equal_symbol = equal_lines[i] if i < len(equal_lines) else ""

                if information:
                    sheet.write_string(row + i, 2, information, header)

                if equal_symbol:
                    sheet.write_string(row + i, 7, equal_symbol, header)

            row = row + len(information_lines)
            #row = row + 4
            sheet.write(row+2,2,'P.O No.', header)
            sheet.write(row+3,2,'TRUCK', header)
            sheet.write(row+4,2,'TURUN', header)
            sheet.write(row+5,2,'SKSHHK / NOTA', header)
            sheet.write(row+6,2,'DKHP', header)
            sheet.write(row+2,3,':', table_h2)
            sheet.write(row+3,3,':', table_h2)
            sheet.write(row+4,3,':', table_h2)
            sheet.write(row+5,3,':', table_h2)
            sheet.write(row+6,3,':', table_h2)
            sheet.write(row+1,4,obj.purchase_id.name or '', header)
            sheet.write(row+2,4,obj.truck or '', header)
            sheet.write(row+3,4,obj.turun or '', header)
            sheet.write(row+4,4,obj.nota or '', header)
            sheet.write(row+5,4,obj.dkhp or '', header)
            # add one line of blank space for boundary
            # sheet.write('', 0, 0, '')
            
            row = row + 8
            sheet.merge_range(row,0,row,1,'Mengetahui,', header_center)
            sheet.write(row,2,'Diperiksa,', header_center)
            sheet.merge_range(row,3,row,5,'Grader,', header_center)
            sheet.merge_range(row,6,row,7,'Dibuat,', header_center)
            sheet.merge_range(row,8,row,9,'Penjual,', header_center)
            row = row + 5
            sheet.merge_range(row,0,row,1,'INDRA K.', bold_bottom_header)
            sheet.write(row,2,'ENDRO', bold_bottom_header)
            sheet.merge_range(row,3,row,5,'TOKID', bold_bottom_header)
            sheet.merge_range(row,6,row,7,'TARI', bold_bottom_header)
            sheet.merge_range(row,8,row,9,obj.partner_id.display_name, bold_bottom_header)