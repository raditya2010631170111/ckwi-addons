from odoo import models, fields, api
from datetime import datetime


class StockQuantReport(models.AbstractModel):
    _name = 'report.custom_stock_report.stock_quant_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        # Buat worksheet baru
        worksheet = workbook.add_worksheet('Stock Quant')
        worksheet.set_column(0, 4, 18)      
          # Definisikan format sel
        yellow_format = workbook.add_format({'bg_color': 'yellow','bold': True})
        green = workbook.add_format({'bg_color': 'green','bold': True})

        bold = workbook.add_format({'bold': True})
        #Judul Utama
        # Mendapatkan tanggal saat ini dari filter Odoo tree
        # Mendapatkan tanggal saat ini dari filter Odoo tree
        filter_date = self.env.context.get('filter_date') or fields.Date.context_today(self)

        # Ubah format tanggal ke dalam format yang diinginkan (misalnya, 21 Januari 2023)
        formatted_date = filter_date.strftime('%d %B %Y')
        worksheet.write(0, 0, 'STOK AKHIR BAHAN BAKU PER- ', bold)
        worksheet.write(0, 2, formatted_date, bold)

        # Tulis judul
        worksheet.merge_range(3, 0, 3, 1, 'KETERANGAN', bold)

        # worksheet.write(4, 0, 'KETERANGAN', bold)
        worksheet.write(3, 2, 'M3', bold)
        worksheet.write(3, 3, 'HARGA', bold)
        worksheet.write(3, 4, 'TOTAL', bold)
        #baris baru 
        worksheet.write(5, 0,'BAHAN BAKU KERING', bold)
        # Tulis data stock.quant
        row = 7
        total_quantity = 0 
        t_harga_total= 0
        t_quantity = 0
        t_harga= 0 
        t_quantity_jadi=0
        t_harga_jadi= 0
        t_quantity_wip=0
        t_harga_wip=0
        t_qty=0
        t_hrg=0
        formatted_total_quantity = ''
        formatted_t_harga_total = ''
        formatted_t_quantity = ''
        formatted_t_harga = ''
        formatted_t_qty = ''
        formatted_t_hrg = ''
        formatted_t_quantity_wip = ''
        formatted_t_harga_wip = ''
        
        for quant in objects:
            if quant.location_id.name == 'GD Kayu Kering':
            # if quant.location_id.name == 'Pre-Production':
                total = quant.quantity * quant.product_id.standard_price
                formatted_quantity = format(quant.quantity, ',')
                formatted_standard_price = format(quant.product_id.standard_price, ',')
                formatted_total = format(round(total, 2), ',')
                worksheet.write(row, 0, quant.product_id.name)
                worksheet.write(row, 2, formatted_quantity)
                worksheet.write(row, 3, formatted_standard_price)
                worksheet.write(row, 4, formatted_total)
                # worksheet.write(row, 5, quant.location_id.name)
                row += 1
                total_quantity += quant.quantity 
                t_harga_total += total
                t_quantity += quant.quantity 
                t_harga += total
                t_qty += quant.quantity
                t_hrg += total     
                
                formatted_total_quantity = format(total_quantity, '.5f').replace('.', ',')
                formatted_t_harga_total = format(round(t_harga_total, 2), ',')
                formatted_t_quantity = format(t_quantity, '.5f').replace('.', ',')
                formatted_t_harga = format(round(t_harga, 2), ',')
                formatted_t_qty = format(t_qty, '.5f').replace('.', ',')
                formatted_t_hrg = format(round(t_hrg, 2), ',')

            if total_quantity is not False and t_harga_total is not False:
                worksheet.write(row, 2, formatted_total_quantity, bold)
                worksheet.write(row, 4, formatted_t_harga_total, bold)


        row += 3
        worksheet.write(row, 0, 'BAHAN BAKU BASAH (DI LAPANGAN)', bold)
        row += 2 
        total_quantity = False 
        t_harga_total = False 

        for quant in objects:
            # if quant.location_id.name == 'Pre-Production':
            if quant.location_id.name == 'GD Kayu Basah':
                total = quant.quantity * quant.product_id.standard_price
                formatted_quantity = format(quant.quantity, ',')
                formatted_standard_price = format(quant.product_id.standard_price, ',')
                formatted_total = format(round(total, 2), ',')
                worksheet.write(row, 0, quant.product_id.name)
                worksheet.write(row, 2, formatted_quantity)
                worksheet.write(row, 3, formatted_standard_price)
                worksheet.write(row, 4, formatted_total)
                # worksheet.write(row, 5, quant.location_id.name)
                row += 1
                total_quantity += quant.quantity 
                t_harga_total += total
                t_quantity += quant.quantity 
                t_harga += total
                t_qty += quant.quantity
                t_hrg += total   
                
                formatted_total_quantity = format(total_quantity, '.5f').replace('.', ',')
                formatted_t_harga_total = format(round(t_harga_total, 2), ',')
                formatted_t_quantity = format(t_quantity, '.5f').replace('.', ',')
                formatted_t_harga = format(round(t_harga, 2), ',')
                formatted_t_qty = format(t_qty, '.5f').replace('.', ',')
                formatted_t_hrg = format(round(t_hrg, 2), ',')

            if total_quantity is not False and t_harga_total is not False:
                worksheet.write(row, 2, formatted_total_quantity, bold)
                worksheet.write(row, 4, formatted_t_harga_total, bold)


        row += 3
        worksheet.write(row, 0, 'BAHAN BAKU BASAH (DALAM OVEN)', bold)
        row += 2 
        total_quantity = False 
        t_harga_total = False 

        for quant in objects:
            # if quant.location_id.name == 'Pre-Production':
            if quant.location_id.name == 'GD Kayu Basah':
                total = quant.quantity * quant.product_id.standard_price
                formatted_quantity = format(quant.quantity, ',')
                formatted_standard_price = format(quant.product_id.standard_price, ',')
                formatted_total = format(round(total, 2), ',')
                worksheet.write(row, 0, quant.product_id.name)
                worksheet.write(row, 2, formatted_quantity)
                worksheet.write(row, 3, formatted_standard_price)
                worksheet.write(row, 4, formatted_total)
                # worksheet.write(row, 5, quant.location_id.name)
                row += 1
                total_quantity += quant.quantity 
                t_harga_total += total
                t_quantity += quant.quantity 
                t_harga += total
                t_qty += quant.quantity
                t_hrg += total                  
                
                formatted_total_quantity = format(total_quantity, '.5f').replace('.', ',')
                formatted_t_harga_total = format(round(t_harga_total, 2), ',')
                formatted_t_quantity = format(t_quantity, '.5f').replace('.', ',')
                formatted_t_harga = format(round(t_harga, 2), ',')
                formatted_t_qty = format(t_qty, '.5f').replace('.', ',')
                formatted_t_hrg = format(round(t_hrg, 2), ',')

            if total_quantity is not False and t_harga_total is not False:
                worksheet.write(row, 2, formatted_total_quantity, bold)
                worksheet.write(row, 4, formatted_t_harga_total, bold)

        row += 3
        worksheet.write(row, 0, 'KAYU LOG DI CIPTA', bold)
        row += 2 
        total_quantity = False 
        t_harga_total = False 

        for quant in objects:
            if quant.location_id.name == 'Kayu Log Di Cipta':
            # if quant.location_id.name == 'GD Kayu Basah':
                total = round(quant.quantity * quant.product_id.standard_price, 2)
                formatted_quantity = format(quant.quantity, ',')
                formatted_standard_price = format(quant.product_id.standard_price, ',')
                formatted_total = format(total, ',')
                worksheet.write(row, 0, quant.product_id.name)
                worksheet.write(row, 2, formatted_quantity)
                worksheet.write(row, 3, formatted_standard_price)
                worksheet.write(row, 4, formatted_total)
                # worksheet.write(row, 5, quant.location_id.name)
                row += 1
                total_quantity += quant.quantity 
                t_harga_total += total
                t_quantity += quant.quantity 
                t_harga += total
                t_qty += quant.quantity
                t_hrg += total     
                
                formatted_total_quantity = format(total_quantity, '.5f').replace('.', ',')
                formatted_t_harga_total = format(round(t_harga_total, 2), ',')
                formatted_t_quantity = format(t_quantity, '.5f').replace('.', ',')
                formatted_t_harga = format(round(t_harga, 2), ',')
                formatted_t_qty = format(t_qty, '.5f').replace('.', ',')
                formatted_t_hrg = format(round(t_hrg, 2), ',')

            if total_quantity is not False and t_harga_total is not False:
                worksheet.write(row, 2, formatted_total_quantity, bold)
                worksheet.write(row, 4, formatted_t_harga_total, bold)

        row += 3
        worksheet.write(row, 0, 'KAYU DI IFINDO', bold)
        row += 2 
        total_quantity = False 
        t_harga_total = False 

        for quant in objects:
            if quant.location_id.name == 'Kayu Di Ifindo':
            # if quant.location_id.name == 'GD Kayu Basah':
                total = quant.quantity * quant.product_id.standard_price
                formatted_quantity = format(quant.quantity, ',')
                formatted_standard_price = format(quant.product_id.standard_price, ',')
                formatted_total = format(round(total, 2), ',')
                worksheet.write(row, 0, quant.product_id.name)
                worksheet.write(row, 2, formatted_quantity)
                worksheet.write(row, 3, formatted_standard_price)
                worksheet.write(row, 4, formatted_total)
                # worksheet.write(row, 5, quant.location_id.name)
                row += 1
                total_quantity += quant.quantity 
                t_harga_total += total
                t_quantity += quant.quantity 
                t_harga += total
                t_qty += quant.quantity
                t_hrg += total     
                
                formatted_total_quantity = format(total_quantity, '.5f').replace('.', ',')
                formatted_t_harga_total = format(round(t_harga_total, 2), ',')
                formatted_t_quantity = format(t_quantity, '.5f').replace('.', ',')
                formatted_t_harga = format(round(t_harga, 2), ',')
                formatted_t_qty = format(t_qty, '.5f').replace('.', ',')
                formatted_t_hrg = format(round(t_hrg, 2), ',')

            if total_quantity is not False and t_harga_total is not False:
                worksheet.write(row, 2, formatted_total_quantity, bold)
                worksheet.write(row, 4, formatted_t_harga_total, bold)
        
        row += 2
        worksheet.write(row, 0, 'TOTAL BAHAN BAKU',  yellow_format)
        worksheet.write(row, 1, '',  yellow_format)
        worksheet.write(row, 2, t_quantity,  yellow_format)
        worksheet.write(row, 3, '',  yellow_format)
        worksheet.write(row, 4, t_harga,  yellow_format)

        row += 3
        worksheet.write(row, 0, 'GUDANG MOULDING', bold)
        row += 2 
        total_quantity = False 
        t_harga_total = False 

        for quant in objects:
            if quant.location_id.name == 'GD Molding Komponen':
            # if quant.location_id.name == 'GD Kayu Basah':
                total = quant.quantity * quant.product_id.standard_price
                formatted_quantity = format(quant.quantity, ',')
                formatted_standard_price = format(quant.product_id.standard_price, ',')
                formatted_total = format(round(total, 2), ',')
                worksheet.write(row, 0, quant.product_id.name)
                worksheet.write(row, 2, formatted_quantity)
                worksheet.write(row, 3, formatted_standard_price)
                worksheet.write(row, 4, formatted_total)
                # worksheet.write(row, 5, quant.location_id.name)
                row += 1
                total_quantity += quant.quantity 
                t_harga_total += total
                t_quantity += quant.quantity 
                t_harga += total
                t_qty += quant.quantity
                t_hrg += total     
                
                formatted_total_quantity = format(total_quantity, '.5f').replace('.', ',')
                formatted_t_harga_total = format(round(t_harga_total, 2), ',')
                formatted_t_quantity = format(t_quantity, '.5f').replace('.', ',')
                formatted_t_harga = format(round(t_harga, 2), ',')
                formatted_t_qty = format(t_qty, '.5f').replace('.', ',')
                formatted_t_hrg = format(round(t_hrg, 2), ',')

            if total_quantity is not False and t_harga_total is not False:
                worksheet.write(row, 2, formatted_total_quantity, bold)
                worksheet.write(row, 4, formatted_t_harga_total, bold)

        row += 3
        worksheet.write(row, 0, 'GUDANG 1/2 JADI', bold)
        row += 2 
        total_quantity = False 
        t_harga_total = False 

        for quant in objects:
            if quant.location_id.name == 'GD Setengah Jadi':
            # if quant.location_id.name == 'GD Kayu Basah':
                total = quant.quantity * quant.product_id.standard_price
                formatted_quantity = format(quant.quantity, ',')
                formatted_standard_price = format(quant.product_id.standard_price, ',')
                formatted_total = format(round(total, 2), ',')
                worksheet.write(row, 0, quant.product_id.name)
                worksheet.write(row, 2, formatted_quantity)
                worksheet.write(row, 3, formatted_standard_price)
                worksheet.write(row, 4, formatted_total)
                # worksheet.write(row, 5, quant.location_id.name)
                row += 1
                total_quantity += quant.quantity 
                t_harga_total += total
                t_quantity += quant.quantity 
                t_harga += total
                t_qty += quant.quantity
                t_hrg += total     
                
                formatted_total_quantity = format(total_quantity, '.5f').replace('.', ',')
                formatted_t_harga_total = format(round(t_harga_total, 2), ',')
                formatted_t_quantity = format(t_quantity, '.5f').replace('.', ',')
                formatted_t_harga = format(round(t_harga, 2), ',')
                formatted_t_qty = format(t_qty, '.5f').replace('.', ',')
                formatted_t_hrg = format(round(t_hrg, 2), ',')

            if total_quantity is not False and t_harga_total is not False:
                worksheet.write(row, 2, formatted_total_quantity, bold)
                worksheet.write(row, 4, formatted_t_harga_total, bold)

        row += 3
        worksheet.write(row, 0, 'GUDANG BARANG JADI', bold)
        row += 2 
        total_quantity = False 
        t_harga_total = False 

        for quant in objects:
            if quant.location_id.name == 'GD Barang Jadi':
            # if quant.location_id.name == 'GD Kayu Basah':
                total = quant.quantity * quant.product_id.standard_price
                formatted_quantity = format(quant.quantity, ',')
                formatted_standard_price = format(quant.product_id.standard_price, ',')
                formatted_total = format(round(total, 2), ',')
                worksheet.write(row, 0, quant.product_id.name)
                worksheet.write(row, 2, formatted_quantity)
                worksheet.write(row, 3, formatted_standard_price)
                worksheet.write(row, 4, formatted_total)
                # worksheet.write(row, 5, quant.location_id.name)
                row += 1
                total_quantity += quant.quantity 
                t_harga_total += total
                t_quantity += quant.quantity 
                t_harga += total
                t_qty += quant.quantity
                t_hrg += total     
                
                formatted_total_quantity = format(total_quantity, '.5f').replace('.', ',')
                formatted_t_harga_total = format(round(t_harga_total, 2), ',')
                formatted_t_quantity = format(t_quantity, '.5f').replace('.', ',')
                formatted_t_harga = format(round(t_harga, 2), ',')
                formatted_t_qty = format(t_qty, '.5f').replace('.', ',')
                formatted_t_hrg = format(round(t_hrg, 2), ',')

            if total_quantity is not False and t_harga_total is not False:
                worksheet.write(row, 2, formatted_total_quantity, bold)
                worksheet.write(row, 4, formatted_t_harga_total, bold)

        row += 2
        worksheet.write(row, 0, 'TOTAL BARANG JADI',  yellow_format)
        worksheet.write(row, 1, '',  yellow_format)
        worksheet.write(row, 2, t_quantity_jadi,  yellow_format)
        worksheet.write(row, 3, '',  yellow_format)
        worksheet.write(row, 4, t_harga_jadi,  yellow_format)


        row += 3
        worksheet.write(row, 0, 'WIP', bold)
        row += 2 
        total_quantity = False 
        t_harga_total = False 
    
        worksheet.write(row, 0, 'PEMBAHANAN')
        for quant in objects:
            if quant.location_id.name == 'Pembahanan':
            # if quant.location_id.name == 'GD Kayu Basah':
                total = quant.quantity * quant.product_id.standard_price
                formatted_quantity = format(quant.quantity, ',')
                formatted_standard_price = format(quant.product_id.standard_price, ',')
                formatted_total = format(round(total, 2), ',')
                worksheet.write(row, 0, quant.product_id.name)
                worksheet.write(row, 2, formatted_quantity)
                worksheet.write(row, 3, formatted_standard_price)
                worksheet.write(row, 4, formatted_total)
                # worksheet.write(row, 5, quant.location_id.name)
                row += 1
                total_quantity += quant.quantity 
                t_harga_total += total
                t_quantity += quant.quantity 
                t_harga += total
                t_qty += quant.quantity
                t_hrg += total     
                
                formatted_total_quantity = format(total_quantity, '.5f').replace('.', ',')
                formatted_t_harga_total = format(round(t_harga_total, 2), ',')
                formatted_t_quantity = format(t_quantity, '.5f').replace('.', ',')
                formatted_t_harga = format(round(t_harga, 2), ',')
                formatted_t_qty = format(t_qty, '.5f').replace('.', ',')
                formatted_t_hrg = format(round(t_hrg, 2), ',')

            if total_quantity is not False and t_harga_total is not False:
                worksheet.write(row, 2, formatted_total_quantity, bold)
                worksheet.write(row, 4, formatted_t_harga_total, bold)
        
        
        row += 2 
        total_quantity = False 
        t_harga_total = False 

        worksheet.write(row, 0, 'ASSEMBLING')
        for quant in objects:
            if quant.location_id.name == 'Assembling':
            # if quant.location_id.name == 'GD Kayu Basah':
                total = quant.quantity * quant.product_id.standard_price
                formatted_quantity = format(quant.quantity, ',')
                formatted_standard_price = format(quant.product_id.standard_price, ',')
                formatted_total = format(round(total, 2), ',')
                worksheet.write(row, 0, quant.product_id.name)
                worksheet.write(row, 2, formatted_quantity)
                worksheet.write(row, 3, formatted_standard_price)
                worksheet.write(row, 4, formatted_total)
                # worksheet.write(row, 5, quant.location_id.name)
                row += 1
                total_quantity += quant.quantity 
                t_harga_total += total
                t_quantity += quant.quantity 
                t_harga += total
                t_qty += quant.quantity
                t_hrg += total     
                
                formatted_total_quantity = format(total_quantity, '.5f').replace('.', ',')
                formatted_t_harga_total = format(round(t_harga_total, 2), ',')
                formatted_t_quantity = format(t_quantity, '.5f').replace('.', ',')
                formatted_t_harga = format(round(t_harga, 2), ',')
                formatted_t_qty = format(t_qty, '.5f').replace('.', ',')
                formatted_t_hrg = format(round(t_hrg, 2), ',')

            if total_quantity is not False and t_harga_total is not False:
                worksheet.write(row, 2, formatted_total_quantity, bold)
                worksheet.write(row, 4, formatted_t_harga_total, bold)

        row += 2 
        total_quantity = False 
        t_harga_total = False 

        worksheet.write(row, 0, 'FINISHING')
        for quant in objects:
            if quant.location_id.name == 'Finishing':
            # if quant.location_id.name == 'GD Kayu Basah':
                total = quant.quantity * quant.product_id.standard_price
                formatted_quantity = format(quant.quantity, ',')
                formatted_standard_price = format(quant.product_id.standard_price, ',')
                formatted_total = format(round(total, 2), ',')
                worksheet.write(row, 0, quant.product_id.name)
                worksheet.write(row, 2, formatted_quantity)
                worksheet.write(row, 3, formatted_standard_price)
                worksheet.write(row, 4, formatted_total)
                # worksheet.write(row, 5, quant.location_id.name)
                row += 1
                total_quantity += quant.quantity 
                t_harga_total += total
                t_quantity += quant.quantity 
                t_harga += total
                t_qty += quant.quantity
                t_hrg += total     
                
                formatted_total_quantity = format(total_quantity, '.5f').replace('.', ',')
                formatted_t_harga_total = format(round(t_harga_total, 2), ',')
                formatted_t_quantity = format(t_quantity, '.5f').replace('.', ',')
                formatted_t_harga = format(round(t_harga, 2), ',')
                formatted_t_qty = format(t_qty, '.5f').replace('.', ',')
                formatted_t_hrg = format(round(t_hrg, 2), ',')

            if total_quantity is not False and t_harga_total is not False:
                worksheet.write(row, 2, formatted_total_quantity, bold)
                worksheet.write(row, 4, formatted_t_harga_total, bold)

        row += 2 
        total_quantity = False 
        t_harga_total = False 
        
        worksheet.write(row, 0, 'PACKING')
        for quant in objects:
            if quant.location_id.name == 'Packing':
            # if quant.location_id.name == 'GD Kayu Basah':
                total = quant.quantity * quant.product_id.standard_price
                formatted_quantity = format(quant.quantity, ',')
                formatted_standard_price = format(quant.product_id.standard_price, ',')
                formatted_total = format(round(total, 2), ',')
                worksheet.write(row, 0, quant.product_id.name)
                worksheet.write(row, 2, formatted_quantity)
                worksheet.write(row, 3, formatted_standard_price)
                worksheet.write(row, 4, formatted_total)
                # worksheet.write(row, 5, quant.location_id.name)
                row += 1
                total_quantity += quant.quantity 
                t_harga_total += total
                t_quantity += quant.quantity 
                t_harga += total
                t_qty += quant.quantity
                t_hrg += total     
                
                formatted_total_quantity = format(total_quantity, '.5f').replace('.', ',')
                formatted_t_harga_total = format(round(t_harga_total, 2), ',')
                formatted_t_quantity = format(t_quantity, '.5f').replace('.', ',')
                formatted_t_harga = format(round(t_harga, 2), ',')
                formatted_t_qty = format(t_qty, '.5f').replace('.', ',')
                formatted_t_hrg = format(round(t_hrg, 2), ',')

            if total_quantity is not False and t_harga_total is not False:
                worksheet.write(row, 2, formatted_total_quantity, bold)
                worksheet.write(row, 4, formatted_t_harga_total, bold)

        row += 2
        formatted_t_quantity_wip = format(t_quantity_wip, '.5f').replace('.', ',')
        formatted_t_harga_wip = format(round(t_harga_wip, 2), ',')
        
        worksheet.write(row, 0, 'TOTAL WIP',  yellow_format)
        worksheet.write(row, 1, '',  yellow_format)
        worksheet.write(row, 2, formatted_t_quantity_wip,  yellow_format)
        worksheet.write(row, 3, '',  yellow_format)
        worksheet.write(row, 4, formatted_t_harga_wip,  yellow_format)

        row += 2
        worksheet.write(row, 0, 'TOTAL STOK KAYU',  green)
        worksheet.write(row, 1, '',  green)
        worksheet.write(row, 2, formatted_t_qty,  green)
        worksheet.write(row, 3, '',  green)
        worksheet.write(row, 4, formatted_t_hrg,  green)