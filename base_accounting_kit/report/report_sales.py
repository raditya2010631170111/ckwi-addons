from odoo import models, fields, _

class ReportHasilTesInternalExternalXLSX(models.AbstractModel):
    _name = 'report.base_accounting_kit.sample_costumer_invoice_local_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        for obj in objects:
            start_date = obj.start_date
            end_date = obj.end_date
            filter = []
            account_obj = self.env['account.move']

            if obj.type == 'penjualan_local':
                filter.append(('partner_id.is_local', '=', True))
                filter.append(('move_type', '=', 'out_invoice'))
            elif obj.type == 'penjualan_export':
                filter.append(('partner_id.is_local', '=', False))
                filter.append(('move_type', '=', 'out_invoice'))
            filter.append(('date', '>=', start_date))
            filter.append(('date', '<=', end_date))
            account = account_obj.search(filter, order="date asc")
			
            if obj.type == 'penjualan_local':
                report_name = 'Customer Invoice Local'
                sheet = workbook.add_worksheet(report_name[:31])
                bold_header = workbook.add_format({'border':1,'align':'center','valign':'vcenter','bold':True})
                table_header = workbook.add_format({'border':1,'align':'center','valign':'vcenter','text_wrap':True,'bg_color':'#66ff66','font_size':10,'bold':True})
                table_header.set_pattern(1)  # Set pattern to solid fill
                body = workbook.add_format({'border':1,'font_size':10})
                body2 = workbook.add_format({'border':1,'font_size':10,'align':'center'})
                body3 = workbook.add_format({'border':1,'font_size':10,'align':'right'})
                sheet.set_column(1, 1, 6)
                sheet.set_column(2, 2, 35)
                sheet.set_column(3, 3, 15)
                sheet.set_column(4, 4, 15)
                sheet.set_column(6, 6, 35)
                sheet.set_column(10, 10, 10)
                sheet.set_column(13, 13, 15)
                sheet.set_column(14, 14, 15)
            
                sheet.merge_range('B2:E4','PENJUALAN LOCAL',bold_header)
                sheet.merge_range('A6:A7','Masa',table_header)
                sheet.merge_range('B6:B7','NO',table_header)
                sheet.merge_range('C6:C7','NAMA PKP PEMBELI BKP/JKP',table_header)
                sheet.merge_range('D6:D7','NPWP',table_header)
                sheet.merge_range('E6:F6','FAKTUR PAJAK',table_header)
                sheet.write('E7','NOMOR',table_header)
                sheet.write('F7','TANGGAL',table_header)
                sheet.merge_range('G6:H6','BKP/JKP',table_header)
                sheet.write('G7','Nama BKP/JKP',table_header)
                sheet.write('H7','Qty',table_header)
                sheet.merge_range('I6:K6','DPP',table_header)
                sheet.write('I7','NILAI',table_header)
                sheet.write('J7','Kurs KMK',table_header)
                sheet.write('K7','DPP (Rp)',table_header)
                sheet.merge_range('L6:L7','PPN',table_header)
                sheet.merge_range('M6:M7','Total',table_header)
                sheet.merge_range('N6:Q6','PELUNASAN',table_header)
                sheet.write('N7','Tanggal Byr',table_header)
                sheet.write('O7','No. Dokumen',table_header)
                sheet.write('P7','Bank',table_header)
                sheet.write('Q7','Jumlah',table_header)
                
                row = 7
                no = 0
                for acc in account:	
                    no+=1	
                    sheet.write(row,0,acc.date.strftime("%B"),body2)
                    sheet.write(row,1,no,body2)
                    if acc.partner_id.name:
                        sheet.write(row,2,acc.partner_id.name,body)
                    elif acc.partner_id.parent_id.name and acc.partner_id.name:
                        sheet.write(row,2, f"{acc.partner_id.parent_id.name}, {acc.partner_id.name}",body)
                    elif acc.partner_id.parent_id.name and acc.partner_id.type:
                        sheet.write(row,2, f"{acc.partner_id.parent_id.name}, {acc.partner_id.type}",body)
                    sheet.write(row,3,acc.partner_id.vat,body2)
                    sheet.write(row,4,acc.l10n_id_tax_number if acc.l10n_id_tax_number else "",body)
                    sheet.write(row,5,acc.invoice_date.strftime(("%Y-%m-%d")) if acc.invoice_date else "",body2)
                    sheet.write(row,9,'',body3)
                    sheet.write(row,10,acc.amount_untaxed,body3)
                    taxed = acc.amount_total - acc.amount_untaxed
                    sheet.write(row,11,taxed,body3)
                    sheet.write(row,12,acc.amount_total,body3)
                    sheet.write(row,13,str(acc.account_payment_id.date),body2)
                    sheet.write(row,14,acc.account_payment_id.name,body)
                    sheet.write(row,16,acc.account_payment_id.amount,body3)
                    for bank in acc.partner_bank_id:
                        if bank.bank_id:
                            sheet.write(row,15,bank.bank_id.name,body)
                        else:
                            sheet.write(row,15,acc.bank_name if acc.bank_name else "",body)
                    for inv in acc.invoice_line_ids:
                        sheet.write(row,6,inv.name,body)
                        sheet.write(row,7,inv.quantity,body3)
                        sheet.write(row,8,inv.price_unit,body3) 
                        row += 1
                    
            elif obj.type == 'penjualan_export':
                report_name = 'Laporan Export'
                sheet = workbook.add_worksheet(report_name[:31])
                sheet.set_column(7, 14, 12)
                sheet.set_column(1, 1, 6)
                sheet.set_column(4, 4, 20)
                sheet.set_column(6, 6, 20)
                sheet.set_column(8, 8, 35)
                sheet.set_column(13, 13, 15)
                sheet.set_column(14, 14, 50)
                bold_header = workbook.add_format({'bold':True,'align':'center','valign':'vcenter'})
                table_header = workbook.add_format({'border':1,'align':'center','valign':'vcenter','text_wrap':True,'bg_color':'#63b76c','font_size':10,'bold':True})
                table_header.set_pattern(1)  # Set pattern to solid fill
                body = workbook.add_format({'border':1,'font_size':10,'align':'center','valign':'vcenter'})
                body2 = workbook.add_format({'border':1,'font_size':10,'valign':'vcenter'})
                
                sheet.write('A1','Ekspor',bold_header)
                sheet.merge_range('A3:A4','Masa',table_header)
                sheet.merge_range('B3:B4','NO',table_header)
                sheet.merge_range('C3:D3','PEB',table_header)
                sheet.write('C4','Nomor',table_header)
                sheet.write('D4','Tanggal',table_header)
                sheet.merge_range('E3:F3','INVOICE',table_header)
                sheet.write('E4','Nomor',table_header)
                sheet.write('F4','Tanggal',table_header)
                sheet.merge_range('G3:H3','B/L',table_header)
                sheet.write('G4','Nomor',table_header)
                sheet.write('H4','Tanggal',table_header)
                sheet.merge_range('G3:H3','B/L',table_header)
                sheet.write('G4','Nomor',table_header)
                sheet.write('H4','Tanggal',table_header)
                sheet.merge_range('I3:J3','PEMBELI',table_header)
                sheet.write('I4','Nama',table_header)
                sheet.write('J4','Negara',table_header)
                sheet.merge_range('K3:L3','NILAI',table_header)
                sheet.write('K4','Jumlah',table_header)
                sheet.write('L4','Currency',table_header)
                sheet.merge_range('M3:M4','KURS',table_header)
                sheet.merge_range('N3:N4','NILAI\n(Rp)',table_header)
                sheet.merge_range('O3:O4','URAIAN\nNAMA BARANG',table_header)
                sheet.merge_range('P3:P4','QUANTITY',table_header)
                sheet.merge_range('Q3:Q4','PAYMENT\nTERM',table_header)
                sheet.merge_range('R3:U3','PEMBAYARAN',table_header)
                sheet.write('R4','Tanggal',table_header)
                sheet.write('S4','No. Bukti',table_header)
                sheet.write('T4','Bank',table_header)
                sheet.write('U4','Jumlah',table_header)
             
                row = 4
                no = 0
                for acc in account:	
                    no+=1	
                    sheet.write(row,0,acc.date.strftime("%B"),body)
                    sheet.write(row,1,no,body)
                    sheet.write(row,2,acc.peb_no,body)
                    sheet.write(row,3,acc.peb_date if acc.peb_date else "",body)
                    sheet.write(row,4,acc.name,body)
                    sheet.write(row,5, str(acc.invoice_date) if acc.invoice_date else "", body)
                    sheet.write(row,6,'',body)
                    sheet.write(row,7,'',body)
                    if acc.partner_id.name:
                        sheet.write(row,8,acc.partner_id.name,body)
                    elif acc.partner_id.parent_id.name and acc.partner_id.name:
                        sheet.write(row,8, f"{acc.partner_id.parent_id.name}, {acc.partner_id.name}",body)
                    elif acc.partner_id.parent_id.name and acc.partner_id.type:
                        sheet.write(row,8, f"{acc.partner_id.parent_id.name}, {acc.partner_id.type}",body)
                    sheet.write(row,9,acc.company_id.country_id.name,body)
                    sheet.write(row,10,acc.amount_total,body)
                    sheet.write(row,11,acc.currency_id.name,body)
                    sheet.write(row,12,'',body)
                    sheet.write(row,13,acc.amount_total,body)
                    sheet.write(row,16,acc.invoice_payment_term_id.name if acc.invoice_payment_term_id.name else "",body)
                    sheet.write(row,17,str(acc.account_payment_id.date),body)
                    sheet.write(row,18,acc.account_payment_id.name,body)
                    sheet.write(row,20,acc.account_payment_id.amount,body)
                    for bank in acc.partner_bank_id:
                        if bank.bank_id:
                            sheet.write(row,19,bank.bank_id.name,body)
                        else:
                            sheet.write(row,19,acc.bank_name if acc.bank_name else "",body)
                    for inv in acc.invoice_line_ids:
                        sheet.write(row,14,inv.name,body2)
                        sheet.write(row,15,inv.quantity,body)
                        row += 1