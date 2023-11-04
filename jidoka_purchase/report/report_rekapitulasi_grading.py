from odoo import models, fields, _
from datetime import datetime


class ReportRekapitulasiGradingXLSX(models.AbstractModel):
    _name = 'report.jidoka_purchase.report_rekapitulasi_grading_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        for obj in objects:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet('GL')
            sheet.set_column(0, 0, 30)
            sheet.set_column(1, 6, 14)
            header_top = workbook.add_format({'bold':True,'align':'center','valign':'vcenter','font_size':14})
            sub_header_top = workbook.add_format({'bold':True,'align':'center','valign':'vcenter','font_size':12})
            header = workbook.add_format({'font_size':10})
            header_center = workbook.add_format({'font_size':10,'align':'center','valign':'vcenter'})
            header_center_border_top = workbook.add_format({'font_size':10,'align':'center','valign':'vcenter'})
            header_center_border_top.set_top(1)
            bold_bottom_header = workbook.add_format({'font_size':10,'bold':True,'align':'center','valign':'vcenter','underline':True})
            table_header = workbook.add_format({'border':1,'bold':True,'align':'center','valign':'vcenter','text_wrap':True,'font_size':10})
            table_body = workbook.add_format({'border':1,'align':'center','valign':'vcenter','text_wrap':True,'font_size':10})
            sheet.merge_range('A1:G1',obj.env.company.name, header_top)
            sheet.merge_range('A3:G3','REKAPITULASI PENERIMAAN BALOK JATI', sub_header_top)
            sheet.merge_range('A4:G4','NO. : ' + obj.name, sub_header_top)
            sheet.write('A6', 'Supplier', header)
            # sheet.write('A7', 'TIBA', header)
            # sheet.write('A8', 'NO. MOBIL', header)
            # sheet.write('A9', 'FA - KO / NOTA ANGKUTAN', header)
            sheet.write('A7', 'P.O', header)
            sheet.write('B6', '%s %s' %(': ',obj.partner_id.display_name or ''), header)
            # sheet.write('B7', '%s %s' %(': ',obj.arrival_date or''), header)
            # sheet.write('B8', '%s %s' %(': ',obj.plat_no or ''), header)
            # sheet.write('B9', '%s %s' %(': ',obj.nota or ''), header)
            sheet.write('B7', '%s %s' %(': ',obj.purchase_id.name or''), header)
            sheet.merge_range('A9:A11', 'UKURAN INVOICE \n (LUAS PENAMPANG)',table_header)
            sheet.merge_range('B9:C10', 'BAGUS',table_header)
            sheet.merge_range('D9:E10', 'AFKIR (BUSUK)',table_header)
            sheet.merge_range('F9:G10', 'TOTAL',table_header)
            sheet.write('B11', 'PCS',table_header)
            sheet.write('C11', 'Mᵌ',table_header)
            sheet.write('D11', 'PCS',table_header)
            sheet.write('E11', 'Mᵌ',table_header)
            sheet.write('F11', 'PCS',table_header)
            sheet.write('G11', 'Mᵌ',table_header)
            row = 11
            sum_good_pcs = sum_good_cubic = sum_afkir_pcs = sum_afkir_cubic = sum_total_pcs = sum_total_cubic = 0
            for line in obj.line_ids:
                sheet.write(row,0,line.product_id.name or '',table_body)
                sheet.write(row,1,line.good_pcs or '0',table_body)
                sheet.write(row,2,line.good_cubic or '0',table_body)
                sheet.write(row,3,line.afkir_pcs or '0',table_body)
                sheet.write(row,4,line.afkir_cubic or '0',table_body)
                sheet.write(row,5,line.total_pcs or '0',table_body)
                sheet.write(row,6,line.total_cubic or '0',table_body)
                row = row + 1
                sum_good_pcs = sum_good_pcs + line.good_pcs
                sum_good_cubic = sum_good_cubic + line.good_cubic
                sum_afkir_pcs = sum_afkir_pcs + line.afkir_pcs
                sum_afkir_cubic = sum_afkir_cubic + line.afkir_cubic
                sum_total_pcs = sum_total_pcs + line.total_pcs
                sum_total_cubic = sum_total_cubic + line.total_cubic
            sheet.write(row,0, 'TOTAL',table_header)
            sheet.write(row,1,sum_good_pcs or '0',table_header)
            sheet.write(row,2,sum_good_cubic or '0',table_header)
            sheet.write(row,3,sum_afkir_pcs or '0',table_header)
            sheet.write(row,4,sum_afkir_cubic or '0',table_header)
            sheet.write(row,5,sum_total_pcs or '0',table_header)
            sheet.write(row,6,sum_total_cubic or '0',table_header)
            row = row + 2
            sheet.write(row,0,'Keterangan',header)
            sheet.write(row,1,':',header)
            sheet.merge_range(row+1, 0, row+3,2, obj.notes,header)
            sheet.write(row+5,0,'Karawang, ' + str(datetime.now().strftime("%d %B %Y")),header)
            row = row + 7
            sheet.write(row,0,'Mengetahui,', header_center)
            sheet.write(row,1,'Diperiksa', header_center)
            sheet.merge_range(row,2,row,3,'Dibuat,', header_center)
            sheet.write(row,4,'QC,', header_center)
            sheet.merge_range(row,5,row,6,'Menyetujui', header_center)
            row = row + 4
            sheet.write(row,0,'INDRA K.,', bold_bottom_header)
            sheet.write(row,1,'ENDRO', bold_bottom_header)
            sheet.merge_range(row,2,row,3,'TARI,', bold_bottom_header)
            sheet.write(row,4,'ENTIS R.,', bold_bottom_header)
            sheet.merge_range(row,5,row,6,obj.partner_id.display_name, bold_bottom_header)
            sheet.merge_range(row+2,0,row+2,6, 'Jalan Raya Kosambi Cimahi Km. 4, Desa Cimahi, Kecamatan Klari', header_center_border_top)
            sheet.merge_range(row+3,0,row+3,6, 'Karawang 41371 - Jawa Barat', header_center)
            sheet.merge_range(row+4,0,row+4,6, 'Telp. (62) 0267 - 434870, 435683, 436366 Fax. (62) 0267 - 436373', header_center)