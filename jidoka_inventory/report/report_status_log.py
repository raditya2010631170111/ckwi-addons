from odoo import models, fields, _


class ReportStatusLogXLSX(models.AbstractModel):
    _name = 'report.jidoka_inventory.report_status_log_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, objects):
        KODE_BULAN = ['=','A','B','C','D','E','F','G','H','I','J','K','L']
        sheet = workbook.add_worksheet('GL')
        sheet.set_column(0, 0, 12)
        sheet.set_column(1, 2, 8)
        sheet.set_column(3, 3, 25)
        sheet.set_column(4, 4, 10)
        sheet.set_column(5, 6, 5)
        sheet.set_column(7, 7, 20)
        sheet.set_column(8, 9, 5)
        sheet.set_column(10, 10, 20)
        sheet.set_column(11, 13, 10)
        sheet.set_row(0, 35)
        table_header = workbook.add_format({'bold':True,'border':1,'align':'center','valign':'vcenter','text_wrap':True,'font_size':10})
        table_body = workbook.add_format({'align':'center','valign':'vcenter','text_wrap':True,'font_size':10})
        date_format = workbook.add_format({'num_format':'dd-MMM-yyyy','align':'center','valign':'vcenter','font_size':10})
        sheet.write('A1','Tgl Masuk',table_header)
        sheet.write('B1','BULAN',table_header)
        sheet.write('C1','KODE BULAN',table_header)
        sheet.write('D1','No. Nota',table_header)
        sheet.write('E1','No. Mobil',table_header)
        sheet.write('F1','Surat Jalan (PCS)',table_header)
        sheet.write('G1','Surat Jalan (M3)',table_header)
        sheet.write('H1','Supplier',table_header)
        sheet.write('I1','KODE SUPPLIER',table_header)
        sheet.write('J1','No. Kedatangan',table_header)
        sheet.write('K1','Lokasi (Master Lokasi + Fee + Ongkir)',table_header)
        sheet.write('L1','Kode',table_header)
        sheet.write('M1','Jenis Kayu',table_header)
        sheet.write('N1','Sertifikasi (FSC/Non FSC)',table_header)
        row = 1 
        for obj in objects:
            sheet.write(row,0,obj.create_date or '',date_format)
            sheet.write(row,1,obj.create_date.month or '', table_body)
            sheet.write(row,2,KODE_BULAN[obj.create_date.month] or '', table_body)
            sheet.write(row,3,obj.nota or '', table_body)
            sheet.write(row,4,obj.plat_no or '', table_body)
            sheet.write(row,5,obj.qty_nota or '', table_body)
            sheet.write(row,6,obj.cubic_nota or '', table_body)
            sheet.write(row,7,obj.partner_id.display_name or '', table_body)
            sheet.write(row,8,obj.partner_id.supplier_code_id.code or '', table_body)
            sheet.write(row,9,obj.depart_no or '', table_body)
            sheet.write(row,10,obj.fee_location_id.name or '', table_body)
            sheet.write(row,11,_('%s%s%s')%(KODE_BULAN[obj.create_date.month] or '-',obj.partner_id.supplier_code_id.code or '-',obj.depart_no or '-'), table_body)
            sheet.write(row,12,obj.wood_type or '', table_body)
            sheet.write(row,13,obj.certification_id.name or '', table_body)
            row = row + 1