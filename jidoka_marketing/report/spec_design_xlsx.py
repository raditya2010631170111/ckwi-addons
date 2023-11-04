from odoo import models, fields, _
import datetime
import time
from urllib.request import urlopen
import xlwt
import io, base64
from PIL import Image



class ReportSpecDesignXLSX(models.AbstractModel):
    _name = 'report.jidoka_marketing.report_spec_design_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        #import pdb;pdb.set_trace()

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
        
        title_style = workbook.add_format({'font_name': 'Times', 'border':1,'align':'left','valign':'vcenter'})
        header_style = workbook.add_format({'font_name': 'Times', 'bold': True,'align':'center','valign':'vcenter','align': 'center'})
        bold_border_header = workbook.add_format({'border':1,'bold':True,'align':'center','valign':'vcenter'})
        border_desc = workbook.add_format({'border':1,'bold':True,'align':'center','valign':'vcenter','text_wrap': True})
        border_style = workbook.add_format({'border':1,'bold':True,'align':'left','valign':'vcenter'})
        border_note = workbook.add_format({'bold':True,'align':'left','valign':'vcenter', 'right': 1})
        border_note2 = workbook.add_format({'align':'left','valign':'vcenter', 'right': 1})
        bold_border_signature = workbook.add_format({'border':1,'align':'center','valign':'top'})
        border_desc =  workbook.add_format({'bold':True, 'border':1,'align':'center','valign':'top'})
        field_text = workbook.add_format({'valign':'top', 'text_wrap': True})
        bold_underline_format = workbook.add_format({'bold': True, 'underline': True, 'align': 'center', 'left':1, 'right':1, 'top': 1, 'border_color': 'black'})
        center_format = workbook.add_format({'align': 'center', 'left':1, 'right':1, 'bottom': 1, 'border_color': 'black'})
        table_content = workbook.add_format({
            'border':1,
            'align':'left',
            'valign':'top',
            'text_wrap': True,
            'bold': True,
            })
        
        for obj in objects:
            body = workbook.add_format({'bold': True,'border':4,'align':'center','valign':'vcenter','align': 'center'})
            #date_style = workbook.add_format({'text_wrap': True, 'num_format': 'dd-mm-yyyy','align':'left'}) #30/05/2023
            date_style = workbook.add_format({'text_wrap': True, 'num_format': 'dd MMMM yyyy','align':'left'}) #30 May 2023
            sheet = workbook.add_worksheet('Spec Design Excel')
            sheet.set_portrait()
            sheet.set_paper(9)
            sheet.set_margins(0.75,0.75,0.75,0.75)
            sheet.set_column('B:E', 15)
            sheet.set_column(0, 0, width=10)
            sheet.set_column(1, 1, width=1)
            sheet.set_column(5, 5, width=15)
            sheet.set_column(6, 6, width=1)
            sheet.set_row(4, 75)
            sheet.merge_range('A1:I1', 'Specification Design',header_style)
            sheet.write(1, 0, 'To')
            sheet.write(2, 0, 'Deadline')
            sheet.write(3, 0, 'Request No.')
            sheet.write(4, 0, 'Buyer', field_text)
            sheet.write(1, 1, ':')
            sheet.write(2, 1, ':')
            sheet.write(3, 1, ':')
            sheet.write(4, 1, ':', field_text)
            sheet.merge_range(1, 2, 1, 3, obj.partner_team.name or '')
            sheet.merge_range(2, 2, 2, 3, obj.date_deadline,date_style)
            sheet.merge_range(3, 2, 3, 3, obj.request_no)
            sheet.merge_range(4, 2, 4, 3, obj.partner_id.name, field_text)
            sheet.write(1, 5, 'From')
            sheet.write(2, 5, 'Person in Charge')
            sheet.write(3, 5, 'Date')
            sheet.write(4, 5, 'Costumer', field_text)
            sheet.write(1, 6, ':')
            sheet.write(2, 6, ':')
            sheet.write(3, 6, ':')
            sheet.write(4, 6, ':', field_text)
            sheet.write(1, 7, obj.department_id.name)
            sheet.write(2, 7, obj.user_id.name)
            sheet.write(3, 7, obj.create_date,date_style)
            if obj.partner_shipping_id.display_name:
                sheet.merge_range(4, 7, 4, 8, obj.partner_shipping_id.display_name, field_text)
            else:
                if obj.partner_shipping_id.name:
                    sheet.merge_range(4, 7, 4, 8, obj.partner_shipping_id.name, field_text)
                else:
                    sheet.merge_range(4, 7, 4, 8, obj.partner_shipping_id.parent_id.name, field_text)
            size_w, size_h = 1000, 1000
            cell_width = 270
            cell_height = 200
            x_scale = cell_width/size_w
            y_scale = cell_height/size_h
            row = 6
            for line in obj.spec_design_ids:
                sheet.merge_range('A%s:B%s' % (row, row + 1),  "Item No.", bold_border_header)
                sheet.merge_range('C%s:I%s' % (row, row + 1), line.item_id.name,bold_border_header)
                row += 2
                row_desc_start = row
                # sheet.set_row(row - , 50)
                sheet.merge_range('C%s:I%s' % (row, row + 0),line.description,title_style)
                row += 1
                sheet.merge_range('C%s:I%s' % (row, row + 0), "Note:", border_note)
                row += 1
                sheet.merge_range('C%s:I%s' % (row, row + 0),line.note,border_note2)
                row += 1
                if line.attachment :
                    image_buffer, image = resize(line.attachment, (size_w, size_h))
                    sheet.merge_range('C%s:I%s' % (row, row + 0), '',title_style)
                    sheet.insert_image('C%s:I%s'% (row, row + 0), "attachment.png", {
                        'image_data': image_buffer,
                        'x_scale': x_scale,
                        'y_scale': y_scale,
                        'object_position': 1,
                    })
                    sheet.set_row(row - 1, 153) # adjust row height
                    row += 1
                sheet.merge_range('C%s:I%s' % (row, row + 0), 'Reference Design', border_note)
                row += 1
                for i in range(0, len(line.design_image), 2):
                    if line.design_image[i].attachment and (i+1 < len(line.design_image)) and line.design_image[i+1].attachment:
                        # resize the first image
                        image_buffer1, image1 = resize(line.design_image[i].attachment, (size_w, size_h))
                        # resize the second image
                        image_buffer2, image2 = resize(line.design_image[i+1].attachment, (size_w, size_h))
                        # insert both images in the same row
                        sheet.merge_range('C%s:I%s' % (row, row + 0), '',title_style)
                        sheet.insert_image('C%s:I%s' % (row, row +0),  "attachment1.png", {
                            'image_data': image_buffer1,
                            'x_scale': x_scale,
                            'y_scale': y_scale,
                            'object_position': 1,
                        })
                        sheet.merge_range('F%s:I%s' % (row, row + 0), '',title_style)
                        sheet.insert_image('F%s:I%s' % (row, row + 0),  "attachment2.png", {
                            'image_data': image_buffer2,
                            'x_scale': x_scale,
                            'y_scale': y_scale,
                            'object_position': 1,
                        })
                        
                        sheet.set_row(row-1, 153) # adjust row height
                        row += 1
                        sheet.merge_range('C%s:E%s' % (row, row + 0), line.design_image[i].name,title_style)
                        sheet.merge_range('F%s:I%s' % (row, row + 0),line.design_image[i+1].name,title_style)
                        # move to the next row
                        row += 1
                    elif line.design_image[i].attachment:
                        # resize the image
                        image_buffer, image = resize(line.design_image[i].attachment, (size_w, size_h))
                        # insert the image in a new row
                        sheet.merge_range('C%s:E%s' % (row, row + 0), '',title_style)
                        sheet.insert_image('C%s:E%s' % (row, row + 0), "attachment.png", {
                            'image_data': image_buffer,
                            'x_scale': x_scale,
                            'y_scale': y_scale,
                            'object_position': 1,
                        })
                        sheet.set_row(row - 1, 153) # adjust row height
                        row += 1
                        sheet.merge_range('C%s:E%s' % (row, row + 0), line.design_image[i].name,title_style)
                        row += 1
                sheet.merge_range('A%s:B%s' % (row_desc_start, row -1), "Description", border_desc)
                # for line in line.design_image:
                #     if line.attachment:
                #         image_buffer, image = resize(line.attachment, (size_w, size_h))
                #         sheet.insert_image('B%s:B%s'% (row, row + 1), "attachment.png", {
                #             'image_data': image_buffer,
                #             'x_scale': x_scale,
                #             'y_scale': y_scale,
                #             'object_position': 1
                #         })
                #         sheet.set_row(row - 1, 153) # adjust row height
                #         row += 1
                #         sheet.write(row,1,line.name,title_style)
                #         row += 1
            row_material_start = row
            row = row + 1
            for line in obj.detail_material_ids:
            #for index, line in enumerate(obj.detail_material_ids, start=1):
                if line.name or line.name is None:
                    #sheet.merge_range('C%s:I%s' % (row, row + 0), f"{index}.", title_style)
                    sheet.merge_range('C%s:I%s' % (row, row + 0), line.name or '', title_style)
                    row += 1
            sheet.merge_range('A%s:B%s' % (row_material_start, row-1), "Material", bold_border_header)
            row_detail_finish_start = row
            row = row + 1
            for line in obj.detail_finish_ids:
            #for index, line in enumerate(obj.detail_finish_ids, start=1):
                if line.name or line.name is None:
                    #sheet.merge_range('C%s:I%s' % (row, row + 0), f"{index}.", title_style)
                    sheet.merge_range('C%s:I%s' % (row, row + 0), line.name or '', title_style)
                    row += 1
            sheet.merge_range('A%s:B%s' % (row_detail_finish_start, row-1), "Finish", bold_border_header)
            row_special_start = row
            row = row + 0
            for line in obj.spec_design_ids:
            #for index, line in enumerate(obj.spec_design_ids, start=1):
                for line in line.special_ids:
                    if line.note:
                        #sheet.merge_range('C%s:I%s' % (row, row + 0), f"{index}.", title_style)
                        sheet.merge_range('C%s:I%s' % (row, row + 0), line.note,title_style)
                        row += 1
            sheet.merge_range('A%s:B%s' % (row_special_start, row-1), "Special Instruction", bold_border_header)
            # sheet.write(row - 1, 0, "Note",bold_border_header)
            row_other_note_start = row
            for x in obj.spec_design_ids:
                sheet.merge_range('C%s:I%s' % (row, row + 0), x.other_note,title_style)
                row += 1
            sheet.merge_range('A%s:B%s' % (row_other_note_start, row-1), "Note", bold_border_header)
            sheet.merge_range('A%s:I%s' % (row, row + 0), "Authorized Signature",  bold_border_signature)
            row = row + 1
            if obj.signature_pic :
                image_buffer, image = resize(obj.signature_pic, (size_w, size_h))
                sheet.insert_image('A%s:C%s' % (row, row + 0),"signature_pic.png", {'image_data': image_buffer,'x_scale': x_scale,'y_scale': y_scale,'object_position': 1})
                sheet.set_row(row - 1, 153) # adjust row height
                sheet.merge_range('A%s:C%s' % (row, row + 1),'',bold_underline_format)
                row += 1
            elif obj.signature_mar_mangr :    
                image_buffer, image = resize(obj.signature_mar_mangr, (size_w, size_h))
                sheet.insert_image('D%s:F%s' % (row, row + 0),"signature_mar_mangr.png", {'image_data': image_buffer,'x_scale': x_scale,'y_scale': y_scale,'object_position': 1})   
                sheet.set_row(row - 1, 153) # adjust row height
                sheet.merge_range('D%s:F%s' % (row, row + 1),'',bold_underline_format)
                row += 1
            elif obj.signature_rnd :    
                image_buffer, image = resize(obj.signature_rnd, (size_w, size_h))
                sheet.insert_image('G%s:I%s' % (row, row + 0),"signature_rnd.png", {'image_data': image_buffer,'x_scale': x_scale,'y_scale': y_scale,'object_position': 1})
                sheet.set_row(row - 1, 153) # adjust row height
                sheet.merge_range('G%s:I%s' % (row, row + 1),'',bold_underline_format)
                row += 1
            sheet.merge_range('A%s:C%s' % (row, row + 0), obj.signed_pic, bold_underline_format)
            sheet.merge_range('D%s:F%s' % (row, row + 0), obj.signed_mar_mangr, bold_underline_format)
            sheet.merge_range('G%s:I%s' % (row, row + 0), obj.signed_rnd, bold_underline_format)
            row = row + 1
            sheet.merge_range('A%s:C%s' % (row, row + 0),'PIC',center_format)
            sheet.merge_range('D%s:F%s' % (row, row + 0),'MARKETING MANAGER',center_format)
            sheet.merge_range('G%s:I%s' % (row, row + 0),'RND MANAGER',center_format)