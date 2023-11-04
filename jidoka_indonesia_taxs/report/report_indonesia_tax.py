from odoo import models
 
class HarianProductionXlsx(models.AbstractModel):
    _name = 'report.jidoka_indonesia_taxs.report_indonesia_tax'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, report):
        
        for obj in report:
            report_name = 'Report Indonesia Tax'
            start_date = obj.start_date
            end_date = obj.end_date
            sheet = workbook.add_worksheet(report_name[:31])
            
            text_top_style = workbook.add_format({
                'font_size': 12, 
                'bold': True , 
                'valign': 'vcenter', 
                'text_wrap': True
                })
            label_title = workbook.add_format({
                'bold': True,
                'font_size': 11,
                })
            label_table = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'bold':True,    
                'font_size': 11,
                'border':1,
                'align':'center',
                'bg_color': '#90EE90',
                })
            data_format = workbook.add_format({
                'font_size': 11,
                'border':1,
                })

            sheet.merge_range(0, 0, 0, 5, "Indonesia Tax", text_top_style)

            filter = []
            invoice_obj = self.env['account.move']
            if obj.type == 'out_invoice':
                filter.append(('move_type', '=', 'out_invoice'))
            elif obj.type == 'in_invoice':
                filter.append(('move_type', '=', 'in_invoice'))
            else :
                filter.append('|')
                filter.append(('move_type', '=', 'out_invoice'))
                filter.append(('move_type', '=', 'in_invoice'))

            filter.append(('invoice_date','>=',start_date))
            filter.append(('invoice_date','<=',end_date))

            invoice = invoice_obj.search(filter, order="invoice_date asc")

            sheet.set_column('A:A', 11)
            sheet.set_column('B:B', 4)
            sheet.set_column('C:C', 35)
            sheet.set_column('D:D', 16)
            sheet.set_column('E:E', 16)
            sheet.set_column('F:F', 16)
            sheet.set_column('G:G', 16)
            sheet.set_column('H:H', 16)
            sheet.set_column('I:I', 16)
            sheet.set_column('J:J', 16)
            sheet.set_column('K:K', 16)
            sheet.set_column('L:L', 16)
            sheet.set_column('M:M', 16)
            sheet.set_column('N:N', 16)
            sheet.set_column('O:O', 16)
            sheet.set_column('P:P', 16)
            sheet.set_column('Q:Q', 16)

            sheet.write(1, 0, report_name, label_title)
            sheet.write(2, 0, "Period : %s to %s" % (start_date, end_date), label_title)
            sheet.merge_range(5, 0, 6, 0,"Masa", label_table)
            sheet.merge_range(5, 1, 6, 1, "No.", label_table)
            sheet.merge_range(5, 2, 6, 2, "NAMA PKP PENJUAL", label_table)
            sheet.merge_range(5, 3, 6, 3, "NPWP", label_table)
            sheet.merge_range(5, 4, 5, 5, "FAKTUR PAJAK", label_table)
            sheet.write(6, 4, "Nomor", label_table)
            sheet.write(6, 5, "Tanggal", label_table)
            sheet.merge_range(5, 6, 6, 6, "Struktur / Uraian", label_table)
            sheet.write(5, 7, "DPP", label_table)
            sheet.write(6, 7, "(Rp)", label_table)
            sheet.write(5, 8, "PPN", label_table)
            sheet.write(6, 8, "(Rp)", label_table)
            sheet.merge_range(5, 9, 5, 13, "PELUNASAN", label_table)
            sheet.write(6, 9, "Tanggal Bayar", label_table)
            sheet.write(6, 10, "No. Document", label_table)
            sheet.write(6, 11, "Bank", label_table)
            sheet.write(6, 12, "No. Rekening", label_table)
            sheet.write(6, 13, "Jumlah", label_table)
            sheet.merge_range(5, 14, 5, 15, "Surat Jalan / Invoice", label_table)
            sheet.write(6, 14, "Nomor", label_table)
            sheet.write(6, 15, "Tanggal", label_table)

            no = 0
            first_row = 7
            for inv in invoice:
                no+=1
                sheet.write(first_row, 0, inv.invoice_date.strftime("%B") if inv.invoice_date else "", data_format)
                sheet.write(first_row, 1, no, data_format)
                sheet.write(first_row, 2, inv.partner_id.name if inv.partner_id.name else "", data_format)
                sheet.write(first_row, 3, inv.partner_id.vat if inv.partner_id.vat else "", data_format)
                sheet.write(first_row, 4, inv.faktur_number if inv.faktur_number else "", data_format)
                sheet.write(first_row, 5, inv.faktur_date if inv.faktur_date else "", data_format)
                sheet.write(first_row, 6, inv.uraian if inv.uraian else "", data_format)
                sheet.write(first_row, 7, inv.amount_untaxed, data_format)
                sheet.write(first_row, 8, inv.amount_tax, data_format)
                sheet.write(first_row, 9, inv.invoice_date_due.strftime("%d/%m/%Y") if inv.invoice_date_due else "", data_format)
                # sheet.write(first_row, 10, inv.document_number if inv.document_number else "", data_format)
                sheet.write(first_row, 10, inv.account_payment_id.name if inv.account_payment_id.name else "", data_format)
                sheet.write(first_row, 11, inv.partner_bank_id.bank_id.name if inv.partner_bank_id.bank_id else "", data_format)
                sheet.write(first_row, 12, inv.partner_bank_id.acc_number if inv.partner_bank_id.acc_number else "", data_format)
                sheet.write(first_row, 13, inv.amount_total, data_format)
                sheet.write(first_row, 14, inv.surat_jalan_number if inv.surat_jalan_number else "", data_format)
                sheet.write(first_row, 15, inv.surat_jalan_date if inv.surat_jalan_date else "", data_format)
                first_row+=1
