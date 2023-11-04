from odoo import _, api, fields, models

class InvoiceXlsx(models.AbstractModel):
    _name = 'report.jidoka_export.report_invoice_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, invoice):
        
        border_top = workbook.add_format({'align': 'left'})
        border_top.set_top(1)
        border_bottom = workbook.add_format({'align': 'left'})
        border_bottom.set_bottom(1)
        bold_border = workbook.add_format({'bold': True,'valign': 'vcenter'})  
        bold_border.set_top(1)
        bold_border.set_bottom(2)
        bold_border2 = workbook.add_format({'bold': True,'align': 'center','valign': 'vcenter'}) 
        bold_border2.set_top(1)
        bold_border2.set_bottom(1)
        header_title_center = workbook.add_format({'bold': True, 'font_size': 15, 'align': 'center', 'valign': 'vcenter'})
        header_title_center.set_border_color('#000000')
        header_title_center.set_top(1)
        header_title_center.set_bottom(1)
        header = workbook.add_format({'align':'center','valign':'vcenter'})
        bold_header = workbook.add_format({'bold':True,'align': 'center','valign': 'vcenter'})
        text_center = workbook.add_format({'align':'center'}) 
        text_left = workbook.add_format({'align':'left'}) 
        text_right1 = workbook.add_format({'align':'right'})
        text_right2 = workbook.add_format({'align':'right'}) 
        text_right = workbook.add_format({'align':'right'}) 
        text_right1.set_top(1)
        text_right2.set_bottom(1)

        for obj in invoice: 
            invoice_no = f": {obj.name}" if obj.name else ':'
            invoice_date = f": {obj.invoice_date.strftime('%d.%m.%Y')}" if obj.invoice_date else ':'
            # invoice_amount = f": {obj.amount_total}" if obj.amount_total else ':'
            sc_no = obj.no_sc_ids if obj.no_sc_ids else ''
            sc_no_join = ', '.join(sc_no.mapped('name')) if sc_no else ''
            sc_no_join = f": {sc_no_join}" if sc_no else ':'
            
            to_partner_messr = f": {obj.to_partner_id.name}" if obj.to_partner_id else ': '
            
            messr_city = f"  {obj.to_partner_id.city}" if obj.to_partner_id.city else '  '
            messr_country = obj.to_partner_id.country_id.name if obj.to_partner_id else ''
            messr_city_country = messr_city +', '+ messr_country
            
            vessel = f": {obj.vessel}" if obj.vessel else ':'
            onboard_date = f": {obj.onboard_date.strftime('%d.%m.%Y')}" if obj.onboard_date else ':'
            
            from_invoice_city = f": {obj.from_invoice_city}" if obj.from_invoice_city else ':'
            from_invoice_country = obj.from_invoice_country_id.name if obj.from_invoice_country_id.name else ':'
            from_invoice_city_country = from_invoice_city +', '+ from_invoice_country
            
            to_invoice_city = f": {obj.to_invoice_city}" if obj.to_invoice_city else ':'
            to_invoice_country_state = obj.to_invoice_country_state_id.name if obj.to_invoice_country_state_id.name else ''
            to_invoice_country = obj.to_invoice_country_id.name if obj.to_invoice_country_id.name else ''
            to_invoice_city_country = to_invoice_city +', '+ to_invoice_country_state+', '+to_invoice_country
            
            fob_term = obj.fob_term_id.name if obj.fob_term_id.name else ':'
            fob_from = fob_term +', '+from_invoice_city_country
            
            
            
            sheet = workbook.add_worksheet(invoice_no[:31])
            # HEADER
            sheet.merge_range('B1:H1', obj.env.company.name, bold_header)
            sheet.merge_range('B2:H2', _('%s - %s')%( obj.env.company.street, obj.env.company.zip), header)
            sheet.merge_range('B3:H3', _('%s - %s') %(obj.env.company.state_id.name,obj.env.company.country_id.name), header)      
            sheet.merge_range('B4:H4', '>>>>>      COMMERCIAL INVOICE      <<<<<', header_title_center)
            # ============================================            
            
            
            # worksheet = workbook.add_worksheet(obj.name)
            # KOLOM
            sheet.set_column('A:A', 1)
            sheet.set_column('B:B', 35)
            sheet.set_column('C:C', 35)
            sheet.set_column('D:D', 35)
            sheet.set_column('E:E', 20)
            sheet.set_column('F:F', 35)
            sheet.set_column('G:G', 35)
            sheet.set_column('H:H', 20)  
            sheet.set_row(11, 25)
            
            sheet.write(4, 1, "INVOICE NO",border_top)
            sheet.write(4, 2, invoice_no,border_top)
            sheet.write(4, 3, "SALES ",text_right1)
            sheet.write(4, 4, "CONFIRMATION NO :",border_top)
            sheet.write(4, 5, sc_no_join,border_top)
            sheet.write(4, 6, '',border_top)
            sheet.write(4, 7, '',border_top)
            
            sheet.write(5, 1, "INVOICE DATE",border_bottom)
            sheet.write(5, 2, invoice_date,border_bottom)
            sheet.write(5, 3, '',border_bottom)
            sheet.write(5, 4, '',border_bottom)
            sheet.write(5, 5, '',border_bottom)
            sheet.write(5, 6, '',border_bottom)
            sheet.write(5, 7, '',border_bottom)
            
            sheet.write(6, 1, "MESSR",border_top)
            sheet.write(6, 2, to_partner_messr,border_top)
            sheet.write(6, 3, '',border_top)
            sheet.write(6, 4, '',border_top)
            sheet.write(6, 5, '',border_top)
            sheet.write(6, 6, '',border_top)
            sheet.write(6, 7, '',border_top)
            # sheet.write(8, 1, messr_street)
            sheet.write(7, 2, messr_city_country)
            sheet.write(8, 1, '',border_bottom)
            sheet.write(8, 2, '',border_bottom)
            sheet.write(8, 3, '',border_bottom)
            sheet.write(8, 4, '',border_bottom)
            sheet.write(8, 5, '',border_bottom)
            sheet.write(8, 6, '',border_bottom)
            sheet.write(8, 7, '',border_bottom)

            sheet.write(9, 1, "VESSEL",border_top)
            sheet.write(9, 2, vessel,border_top)
            sheet.write(9, 3, '',border_top)
            sheet.write(9, 4, '',border_top)
            sheet.write(9, 5, "FROM",text_right1)
            sheet.write(9, 6, from_invoice_city_country,border_top)
            sheet.write(9, 7, '',border_top)
            
            sheet.write(10, 1, "ONBOARD",border_bottom)
            sheet.write(10, 2, onboard_date,border_bottom)
            sheet.write(10, 3, '',border_bottom)
            sheet.write(10, 4, '',border_bottom)
            sheet.write(10, 5, "TO",text_right2)
            sheet.write(10, 6, to_invoice_city_country,border_bottom)
            sheet.write(10, 7, '',border_bottom)
            
            sheet.write(11, 1, "ITEM NO",bold_border2)
            sheet.write(11, 2, "SKU",bold_border2)
            sheet.write(11, 3, "DESCRIPTION",bold_border2)
            sheet.write(11, 4, "QTY",bold_border2)
            sheet.write(11, 5, '',bold_border2)
            sheet.write(11, 6, "UNIT PRICE",bold_border2)
            sheet.write(11, 7, "AMOUNT",bold_border2)
            
            for i in range(0, 8):  # Loop through columns 0 to 7 (inclusive)
                    sheet.write(15, i, '')
                    # sheet.write(row + 4, i, '', bold_border)
            
            sheet.write(12, 0, '')
            sheet.write(12, 1, '')
            sheet.write(12, 2, '')
            sheet.write(12, 3, fob_from)
            sheet.write(12, 4, '')
            sheet.write(12, 5, '')

            row = 13
            for cp in obj.invoice_container_operation_ids:
                sc_no = cp.picking_ids if cp.picking_ids else ''
                # sc_no_join = " ".join(sc_no.split())
                picking_names = ', '.join([picking.name for picking in sc_no])
                container_no = cp.container_no if cp.container_no else ''
                seal_no = cp.seal_no if cp.seal_no else ''
                buyer_po = cp.buyer_po if cp.buyer_po else ''
                
                sheet.write(row+2,3,f"CONTAINER NO.# {container_no}")
                sheet.write(row+3,3,f"SEAL NO.# {seal_no}")
                sheet.write(row+5,3,f"PO.NO: {buyer_po}")
                sheet.write(row+6,3,f"SJ.NO: {picking_names}")
                
                for i in range(0, 8):  # Loop through columns 0 to 7 (inclusive)
                    sheet.write(row, i, '')
                    sheet.write(row+1, i, '')
                    sheet.write(row + 3, i, '')
                
                row += 7
                
                for line in cp.invoice_container_operation_line_ids:
                    product = line.product_id.name if line.product_id else ''
                    sku = line.sku if line.sku else ''
                    qty_container = line.product_container_qty if line.product_container_qty else ''
                    unit_price = line.unit_price if line.unit_price else ''
                    amount = line.amount if line.amount else ''
                    
                    sheet.write(row, 1, product)
                    sheet.write(row, 2, sku)
                    sheet.write(row, 3, '')
                    sheet.write(row, 4, qty_container,text_left)
                    sheet.write(row, 5, f"PCS")
                    sheet.write(row, 6, "{:,.2f}".format(unit_price))
                    sheet.write(row, 7, "{:,.2f}".format(amount))
                    # sheet.write(row, 5, amount,bold_border)
                    row += 1
                
                # f"{angka:,.3f}"
                
            sheet.write(row+1, 1, '',bold_border)  
            sheet.write(row+1, 2, '',bold_border) 
            sheet.write(row+1, 3, '',bold_border)  
            sheet.write(row+1, 4, f"****GRAND TOTAL****",bold_border)  
            sheet.write(row+1, 5, '',bold_border)   
            sheet.write(row+1, 6, '',bold_border)   
            # sheet.write(row+1, 5, obj.total_amount,bold_border) 
            sheet.write(row+1, 7, "{:,.2f}".format(obj.total_amount),bold_border)
            
            for i in range(0,8):
                sheet.write(row, i, '')
                
            # row += 4
            # sheet.merge_range(row,7,row,8,obj.env.company.name,text_center)
            # row += 8
            # sheet.write(row,7,f"(")
            # sheet.write(row,8,f")",text_right)
            # row += 1
            # sheet.merge_range(row,7,row,8,f"AUTHORIZED SIGNATURE",text_center)