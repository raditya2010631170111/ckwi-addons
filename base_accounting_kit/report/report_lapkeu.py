from odoo import models, fields, _

class ReportLapkeu(models.AbstractModel):
    _name = 'report.base_accounting_kit.report_lapkeu'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        for obj in objects:
            report_name = 'LapKeu'
            start_date = obj.start_date
            end_date = obj.end_date
            sheet = workbook.add_worksheet(report_name[:31])
            bold_header = workbook.add_format({'font_size':14,'bold':True})
            bold_header2 = workbook.add_format({'font_size':14,'bold':True,'align':'center','text_wrap':True})
            bold_header3 = workbook.add_format({'font_size':14,'bold':True,'align':'center'})
            bold_border = workbook.add_format({'font_size':14,'bold':True,'border':1})
            border_text = workbook.add_format({'border':1})
            bold_text = workbook.add_format({'bold':True})
            bold_center = workbook.add_format({'bold':True,'align':'center'})
            border_bottom = workbook.add_format()
            border_bottom.set_bottom(1)
            border_top = workbook.add_format()
            border_top.set_top(1)
            top_bottom = workbook.add_format()
            top_bottom.set_top(1)
            top_bottom.set_bottom(1)
            border_blue = workbook.add_format({'bg_color': '#B0E0E6','border':1})
            color_blue = workbook.add_format({'bg_color': '#B0E0E6'})
            border_yellow = workbook.add_format({'bg_color': 'yellow','border':1})
            color_yellow = workbook.add_format({'bg_color': 'yellow'})
            filter = []
            account_obj = self.env['account.payment']
            
            #JC-216 Report Akunting, Balance Sheet, Profil Loss, Trial Balance, Cash Flow, Partner Ledger, Partner Ageing, Multi Currencies

            if obj.type == 'neraca':
                filter.append(('payment_type', '=', 'inbound'))
            elif obj.type == 'perincian_neraca':
                filter.append(('payment_type', '=', 'inbound'))
            elif obj.type == 'laba_rugi':
                filter.append(('payment_type', '=', 'inbound'))
            elif obj.type == 'perincian_rl':
                filter.append(('payment_type', '=', 'inbound'))
            filter.append(('date', '>=', start_date))
            filter.append(('date', '<=', end_date))
            account = account_obj.search(filter, order="date asc")
            
            type_dict = {
                'neraca': 'N E R A C A',
                'perincian_neraca': 'PENJELASAN POS-POS NERACA',
                'laba_rugi': 'PERHITUNGAN LABA RUGI',
                'perincian_rl': 'PENJELASAN POS-POS LABA RUGI',
                False: ''
            }
            
            if obj.type == 'neraca':
                sheet.set_column(0, 0, 40)
                sheet.set_column(1, 1, 20)
                sheet.set_column(2, 2, 30)
                sheet.write('A1',obj.env.company.name,bold_header)
                sheet.write('A2',type_dict[obj.type],bold_header)
                sheet.write('A3','PER %s' % (obj.start_date.strftime("%d %B %Y").upper() if obj.start_date else ""),bold_header)
                sheet.write('A5','AKTIVA',bold_header)
                sheet.write('A7','AKTIVA LANCAR',bold_header)
                sheet.write('A8','Kas & Bank')
                sheet.write('A9','Piutang Eksport')
                sheet.write('A10','Piutang Lokal')
                sheet.write('A11','Piutang Karyawan')
                sheet.write('A12','Uang Muka')
                sheet.write('A13','Uang Jaminan')
                sheet.write('A14','Persediaan')
                sheet.write('A15','Biaya Dibayar Dimuka')
                sheet.write('A16','Pajak Dibayar Dimuka')
                sheet.write('A17','JUMLAH AKTIVA LANCAR',bold_header)
                sheet.write('A19','AKTIVA TETAP',bold_header)
                sheet.write('A20','Nilai Perolehan')
                sheet.write('A21','Akumulasi Penyusutan')
                sheet.write('A22','NILAI BUKU',bold_header)
                sheet.write('A24','JUMLAH AKTIVA',bold_header)
                sheet.write('A26','PASSIVA',bold_header)
                sheet.write('A28','HUTANG LANCAR',bold_header)
                sheet.write('A29','Hutang Dagang')
                sheet.write('A30','Hutang Bank')
                sheet.write('A31','Uang Muka Penjualan')
                sheet.write('A32','Pajak YMH Dibayar')
                sheet.write('A33','Biaya YMH Dibayar')
                sheet.write('A34','JUMLAH HUTANG LANCAR',bold_header)
                sheet.write('A36','HUTANG JANGKA PANJANG',bold_header)
                sheet.write('A37','Hutang Lain-lain')
                sheet.write('A38','JUMLAH HUTANG JANGKA PANJANG',bold_header)
                sheet.write('A40','MODAL',bold_header)
                sheet.write('A41','Modal Saham')
                sheet.write('A42','Laba (Rugi) Tahun-Tahun Yang  Lalu')
                sheet.write('A43','Laba (Rugi) Tahun-berjalan')
                sheet.write('A44','JUMLAH MODAL',bold_header)
                sheet.write('A46','JUMLAH HUTANG DAN MODAL',bold_header)
                
                for acc in account:	
                    sheet.write('B8',acc.amount)
                    sheet.write('B9',acc.amount)
                    sheet.write('B10',acc.amount)
                    sheet.write('B11',acc.amount)
                    sheet.write('B12',acc.amount)
                    sheet.write('B13',acc.amount)
                    sheet.write('B14',acc.amount)
                    sheet.write('B15',acc.amount)
                    sheet.write('B16',acc.amount)
                    sum_aktiva_lancar = acc.amount + acc.amount + acc.amount + acc.amount + acc.amount + acc.amount + acc.amount + acc.amount + acc.amount
                    sheet.write('B17','',border_top)
                    sheet.write('C17',sum_aktiva_lancar)
                    sheet.write('B20',acc.amount)
                    sheet.write('B21',acc.amount)
                    sum_buku = acc.amount - acc.amount
                    sheet.write('B22','',border_top)
                    sheet.write('B22',sum_buku,border_bottom)
                    sum_aktiva = sum_aktiva_lancar + sum_buku
                    sheet.write('C24',sum_aktiva,border_bottom)
                    sheet.write('C25','',border_top)
                    sheet.write('B29',acc.amount)
                    sheet.write('B30',acc.amount)
                    sheet.write('B31',acc.amount)
                    sheet.write('B32',acc.amount)
                    sheet.write('B33',acc.amount)
                    sum_hutang = acc.amount + acc.amount + acc.amount + acc.amount + acc.amount
                    sheet.write('B34','',border_top)
                    sheet.write('C34',sum_hutang)
                    sheet.write('B37',acc.amount)
                    sheet.write('B38','',border_top)
                    sum_hutang_panjang = acc.amount
                    sheet.write('C38',sum_hutang_panjang)
                    sheet.write('B41',acc.amount)
                    sheet.write('B42',acc.amount)
                    sheet.write('B43',acc.amount)
                    sum_modal = acc.amount + acc.amount + acc.amount
                    sheet.write('B44','',border_top)
                    sheet.write('C44',sum_modal,border_bottom)
                    sum_hutang_modal = sum_hutang + sum_hutang_panjang + sum_modal
                    sheet.write('C46',sum_hutang_modal,border_bottom)
                    sheet.write('C47','',border_top)
                    
            elif obj.type == 'perincian_neraca':
                sheet.set_column(0, 0, 12)
                sheet.set_column(1, 1, 40)
                sheet.set_column(2, 2, 20)
                sheet.set_column(3, 3, 20)
                sheet.write('A1',obj.env.company.name,bold_header)
                sheet.write('A2',type_dict[obj.type],bold_header)
                sheet.write('A3','PER %s' % (obj.start_date.strftime("%d %B %Y").upper() if obj.start_date else ""),bold_header)
                sheet.merge_range('A5:B5','POS-POS NERACA',bold_header3)
                sheet.write('C5','JUMLAH',bold_header3)
                sheet.write('D5','TOTAL',bold_header3)
                sheet.write('A6','KAS & BANK',bold_border)
                sheet.write('B6','',bold_border)
                sheet.write('C6','',bold_border)
                sheet.write('D6','',bold_border)
                
                row = 6
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.journal_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'PIUTANG EKSPORT',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'PIUTANG LOKAL',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'PIUTANG KARYAWAN',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'UANG MUKA',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'UANG JAMINAN',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'PERSEDIAAN',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'BIAYA DIBAYAR MUKA',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'AKTIVA TETAP',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'AKUMULASI PENYUSUTAN',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'HUTANG DAGANG',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'HUTANG BANK',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'UANG MUKA PENJUALAN',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'PAJAK YMH DIBAYAR',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    #for move in acc.move_id:
                        #for inv in move.invoice_line_ids:
                            #sheet.write(row,1,inv.tax_ids,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'BIAYA YMH DIBAYAR',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'HUTANG LAIN-LAIN',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'MODAL',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                
            elif obj.type == 'laba_rugi':
                sheet.set_column(0, 0, 50)
                sheet.set_column(1, 1, 20)
                sheet.set_column(2, 2, 25)
                sheet.set_column(3, 3, 3)
                sheet.set_column(4, 4, 17)
                sheet.set_column(5, 5, 25)
                sheet.merge_range('A1:F1',obj.env.company.name,bold_header3)
                sheet.merge_range('A2:F2',type_dict[obj.type],bold_header3)
                sheet.merge_range('A3:F3','UNTUK TAHUN YANG BERAKHIR PADA %s' % (obj.end_date.strftime("%d %B %Y").upper() if obj.end_date else ""),bold_header3)
                sheet.merge_range('B5:C5','KOMERSIL',bold_header3)
                sheet.write('E5','KOREKSI FISKAL',bold_header2)
                sheet.write('F5','FISKAL',bold_header3)
                sheet.write('A7','PENJUALAN',bold_header)
                sheet.write('A8','  PENJUALAN LOKAL')
                sheet.write('A9','  PENJUALAN EKSPORT')
                sheet.write('A10','TOTAL PENJUALAN',bold_header)
                sheet.write('A12','HARGA POKOK PENJUALAN',bold_header)
                sheet.write('A14','PEMAKAIAN BAHAN BAKU',bold_text)
                sheet.write('A15','   PERSEDIAAN AWAL')
                sheet.write('A16','   PEMBELIAN')
                sheet.write('A17','   PERSEDIAAN AKHIR')
                sheet.write('A18','PEMAKAIAN BAHAN BAKU',bold_center)
                sheet.write('A20','PEMAKAIAN BAHAN PEMBANTU',bold_text)
                sheet.write('A21','   PERSEDIAAN AWAL')
                sheet.write('A22','   PEMBELIAN BAHAN PEMBANTU')
                sheet.write('A23','   PERSEDIAAN AKHIR')
                sheet.write('A24','PEMAKAIAN BAHAN BAKU',bold_center)
                sheet.write('A26','PERSEDIAAN AWAL BARANG JADI')
                sheet.write('A27','PERSEDIAAN AKHIR BARANG JADI')
                sheet.write('A29','WIP AWAL')
                sheet.write('A30','WIP AKHIR')
                sheet.write('A32','TOTAL HARGA POKOK PRODUKSI',bold_header)
                sheet.write('A34','BIAYA PRODUKSI',bold_text)
                sheet.write('A35','   BIAYA UPAH LANGSUNG')
                sheet.write('A36','   BIAYA PRODUKSI LAINNYA')
                sheet.write('A37','TOTAL BIAYA PRODUKSI',bold_center)
                sheet.write('A39','HARGA POKOK PENJUALAN',bold_header)
                sheet.write('A41','LABA KOTOR',bold_header)
                sheet.write('A43','BIAYA PENJUALAN & ADMINISTRASI',bold_header)
                sheet.write('A44','  BIAYA PENJUALAN')
                sheet.write('A45','  BIAYA ADMINISTRASI')
                sheet.write('A46','TOTAL BIAYA PENJUALAN & ADMINISTRASI',bold_header)
                sheet.write('A48','LABA OPERASIONAL',bold_header)
                sheet.write('A50','PENDAPATAN DAN BIAYA LAIN',bold_header)
                sheet.write('A51','  PENDAPATAN LAIN - LAIN')
                sheet.write('A52','  BIAYA LAIN -LAIN')
                sheet.write('A53','TOTAL PENDAPATAN & BIAYA LAIN-LAIN',bold_header)
                sheet.write('A55','LABA (RUGI) SEBELUM PAJAK',bold_header)
                sheet.write('A56','PAJAK PENGHASILAN',bold_header)
                sheet.write('A57','LABA (RUGI) SETELAH PAJAK',bold_header)
                
                sheet.write('B8',None)
                sheet.write('B9',None)
                sheet.write('B10',None,border_top)
                sheet.write('B12',None)
                sheet.write('B15',None)
                sheet.write('B16',None)
                sheet.write('B17',None)
                sheet.write('B18',None,border_top)
                sheet.write('B21',None)
                sheet.write('B22',None)
                sheet.write('B23',None)
                sheet.write('B24',None,border_top)
                sheet.write('B26',None)
                sheet.write('B27',None)
                sheet.write('B29',None)
                sheet.write('B30',None)
                sheet.write('B32',None)
                sheet.write('B35',None)
                sheet.write('B36',None)
                sheet.write('B37',None,border_top)
                sheet.write('B39',None)
                sheet.write('B41',None)
                sheet.write('B44',None)
                sheet.write('B45',None)
                sheet.write('B46',None,border_top)
                sheet.write('B48',None)
                sheet.write('B51',None)
                sheet.write('B52',None)
                sheet.write('B53',None,border_top)
                sheet.write('B55',None)
                sheet.write('B56',None)
                sheet.write('B57',None)
                
                #sum_TOTAL PENJUALAN = 
                sheet.write('C10',None)
                #sum_PEMAKAIAN BAHAN BAKU = 
                sheet.write('C18',None)
                #sum _PEMAKAIAN BAHAN PEMBANTU = 
                sheet.write('C24',None)
                #sum_WIP AKHIR = 
                sheet.write('C31',None,border_top)
                #sum_HARGA POKOK PENJUALAN = 
                sheet.write('C40',None,border_top)
                #sum_TOTAL BIAYA PENJUALAN & ADMINISTRASI = 
                sheet.write('C46',None,border_top)
                #sum_TOTAL PENDAPATAN & BIAYA LAIN-LAIN = 
                sheet.write('C54',None,border_top)
                #sum_PAJAK PENGHASILAN =
                sheet.write('C58',None,top_bottom)
                #sum_LABA (RUGI) SETELAH PAJAK = 
                sheet.write('C58',None,border_top)
                
                #sum_TOTAL PENJUALAN = 
                sheet.write('F10',None,border_top)
                #sum_PEMAKAIAN BAHAN BAKU = 
                sheet.write('F18',None,border_top)
                #sum_PEMAKAIAN BAHAN PEMBANTU = 
                sheet.write('F24',None,border_top)
                #sum_WIP AKHIR = 
                sheet.write('F31',None,border_top)
                #sum_TOTAL BIAYA PRODUKSI =
                sheet.write('F37',None,border_top)
                #sum_HARGA POKOK PENJUALAN = 
                sheet.write('F40',None,border_top)
                #sum_BIAYA ADMINISTRASI = 
                sheet.write('F46',None,border_top)
                #sum_BIAYA LAIN -LAIN =
                sheet.write('F53',None,border_top)
                #sum_TOTAL PENDAPATAN & BIAYA LAIN-LAIN =
                sheet.write('F54',None,border_top)
                #sum_LABA (RUGI) SEBELUM PAJAK = 
                sheet.write('F55',None,border_bottom)
                sheet.write('F56',None,border_top)
                    
            elif obj.type == 'perincian_rl':
                sheet.set_column(0, 0, 12)
                sheet.set_column(1, 1, 40)
                sheet.set_column(2, 2, 20)
                sheet.set_column(3, 3, 20)
                sheet.write('A1',obj.env.company.name,bold_header)
                sheet.write('A2',type_dict[obj.type],bold_header)
                sheet.write('A3','UNTUK TAHUN YANG BERAKHIR PADA %s' % (obj.end_date.strftime("%d %B %Y").upper() if obj.end_date else ""),bold_header)
                sheet.merge_range('A5:B5','POS-POS LABA RUGI',bold_header3)
                sheet.write('C5','JUMLAH',bold_header3)
                sheet.write('D5','TOTAL',bold_header3)
                sheet.write('A6','PENJUALAN',bold_border)
                sheet.write('B6','',bold_border)
                sheet.write('C6','',bold_border)
                sheet.write('D6','',bold_border)
                
                row = 6
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'PEMAKAIAN BAHAN BAKU',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'PEMAKAIAN BAHAN PEMBANTU',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'BIAYA UPAH LANGSUNG',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'BIAYA PRODUKSI LAINNYA',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_yellow)
                    sheet.write(row,3,acc.amount,border_text)
                    #if acc.quantity == <0
                        #sheet.write(row,2,None,border_blue)
                    #elif acc.quantity == <0
                        #sheet.write(row,2,None,border_yellow)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'BIAYA PENJUALAN',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'BIAYA ADMINISTRASI',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'PENDAPATAN LAIN-LAIN',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                sheet.write(row,0,'',border_text)
                sheet.write(row,1,'',border_text)
                sheet.write(row,2,'',border_text)
                sheet.write(row,3,'',border_text)
                row += 1
                    
                sheet.write(row,0,'BIAYA LAIN-LAIN',bold_border)
                sheet.write(row,1,'',bold_border)
                sheet.write(row,2,'',bold_border)
                sheet.write(row,3,'',bold_border)
                
                row += 1
                for acc in account:	
                    sheet.write(row,0,acc.destination_account_id.code,border_text)
                    sheet.write(row,1,acc.partner_id.name,border_text)
                    sheet.write(row,2,None,border_text)
                    sheet.write(row,3,acc.amount,border_text)
                    row += 1
                
                row += 1
                sheet.write(row,0,'Legenda :')
                row += 1
                sheet.write(row,0,'',color_blue)
                sheet.write(row,1,'Koreksi negatif')
                row += 1
                sheet.write(row,0,'',color_yellow)
                sheet.write(row,1,'Koreksi positif')
