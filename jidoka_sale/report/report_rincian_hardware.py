from odoo import models, fields, _


class ReportRincianHardwareXLSX(models.AbstractModel):
    _name = 'report.jidoka_sale.report_rincian_hardware_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        for obj in objects:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet('PERINCIAN HARDWARES & ASESORIS')
            sheet.set_column(0, 0, 5)
            sheet.set_column(1, 1, 20)
            sheet.set_column(3, 3, 20)
            sheet.set_column(4, 7, 5)
            sheet.set_column(8, 8, 15)
            sheet.set_row(4, 25)
            bold_header = workbook.add_format({'bold':True,'align':'center','valign':'vcenter'})
            bold_header_right = workbook.add_format({'bold':True,'align':'right','valign':'vcenter'})
            date_format = workbook.add_format({'num_format':'dd-MMM-yyyy','bold':True})
            table_header = workbook.add_format({'bold':True,'border':1,'align':'center','valign':'vcenter'})
            body = workbook.add_format({'border':1,'align':'center','valign':'vcenter'})
            border_top = workbook.add_format({'align':'center','valign':'vcenter'})
            border_top.set_top(1)
            border_top_right = workbook.add_format({'align':'center','valign':'vcenter'})
            border_top_right.set_top(1)
            border_top_right.set_right(1)
            border_right = workbook.add_format({'align':'center','valign':'vcenter'})
            border_right.set_right(1)
            border_bot = workbook.add_format({'align':'center','valign':'vcenter'})
            border_bot.set_bottom(1)
            border_bot_right = workbook.add_format({'align':'center','valign':'vcenter'})
            border_bot_right.set_bottom(1)
            border_bot_right.set_right(1)
            sheet.merge_range('B1:D1', obj.env.company.name, bold_header)
            sheet.merge_range('H2:I2',fields.Date.today(),date_format)
            sheet.merge_range('B3:D3', 'PERINCIAN HARDWARES & ASESORIS', bold_header)
            sheet.write('B4', 'ITEM No.', bold_header_right)
            sheet.write('A5', 'No', table_header)
            sheet.write('B5', 'Nama Komponen', table_header)
            sheet.write('C5', 'Kode', table_header)
            sheet.write('D5', 'Ukuran', table_header)
            sheet.write('E5', 'Ttl', table_header)
            sheet.write('F5', 'Pro', table_header)
            sheet.write('G5', 'Fin', table_header)
            sheet.write('H5', 'Bks', table_header)
            sheet.write('I5', 'Gambar', table_header)
            idx = 5
            for line in range(1,20):
                sheet.write(idx,0,'',body)
                sheet.write(idx,1,'',body)
                sheet.write(idx,2,'',body)
                sheet.write(idx,3,'',body)
                sheet.write(idx,4,'',body)
                sheet.write(idx,5,'',body)
                sheet.write(idx,6,'',body)
                sheet.write(idx,7,'',body)
                sheet.write(idx,8,'',body)
                idx = idx + 1

            idx = idx + 2
            for line in range(1,16):
                if line <= 1 :
                    sheet.write(idx,0,'',border_top)
                    sheet.write(idx,1,'',border_top)
                    sheet.write(idx,2,'',border_top)
                    sheet.write(idx,3,'',border_top)
                    sheet.write(idx,4,'',border_top)
                    sheet.write(idx,5,'',border_top)
                    sheet.write(idx,6,'',border_top)
                    sheet.write(idx,7,'',border_top)
                    sheet.write(idx,8,'',border_top_right)
                    idx = idx + 1
                else:
                    sheet.write(idx,0,'')
                    sheet.write(idx,1,'')
                    sheet.write(idx,2,'')
                    sheet.write(idx,3,'')
                    sheet.write(idx,4,'')
                    sheet.write(idx,5,'')
                    sheet.write(idx,6,'')
                    sheet.write(idx,7,'')
                    sheet.write(idx,8,'',border_right)
                    idx = idx + 1
        
            sheet.write(idx,1,'Department')
            sheet.write(idx+1,1,'R & D')
            sheet.write(idx,4,'R & D')
            sheet.write(idx+3,0,'',border_bot)
            sheet.write(idx+3,1,'(...............)',border_bot)
            sheet.write(idx+3,2,'',border_bot)
            sheet.write(idx+3,3,'',border_bot)
            sheet.write(idx+3,4,'(...............)')
            sheet.write(idx+3,5,'',border_bot)
            sheet.write(idx+3,6,'',border_bot)
            sheet.write(idx+3,7,'',border_bot)
            sheet.write(idx,8,'',border_right)
            sheet.write(idx+1,8,'',border_right)
            sheet.write(idx+2,8,'',border_right)
            sheet.write(idx+3,8,'',border_bot_right)