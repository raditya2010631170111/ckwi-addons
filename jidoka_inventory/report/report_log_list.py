from odoo import models, fields, _


class ReportLogListXLSX(models.AbstractModel):
    _name = 'report.jidoka_inventory.report_log_list_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        for obj in objects:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet('PL')
            sheet.set_column(0, 11, 5.1)
            sheet.set_row(10, 28)
            bold_header = workbook.add_format({'bold':True,'align':'center','valign':'vcenter','underline':True})
            date_format = workbook.add_format({'num_format':'dd-MMM-yyyy','font_size':10})
            table_header = workbook.add_format({'border':1,'align':'center','valign':'vcenter','text_wrap':True,'font_size':10})
            header = workbook.add_format({'font_size':10})
            header_center = workbook.add_format({'font_size':10,'align':'center','valign':'vcenter'})
            table_body = workbook.add_format({'border':1,'align':'center','valign':'vcenter','text_wrap':True,'font_size':10})
            table_body_num = workbook.add_format({'num_format': '#,###0.000','border':1,'align':'center','valign':'vcenter','text_wrap':True,'font_size':10})
            border_bot = workbook.add_format({'align':'center','valign':'vcenter'})
            border_bot.set_bottom(1)
            border_bot_right = workbook.add_format({'num_format': '#,###0.000', 'align':'center','valign':'vcenter','font_size':10})
            border_bot_right.set_bottom(1)
            border_bot_right.set_right(1)
            border_bot_left = workbook.add_format({'align':'left','valign':'vcenter','font_size':10})
            border_bot_left.set_bottom(1)
            border_bot_left.set_left(1)
            border_bot_top = workbook.add_format({'align':'left','valign':'vcenter','font_size':10})
            border_bot_top.set_bottom(1)
            border_bot_top.set_top(1)
            border_bot_top_center = workbook.add_format({'align':'center','valign':'vcenter','font_size':10})
            border_bot_top_center.set_bottom(1)
            border_bot_top_center.set_top(1)
            border_bot_top_num = workbook.add_format({'num_format': '#,###0.000', 'align':'center','valign':'vcenter','font_size':10})
            border_bot_top_num.set_bottom(1)
            border_bot_top_num.set_top(1)
            sheet.write('A1', obj.env.company.name, header)
            sheet.write('A2', 'DEPT. PEMBELIAN BAHAN BAKU', header)
            sheet.merge_range('A3:L3', 'LOG LIST', bold_header)
            sheet.write('A4', 'PENERIMAAN', header)
            sheet.write('A5', 'PEMAKAIAN', header)
            sheet.write('A6', 'SUPPLIER', header)
            sheet.write('A7', 'CODE', header)
            sheet.write('A8', 'JENIS', header)
            sheet.write('A9', 'TPK/KPH', header)
            sheet.write('C4', '%s %s' %(': ',''), header)
            sheet.write('C5', '%s %s' %(': ',''), header)
            sheet.write('C6', '%s %s' %(': ',obj.partner_id.display_name or ''), header)
            sheet.write('C7', '%s %s' %(': ',obj.partner_id.supplier_code_id.code or ''), header)
            sheet.write('C8', '%s %s' %(': ',''), header)
            sheet.write('C9', '%s %s' %(': ',''), header)
            sheet.write('G4', 'Kwalitas', header)
            sheet.write('G5', 'Tanggal', header)
            sheet.write('G6', 'Truck No.', header)
            sheet.write('G7', 'P.O No.', header)
            sheet.write('G8', 'SKSHHK / NOTA', header)
            sheet.write('G9', 'DKB', header)
            sheet.write('I4', '%s %s' %(': ',''), header)
            sheet.write('I5', '%s %s' %(': ',obj.date_done or ''),date_format)
            sheet.write('I6', '%s %s' %(': ',obj.plat_no or ''), header)
            sheet.write('I7', '%s %s' %(': ',obj.origin or ''), header)
            sheet.write('I8', '%s %s' %(': ',obj.nota or ''), header)
            # sheet.write('C9', '%s %s' %(' : ','A'))
            
            max_perpage = 70
            obj_line = []
            no = 1
            gt_kubikasi = 0
            kubikasi = 0
            for rec in obj.move_line_nosuggest_ids:
                if rec.product_id.product_tmpl_id.wood_type == 'log':
                    obj_line.append({
                        # 'klas':rec.product_id.product_tmpl_id.wood_class_id.name or '',
                        'klas':rec.wood_class_id.name or '',
                        'no':no,
                        # 'p':rec.size_log_id.panjang or '',
                        # 'd':rec.size_log_id.diameter or '',
                        'p':rec.panjang_slog or '',
                        'd':rec.diameter_slog or '',
                        'pcs':'1',
                        # 'kubikasi':rec.size_log_id.kubikasi or ''
                        'kubikasi':rec.qty_done or ''
                    })
                    gt_kubikasi = gt_kubikasi + float(rec.size_log_id.kubikasi or 0.00)
                else:
                    vol = rec.panjang * rec.lebar * rec.tinggi
                    if vol > 0:
                        kubikasi = vol / 1000000
                    obj_line.append({
                        # 'klas':rec.product_id.product_tmpl_id.wood_class_id.name or '',
                        'klas':rec.wood_class_id.name or '',
                        'no':no,
                        'p':rec.panjang or '',
                        'l':rec.lebar or '',
                        't':rec.tinggi or '',
                        'pcs':'1',
                        'kubikasi': kubikasi or ''
                    })
                    gt_kubikasi = gt_kubikasi + float(kubikasi or 0.00)
                no = no + 1
            page = (len(obj_line) // max_perpage) + 1
            row = 10
            count_side = 1
            if rec.product_id.product_tmpl_id.wood_type == 'log':
                row = self.generate_xlsx_log(sheet, header, table_header, header_center, table_body, border_bot, border_bot_left, border_bot_right,table_body_num,obj_line, page, max_perpage,count_side,row)
            else:
                row = self.generate_xlsx_square(sheet, header, table_header, header_center, table_body, border_bot, border_bot_left, border_bot_right,table_body_num,obj_line, page, max_perpage,count_side,row)
            sheet.write(row,0,'GRAND TOTAL',border_bot_top)
            sheet.write(row,1,'',border_bot_top)
            sheet.write(row,2,'',border_bot_top)
            sheet.write(row,3,'',border_bot_top)
            sheet.write(row,4,'',border_bot_top)
            sheet.write(row,5,'',border_bot_top)
            sheet.write(row,6,'',border_bot_top)
            sheet.write(row,7,'',border_bot_top)
            sheet.write(row,8,'',border_bot_top)
            sheet.write(row,9,'',border_bot_top)
            sheet.write(row,10,len(obj_line),border_bot_top_center)
            sheet.write(row,11,gt_kubikasi,border_bot_top_num)

            sheet.merge_range(row+2,0,row+2,1,'Diketahui',header_center)
            sheet.merge_range(row+2,10,row+2,11,'Dibuat',header_center)
            sheet.merge_range(row+7,0,row+7,1,'INDRA K',bold_header)
            sheet.merge_range(row+7,10,row+7,11,'Tari',bold_header)

    def generate_xlsx_log(self, sheet, header, table_header, header_center, table_body, border_bot, border_bot_left, border_bot_right,table_body_num,obj_line, page, max_perpage,count_side,row):
        for p in range(1,page+1):
            if len(obj_line) % max_perpage != 0:
                sheet.write(row-1,6,'PAGE',header)
                sheet.write(row-1,8,': %s'% (p),header)
                sheet.write(row-1,9,'Of',header_center)
                sheet.write(row-1,10,page,header)
                sheet.merge_range(row,0,row+1,0, 'KLAS',table_header)
                sheet.merge_range(row,1,row+1,1, 'NO',table_header)
                sheet.merge_range(row,2,row+1,2, 'PJG',table_header)
                sheet.write(row,3, 'DIAMETER / Cm',table_header)
                sheet.write(row+1,3, 'Ø',table_header)
                sheet.merge_range(row,4,row+1,4, 'PCS',table_header)
                sheet.merge_range(row,5,row+1,5, 'M3',table_header)
                sheet.merge_range(row,6,row+1,6, 'KLAS',table_header)
                sheet.merge_range(row,7,row+1,7, 'NO',table_header)
                sheet.merge_range(row,8,row+1,8, 'PJG',table_header)
                sheet.write(row,9, 'DIAMETER / Cm',table_header)
                sheet.write(row+1,9, 'Ø',table_header)
                sheet.merge_range(row,10,row+1,10, 'PCS',table_header)
                sheet.merge_range(row,11,row+1,11, 'M3',table_header)
            idx = (p-1) * max_perpage
            output_line = obj_line[idx:idx+max_perpage]
            row = row + 2
            right_row = row
            total_pcs = total_kubikasi = 0
            for line in output_line:
                if count_side <= 35:
                    sheet.write(row,0,line.get('klas'), table_body)
                    sheet.write(row,1,line.get('no'), table_body)
                    sheet.write(row,2,line.get('p'), table_body)
                    sheet.write(row,3,line.get('d'), table_body)
                    sheet.write(row,4,line.get('pcs'), table_body)
                    sheet.write(row,5,line.get('kubikasi'), table_body_num)
                    row = row + 1
                    total_pcs = total_pcs + int(line.get('pcs') or 0.00)
                    total_kubikasi = total_kubikasi + float(line.get('kubikasi') or 0.00)
                else:
                    sheet.write(right_row,6,line.get('klas'), table_body)
                    sheet.write(right_row,7,line.get('no'), table_body)
                    sheet.write(right_row,8,line.get('p'), table_body)
                    sheet.write(right_row,9,line.get('d'), table_body)
                    sheet.write(right_row,10,line.get('pcs'), table_body)
                    sheet.write(right_row,11,line.get('kubikasi'), table_body_num)
                    right_row = right_row + 1
                    total_pcs = total_pcs + int(line.get('pcs') or 0.00)
                    total_kubikasi = total_kubikasi + float(line.get('kubikasi') or 0.00)
                if count_side == 35:
                    sheet.write(row,0,'Sub Total', border_bot_left)
                    sheet.write(row,1,'', border_bot)
                    sheet.write(row,2,'', border_bot)
                    sheet.write(row,3,'', border_bot)
                    sheet.write(row,4,total_pcs, table_body)
                    sheet.write(row,5,total_kubikasi, border_bot_right)
                    row = row + 1
                    total_pcs = total_kubikasi = 0
                if count_side == max_perpage:
                    sheet.write(right_row,6,'Sub Total', border_bot_left)
                    sheet.write(right_row,7,'', border_bot)
                    sheet.write(right_row,8,'', border_bot)
                    sheet.write(right_row,9,'', border_bot)
                    sheet.write(right_row,10,total_pcs, table_body)
                    sheet.write(right_row,11,total_kubikasi, border_bot_right)
                    right_row = right_row + 1
                    total_pcs = total_kubikasi = 0
                count_side = count_side + 1
                if count_side > max_perpage:
                    count_side = 1
                    row = row + 2
            if len(obj_line) % max_perpage != 0:
                for x in range(0,max_perpage-count_side+1):
                    if count_side <= 35:
                        sheet.write(row,0,'', table_body)
                        sheet.write(row,1,'', table_body)
                        sheet.write(row,2,'', table_body)
                        sheet.write(row,3,'', table_body)
                        sheet.write(row,4,'', table_body)
                        sheet.write(row,5,'', table_body)
                        row = row + 1
                    else:
                        sheet.write(right_row,6,'', table_body)
                        sheet.write(right_row,7,'', table_body)
                        sheet.write(right_row,8,'', table_body)
                        sheet.write(right_row,9,'', table_body)
                        sheet.write(right_row,10,'', table_body)
                        sheet.write(right_row,11,'',table_body)
                        right_row = right_row + 1
                    if count_side == 35:
                        sheet.write(row,0,'Sub Total', border_bot_left)
                        sheet.write(row,1,'', border_bot)
                        sheet.write(row,2,'', border_bot)
                        sheet.write(row,3,'', border_bot)
                        sheet.write(row,4,total_pcs, table_body)
                        sheet.write(row,5,total_kubikasi, border_bot_right)
                        row = row + 1
                        total_pcs = total_kubikasi = 0
                    if count_side == max_perpage:
                        sheet.write(right_row,6,'Sub Total', border_bot_left)
                        sheet.write(right_row,7,'', border_bot)
                        sheet.write(right_row,8,'', border_bot)
                        sheet.write(right_row,9,'', border_bot)
                        if total_pcs == 0:
                            sheet.write(right_row,10,'', table_body)
                        else:
                            sheet.write(right_row,10,total_pcs, table_body)
                        if total_kubikasi == 0:
                            sheet.write(right_row,11,'', border_bot_right)
                        else:
                            sheet.write(right_row,11,total_kubikasi, border_bot_right)
                        right_row = right_row + 1
                        total_pcs = total_kubikasi = 0
                    count_side = count_side + 1
                    if count_side > max_perpage:
                        count_side = 1
                        row = row + 2
        return row

    def generate_xlsx_square(self, sheet, header, table_header, header_center, table_body, border_bot, border_bot_left, border_bot_right,table_body_num,obj_line, page, max_perpage,count_side,row):
        for p in range(1,page+1):
            if len(obj_line) % max_perpage != 0:
                sheet.write(row-1,6,'PAGE',header)
                sheet.write(row-1,8,': %s'% (p),header)
                sheet.write(row-1,9,'Of',header_center)
                sheet.write(row-1,10,page,header)
                sheet.merge_range(row,0,row+1,0, 'KLAS',table_header)
                sheet.write(row,1, 'D / Cm',table_header)
                sheet.write(row+1,1, 'Ø',table_header)
                sheet.write(row,2, 'D / Cm',table_header)
                sheet.write(row+1,2, 'Ø',table_header)
                sheet.merge_range(row,3,row+1,3, 'PJG',table_header)
                sheet.merge_range(row,4,row+1,4, 'PCS',table_header)
                sheet.merge_range(row,5,row+1,5, 'M3',table_header)
                sheet.merge_range(row,6,row+1,6, 'KLAS',table_header)
                sheet.write(row,7, 'D / Cm',table_header)
                sheet.write(row+1,7, 'Ø',table_header)
                sheet.write(row,8, 'D / Cm',table_header)
                sheet.write(row+1,8, 'Ø',table_header)
                sheet.merge_range(row,9,row+1,9, 'PJG',table_header)
                sheet.merge_range(row,10,row+1,10, 'PCS',table_header)
                sheet.merge_range(row,11,row+1,11, 'M3',table_header)
            idx = (p-1) * max_perpage
            output_line = obj_line[idx:idx+max_perpage]
            row = row + 2
            right_row = row
            total_pcs = total_kubikasi = 0
            for line in output_line:
                if count_side <= 35:
                    sheet.write(row,0,line.get('klas'), table_body)
                    sheet.write(row,1,line.get('t'), table_body)
                    sheet.write(row,2,line.get('l'), table_body)
                    sheet.write(row,3,line.get('p'), table_body)
                    sheet.write(row,4,line.get('pcs'), table_body)
                    sheet.write(row,5,line.get('kubikasi'), table_body_num)
                    row = row + 1
                    total_pcs = total_pcs + int(line.get('pcs') or 0.00)
                    total_kubikasi = total_kubikasi + float(line.get('kubikasi') or 0.00)
                else:
                    sheet.write(right_row,6,line.get('klas'), table_body)
                    sheet.write(right_row,7,line.get('t'), table_body)
                    sheet.write(right_row,8,line.get('l'), table_body)
                    sheet.write(right_row,9,line.get('p'), table_body)
                    sheet.write(right_row,10,line.get('pcs'), table_body)
                    sheet.write(right_row,11,line.get('kubikasi'), table_body_num)
                    right_row = right_row + 1
                    total_pcs = total_pcs + int(line.get('pcs') or 0.00)
                    total_kubikasi = total_kubikasi + float(line.get('kubikasi') or 0.00)
                if count_side == 35:
                    sheet.write(row,0,'Sub Total', border_bot_left)
                    sheet.write(row,1,'', border_bot)
                    sheet.write(row,2,'', border_bot)
                    sheet.write(row,3,'', border_bot)
                    sheet.write(row,4,total_pcs, table_body)
                    sheet.write(row,5,total_kubikasi, border_bot_right)
                    row = row + 1
                    total_pcs = total_kubikasi = 0
                if count_side == max_perpage:
                    sheet.write(right_row,6,'Sub Total', border_bot_left)
                    sheet.write(right_row,7,'', border_bot)
                    sheet.write(right_row,8,'', border_bot)
                    sheet.write(right_row,9,'', border_bot)
                    sheet.write(right_row,10,total_pcs, table_body)
                    sheet.write(right_row,11,total_kubikasi, border_bot_right)
                    right_row = right_row + 1
                    total_pcs = total_kubikasi = 0
                count_side = count_side + 1
                if count_side > max_perpage:
                    count_side = 1
                    row = row + 2
            if len(obj_line) % max_perpage != 0:
                for x in range(0,max_perpage-count_side+1):
                    if count_side <= 35:
                        sheet.write(row,0,'', table_body)
                        sheet.write(row,1,'', table_body)
                        sheet.write(row,2,'', table_body)
                        sheet.write(row,3,'', table_body)
                        sheet.write(row,4,'', table_body)
                        sheet.write(row,5,'', table_body)
                        row = row + 1
                    else:
                        sheet.write(right_row,6,'', table_body)
                        sheet.write(right_row,7,'', table_body)
                        sheet.write(right_row,8,'', table_body)
                        sheet.write(right_row,9,'', table_body)
                        sheet.write(right_row,10,'', table_body)
                        sheet.write(right_row,11,'',table_body)
                        right_row = right_row + 1
                    if count_side == 35:
                        sheet.write(row,0,'Sub Total', border_bot_left)
                        sheet.write(row,1,'', border_bot)
                        sheet.write(row,2,'', border_bot)
                        sheet.write(row,3,'', border_bot)
                        sheet.write(row,4,total_pcs, table_body)
                        sheet.write(row,5,total_kubikasi, border_bot_right)
                        row = row + 1
                        total_pcs = total_kubikasi = 0
                    if count_side == max_perpage:
                        sheet.write(right_row,6,'Sub Total', border_bot_left)
                        sheet.write(right_row,7,'', border_bot)
                        sheet.write(right_row,8,'', border_bot)
                        sheet.write(right_row,9,'', border_bot)
                        if total_pcs == 0:
                            sheet.write(right_row,10,'', table_body)
                        else:
                            sheet.write(right_row,10,total_pcs, table_body)
                        if total_kubikasi == 0:
                            sheet.write(right_row,11,'', border_bot_right)
                        else:
                            sheet.write(right_row,11,total_kubikasi, border_bot_right)
                        right_row = right_row + 1
                        total_pcs = total_kubikasi = 0
                    count_side = count_side + 1
                    if count_side > max_perpage:
                        count_side = 1
                        row = row + 2
        return row