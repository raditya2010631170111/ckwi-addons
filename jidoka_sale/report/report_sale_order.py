from odoo import models
import io, base64
from urllib.request import urlopen


class ReportSaleOrderXLSX(models.AbstractModel):
    _name = 'report.jidoka_sale.report_sale_order_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        for obj in objects:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name)
            header = workbook.add_format({'bold': True,'border':6,'align':'center','valign':'vcenter'})
            body = workbook.add_format({'border':6,'align':'center','valign':'vcenter'})
            sheet.merge_range(3, 0, 4, 0, "No", header)
            sheet.merge_range(3, 1, 4, 1, "PICTURE", header)
            sheet.merge_range(3, 2, 4, 2, "ITEM NO#", header)
            sheet.merge_range(3, 3, 4, 3, "ASSEMBLY SIZE", header)
            sheet.merge_range(3, 4, 4, 4, "MATERIAL FINISHING", header)
            # sheet.merge_range(3, 5, 4, 5, "QTY", header)
            # sheet.merge_range(3, 6, 4, 6, "WOOD", header)
            # sheet.merge_range(3, 7, 4, 7, "WOOD PRICE", header)
            # sheet.merge_range(3, 8, 4, 8, "LABOUR", header)
            # sheet.merge_range(3, 9, 4, 9, "15%", header)
            # sheet.merge_range(3, 10, 4, 10, "PAINT", header)
            # sheet.merge_range(3, 11, 4, 11, "PACKING", header)
            # sheet.merge_range(3, 12, 4, 12, "HARD", header)
            # sheet.merge_range(3, 13, 4, 13, "35%", header)
            # sheet.merge_range(3, 14, 4, 14, "SP HDR", header)
            # sheet.merge_range(3, 15, 4, 15, "CUSHION/CANVAS", header)
            # sheet.merge_range(3, 16, 4, 16, "15%", header)
            # sheet.merge_range(3, 17, 4, 17, "LOAD", header)
            # sheet.merge_range(3, 18, 4, 18, "TOTAL COST", header)
            # sheet.write(3, 19, "WOOD PRICE", header)
            # sheet.write(4, 19, "PRICE", header)
            # sheet.write(3, 20, "MARGIN", header)
            # sheet.write(4, 20, "PRICE", header)
            # sheet.write(3, 21, "NET PRICE", header)
            # sheet.write(4, 21, "FOB PRICE", header)
            # sheet.write(3, 22, "SET PRICE", header)
            # sheet.write(4, 22, "FOB PRICE", header)
            sheet.merge_range(3, 5, 3, 6, "WILLIAM", header)
            sheet.write(4, 5, "SET PRICE", header)
            sheet.write(4, 6, "FOB PRICE", header)
            sheet.merge_range(3, 7, 4, 8, "PACKING SIZE ( Carton Size )", header)
            sheet.write(4, 9, "QTY / CTN", header)
            sheet.write(4, 10, "CU FT", header)
            sheet.write(4, 11, "40' (PCS)", header)
            sheet.write(4, 12, "40' HQ (PCS)", header)
            sheet.write(4, 13, "MOQ", header)
            row = 5
            idx = 1
            for line in obj.order_line:
                sheet.write(row,0,idx,body)
                if line.attachment:
                    image_data = io.BytesIO(base64.b64decode(line.attachment))
                    sheet.insert_image(row,1,'attachment.png',{'image_data': image_data})
                else:
                    sheet.write(row,1,'',body)
                sheet.write(row,2,line.name,body)
                sheet.write(row,3,line.assembly_size,body)
                # sheet.write(row,4,line.material_finishing,body)
                sheet.write(row,4,line.material_finish_id.name,body)
                # sheet.write(row,5,line.wood,body)
                # sheet.write(row,6,line.wood_price,body)
                # sheet.write(row,7,line.labour,body)
                # sheet.write(row,8,line.wood_15,body)
                # sheet.write(row,9,line.paint,body)
                # sheet.write(row,10,line.packing,body)
                # sheet.write(row,11,line.hard,body)
                # sheet.write(row,12,line.hd_35,body)
                # sheet.write(row,13,line.spesial_hardware,body)
                # sheet.write(row,14,line.canvas,body)
                # sheet.write(row,15,line.canvas_15,body)
                # sheet.write(row,16,line.load,body)
                # sheet.write(row,17,line.total_cost,body)
                # sheet.write(row,18,line.total_wood_price,body)
                # sheet.write(row,19,line.total_margin_price,body)
                # sheet.write(row,20,line.total_net_price,body)
                # sheet.write(row,21,line.total_set_price,body)
                # sheet.write(row,22,line.william_fob_price,body)
                sheet.write(row,5,line.william_set_price,body)
                sheet.write(row,6,line.packing_size_p,body)
                sheet.write(row,7,line.packing_size_l,body)
                sheet.write(row,8,line.packing_size_t,body)
                sheet.write(row,9,line.qty_carton,body)
                sheet.write(row,10,line.cu_ft,body)
                sheet.write(row,11,line.inch_40,body)
                sheet.write(row,12,line.inch_40_hq,body)
                sheet.write(row,13,line.moq,body)
                row = row + 1
