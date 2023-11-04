# -*- coding: utf-8 -*-
from odoo import models, _
import io, base64
from PIL import Image

class ReportSampleRequestXLSX(models.AbstractModel):
    _name = 'report.jidoka_crm_sample_request.report_sample_request_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        def buffer_image(image: Image):
            # Store image in buffer, so we don't have to write it to disk.
            buffer = io.BytesIO()
            image.save(buffer, 'png')
            return buffer, image

        def resize(gambar, size):
            image = Image.open(io.BytesIO(
                base64.b64decode(gambar)))
            image = image.resize(size)
            return buffer_image(image)

        for obj in objects:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name)
            # styling
            bold_header = workbook.add_format({'bold':True,'align':'center','valign':'vcenter'})
            bold_border_header = workbook.add_format({'border':1,'bold':True,'align':'center','valign':'vcenter'})
            bold_border_header.set_border_color('#000000')
            header = workbook.add_format({'align':'center','valign':'vcenter'})
            table_header = workbook.add_format({'border':1,'align':'center','valign':'vcenter'})
            table_remark = workbook.add_format({'border':1,'align':'left','valign':'vcenter','text_wrap': True})
            buyer_style = workbook.add_format({'align':'left','valign':'vcenter','text_wrap': True})
            table_content = workbook.add_format({
                'border':1,
                'align':'left',
                'valign':'top',
                'text_wrap': True,
                'bold': True,
            })
            table_content_center = workbook.add_format({
                'border':1,
                'align':'center',
                'valign':'top',
                'text_wrap': True,
                'bold': True,
            })
            table_content_center2 = workbook.add_format({'border':1,'align':'left','valign':'vcenter','text_wrap': True,'bold': True})
            body = workbook.add_format({'border':1,'align':'center','valign':'vcenter'})
            body_min = workbook.add_format({'align':'center','valign':'vcenter'})
            date_format = workbook.add_format({'num_format': 'dd-MMM-yyyy', 'align': 'left'})
            date_format.set_right(1)  
            left_align = workbook.add_format({'align': 'left'})
            left_align.set_right(1)  
            left_align2 = workbook.add_format({'align': 'left'})
            border_right = workbook.add_format()
            border_right.set_right()
            border_left = workbook.add_format()
            border_left.set_left()
            ttd_format_center = workbook.add_format({'bold': True,'underline':True,'italic':True,'align':'center'})
            sheet.merge_range('A1:I1', obj.env.company.name, bold_header)
            sheet.merge_range('A3:I3', _('%s - %s')%( obj.env.company.street, obj.env.company.zip), header)
            sheet.merge_range('A4:I4', _('%s - %s') %(obj.env.company.state_id.name,obj.env.company.country_id.name), header)
            # sheet.merge_range('A5:I5', _('TEL : %s FAX : %s')%(obj.env.company.phone,obj.env.company.vat), header)
            sheet.merge_range('A5:I5', _('TEL : %s FAX : %s')%(obj.env.company.phone,obj.env.company.fax), header)
            sheet.write('G6','Page: 1  Of:1')
            sheet.merge_range('A7:I7', 'SAMPLE REQUEST', bold_border_header)
            sheet.write('A8','To :', border_left)
            sheet.merge_range('B8:E8',obj.partner_team.name,left_align2)
            sheet.merge_range('F8:G8','From :')
            sheet.merge_range('H8:I8',obj.department_id.name,left_align)
            sheet.write('A9','Request No. :', border_left)
            sheet.merge_range('B9:E9',obj.name,left_align2)
            sheet.merge_range('F9:G9','Date Issued :')
            sheet.merge_range('H9:I9',obj.date_issued,date_format)
            sheet.write('A10','Buyer :', border_left)
            sheet.write('A11','', border_left)
            if obj.partner_id.name:
                sheet.merge_range('B10:E11', obj.partner_id.name, buyer_style)
            elif obj.partner_id.parent_id.name and obj.partner_id.name:
                sheet.merge_range('B10:E11', f"{obj.partner_id.parent_id.name}, {obj.partner_id.name}", buyer_style)
            elif obj.partner_id.parent_id.name and obj.partner_id.type:
                sheet.merge_range('B10:E11', f"{obj.partner_id.parent_id.name}, {obj.partner_id.type}", buyer_style)
            sheet.merge_range('F10:G10','Deadline :')
            sheet.merge_range('H10:I10',obj.date_deadline,date_format)
            sheet.write('I11','',border_right)
            sheet.write('A12','Purpose :',border_left)
            sheet.merge_range('B12:E12',obj.purpose,left_align2)
            sheet.merge_range('F11:I11','',border_right)
            sheet.merge_range('F12:I12','',border_right)
            # table header
            sheet.write('A13','Item No.',table_header)
            sheet.merge_range('B13:F13','Description',table_header)
            sheet.write('G13','Qty',table_header)
            sheet.merge_range('H13:I13','Remark',table_header)
            row = 14
            # set default size (di standarkan)
            size_w, size_h = 675, 500
            size_w2, size_h2 = 330, 250
            # ukuran cell
            cell_width = 135
            cell_height = 100
            cell_width2 = 70
            cell_height2 = 50
            x_scale = cell_width/size_w
            y_scale = cell_height/size_h
            x_scale2 = cell_width2/size_w2
            y_scale2 = cell_height2/size_h2
            for line in obj.line_ids:
                sheet.merge_range('A%s:A%s' % (row, row + 2), line.product_id.name, table_content)
                sheet.merge_range('B%s:F%s' % (row, row + 2), line.description or '', table_content)
                sheet.merge_range('G%s:G%s' % (row, row + 2), '%s %s' % (line.qty, line.uom_id.name), table_content_center)
                remark_lines = line.remark.strip().splitlines() if line.remark else []
                sheet.merge_range('H%s:I%s' % (row, row + 2), '\n'.join(remark_lines), table_content)
                sheet.set_row(row - 1, 14) # adjust row height
                row += 1
                if line.attachment:
                    image_buffer, image = resize(line.attachment, (size_w, size_h))
                    sheet.insert_image('B%s' % row, "attachment.png", {
                        'image_data': image_buffer,'x_scale': x_scale,'y_scale': y_scale,'object_position': 1, 'options': {'x_offset': 5, 'y_offset': 5}
                    })
                    sheet.set_row(row - 1, 76) # adjust row height
                if line.attachment2:
                    image_buffer, image = resize(line.attachment2, (size_w, size_h))
                    sheet.insert_image('D%s' % row, "attachment2.png", {
                       'image_data': image_buffer,'x_scale': x_scale,'y_scale': y_scale,'object_position': 1, 'options': {'x_offset': 5, 'y_offset': 5}
                    })
                    sheet.set_row(row - 1, 76)
                row += 1
                if line.attachment3:
                    image_buffer, image = resize(line.attachment3, (size_w, size_h))
                    sheet.insert_image('B%s' % row, "attachment3.png", {
                       'image_data': image_buffer,'x_scale': x_scale,'y_scale': y_scale,'object_position': 1, 'options': {'x_offset': 5, 'y_offset': 5}
                    })
                    sheet.set_row(row - 1, 76)
                    row += 1
                else:
                    row += 1
            sheet.write(row - 1,0,'MATERIAL',table_content_center2)
            material_name = obj.material_ids and ", ".join([x.name for x in obj.material_ids]) or ''
            sheet.merge_range(row - 1,1,row - 1,5,'%s' % material_name,table_content_center2)
            sheet.write(row - 1,6,'',table_header)
            sheet.merge_range(row - 1,7,row - 1,8,'',table_header)
            row = row + 1
            sheet.write(row - 1,0,'FINISH',table_content_center2)
            sheet.merge_range(row - 1,1,row - 1,5,obj.detail_finish_ids.name,table_content_center2)
            sheet.write(row - 1,6,'',table_header)
            sheet.merge_range(row - 1,7,row - 1,8,'',table_header)
            row = row + 1
            sheet.write(row - 1,0,'NOTES',table_content_center2)
            sheet.merge_range(row - 1,1,row - 1,5,obj.internal_notes,table_content_center2)
            sheet.write(row - 1,6,'',table_header)
            sheet.merge_range(row - 1,7,row - 1,8,'',table_header)
            row = row + 1
            sheet.merge_range(row,0,row,2,'R&D MANAGER',ttd_format_center)
            sheet.merge_range(row,3,row,4,'R&D DEPT.',ttd_format_center)
            sheet.merge_range(row,5,row,6,'MARKETING MANAGER',ttd_format_center)
            sheet.merge_range(row,7,row,8,'MARKETING DEPT.',ttd_format_center)
            row = row + 2
            if obj.ttd_rnd_manager:
                image_buffer, image = resize(obj.ttd_rnd_manager, (size_w2, size_h2))
                sheet.insert_image('B%s:C%s' % (row, row), "ttd_rnd_manager.png", {
                    'image_data': image_buffer,'x_scale': x_scale2,'y_scale': y_scale2,'object_position': 1,'options': {'x_offset': 10, 'y_offset': 10}
                })
                sheet.set_row(row - 1, 40)
            if obj.ttd_rnd_department:
                image_buffer, image = resize(obj.ttd_rnd_department, (size_w2, size_h2))
                sheet.insert_image('D%s:E%s' % (row, row), "ttd_rnd_department.png", {
                    'image_data': image_buffer,'x_scale': x_scale2,'y_scale': y_scale2,'object_position': 1,'options': {'x_offset': 10, 'y_offset': 10}
                })
                sheet.set_row(row - 1, 40)
            if obj.ttd_marketing_manager:
                image_buffer, image = resize(obj.ttd_marketing_manager, (size_w2, size_h2))
                sheet.insert_image('F%s:G%s' % (row, row), "ttd_marketing_manager.png", {
                    'image_data': image_buffer,'x_scale': x_scale2,'y_scale': y_scale2,'object_position': 1,'options': {'x_offset': 10, 'y_offset': 10}
                })
                sheet.set_row(row - 1, 40)
            if obj.ttd_marketing_department:
                image_buffer, image = resize(obj.ttd_marketing_department, (size_w2, size_h2))
                sheet.insert_image('H%s:I%s' % (row, row), "ttd_marketing_department.png", {
                    'image_data': image_buffer,'x_scale': x_scale2,'y_scale': y_scale2,'object_position': 1,'options': {'x_offset': 10, 'y_offset': 10}
                })
                sheet.set_row(row - 1, 40)
            sheet.merge_range(row,0,row,2,obj.name_rnd_manager,ttd_format_center)
            sheet.merge_range(row,3,row,4,obj.name_rnd_department,ttd_format_center)
            sheet.merge_range(row,5,row,6,obj.name_marketing_manager,ttd_format_center)
            sheet.merge_range(row,7,row,8,obj.name_marketing_department,ttd_format_center)