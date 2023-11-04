from odoo import models, _
class PackingListXlsx(models.AbstractModel):
    _name = 'report.jidoka_export.report_packing_list_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, packing_list):
        bold = workbook.add_format({'bold': True})
        # border = workbook.add_format({'border': 1})  
        # border = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter','text_wrap':True,})
        border_top = workbook.add_format({'align': 'left'})
        border_top.set_top(1)
        border_bottom = workbook.add_format({'align': 'left'})
        border_bottom.set_bottom(1)
        bold_border = workbook.add_format({'bold': True,'valign': 'vcenter','align':'left'})  
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
        text_center.set_bottom(1)
        text_left = workbook.add_format({'align':'left'}) 
        text_right1 = workbook.add_format({'align':'right'})
        text_right2 = workbook.add_format({'align':'right'}) 
        text_right1.set_top(1)
        text_right2.set_bottom(1)

        for obj in packing_list:
            invoice_date = f": {obj.invoice_date.strftime('%d.%m.%Y')}" if obj.invoice_date else ':'
            onboard_date = f": {obj.onboard_date.strftime('%d.%m.%Y')}" if obj.onboard_date else ':'
            # onboard_date = obj.onboard_date.strftime("%d.%m.%Y") if obj.onboard_date else ':'
            
            container_index = 0  # Initialize the container index counter
            

            report_name = f": {obj.name}" if obj.name else ':'
            vessel = f": {obj.vessel}" if obj.vessel else ':'
            # no_sc_ids = f"{obj.no_sc_ids}" if obj.no_sc_ids else ''
            # no_sc_ids = obj.no_sc_ids if obj.no_sc_ids else []
            no_sc_ids = obj.no_sc_ids if obj.no_sc_ids else []
            from_packing_city = f": {obj.from_packing_city}" if obj.from_packing_city else ':'
            from_packing_country_id = f"{obj.from_packing_country_id.name}" if obj.from_packing_country_id.name else ''
            to_packing_city = f": {obj.to_packing_city}" if obj.to_packing_city else ':'
            to_packing_country_id = f" {obj.to_packing_country_id.name}" if obj.to_packing_country_id else ''

            # no_sc_ids_value = ', '.join([str(sc.name) for sc in no_sc_ids])
            no_sc_ids_value = ', '.join(no_sc_ids.mapped('name')) if no_sc_ids else ''

            no_sc_ids_value = f": {no_sc_ids_value}" if no_sc_ids_value else ':'
            messr_name = f": {obj.to_partner_id.name}" if obj.to_partner_id.name else ''
            messr_street = f"  {obj.to_partner_id.street}" if obj.to_partner_id.street else ''
            messr_city = f"  {obj.to_partner_id.city}" if obj.to_partner_id.city else ''
            messr_country = f"{obj.to_partner_id.country_id.name}" if obj.to_partner_id.country_id.name else ''
            messr_city_country = f"{messr_city}, {messr_country}" if messr_city else ''

            from_city_country = f"{from_packing_city}, {from_packing_country_id}"
            to_city_country = f"{to_packing_city}, {to_packing_country_id}"
            total_qty_pcs = int(obj.total_qty_pcs) if obj.total_qty_pcs else ''
            total_qty_set = int(obj.total_qty_set) if obj.total_qty_set else ''
            total_pack = obj.total_pack if obj.total_pack else ''
            total_net_wght = obj.total_net_wght if obj.total_net_wght else ''
            total_gross_wght = obj.total_gross_wght if obj.total_gross_wght else ''
            total_means = obj.total_means if obj.total_means else ''
            
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name[:31])

            sheet.merge_range('B1:K1', obj.env.company.name, bold_header)
            sheet.merge_range('B2:K2', _('%s - %s')%( obj.env.company.street, obj.env.company.zip), header)
            sheet.merge_range('B3:K3', _('%s - %s') %(obj.env.company.state_id.name,obj.env.company.country_id.name), header)
            
            sheet.merge_range('B4:K4', '>>>>>      PACKING LIST      <<<<<', header_title_center)
            sheet.set_column('A:A', 1)
            sheet.set_column('B:B', 40)
            sheet.set_column('C:C', 35)
            sheet.set_column('D:D', 35)
            sheet.set_column('E:E', 5)
            sheet.set_column('G:G', 20)
            sheet.set_column('H:H', 25)
            sheet.set_row(11, 25)

            # sheet.write(0, 0, "PACKING LIST", bold)
            sheet.write(4, 1, "INVOICE NO",border_top)
            sheet.write(4, 2, report_name,border_top)
            sheet.write(4, 3, '',border_top)
            sheet.write(4, 4, '',border_top)
            sheet.write(4, 5, '',border_top)
            sheet.write(4, 6, "SALES CONFIRMATION NO    :",border_top)
            sheet.write(4, 7, no_sc_ids_value,border_top)
            sheet.write(4, 8, '',border_top)
            sheet.write(4, 9, '',border_top)
            sheet.write(4, 10, '',border_top)
            
            sheet.write(5, 1, "INVOICE DATE",border_bottom)
            sheet.write(5, 2, invoice_date,border_bottom)
            sheet.write(5, 3, '',border_bottom)
            sheet.write(5, 4, '',border_bottom)
            sheet.write(5, 5, '',border_bottom)
            sheet.write(5, 6, '',border_bottom)
            sheet.write(5, 7, '',border_bottom)
            sheet.write(5, 8, '',border_bottom)
            sheet.write(5, 9, '',border_bottom)
            sheet.write(5, 10, '',border_bottom)
            
            sheet.write(6, 1, "MESSR",border_top)
            sheet.write(6, 2, messr_name,border_top)
            sheet.write(6, 3, '',border_top)
            sheet.write(6, 4, '',border_top)
            sheet.write(6, 5, '',border_top)
            sheet.write(6, 6, '',border_top)
            sheet.write(6, 7, '',border_top)
            sheet.write(6, 8, '',border_top)
            sheet.write(6, 9, '',border_top)
            sheet.write(6, 10, '',border_top)
            sheet.write(7, 2, messr_street)
            sheet.write(8, 1, '',border_bottom)
            sheet.write(8, 2, messr_city_country,border_bottom)
            sheet.write(8, 3, '',border_bottom)
            sheet.write(8, 4, '',border_bottom)
            sheet.write(8, 5, '',border_bottom)
            sheet.write(8, 6, '',border_bottom)
            sheet.write(8, 7, '',border_bottom)
            sheet.write(8, 8, '',border_bottom)
            sheet.write(8, 9, '',border_bottom)
            sheet.write(8, 10, '',border_bottom)

            sheet.write(9, 1, "VESSEL",border_top)
            sheet.write(9, 2, vessel,border_top)
            sheet.write(9, 3, '',border_top)
            sheet.write(9, 4, '',border_top)
            sheet.write(9, 5, '',border_top)
            sheet.write(9, 6, "FROM",text_right1)
            sheet.write(9, 7, from_city_country,border_top)
            sheet.write(9, 8, '',border_top)
            sheet.write(9, 9, '',border_top)
            sheet.write(9, 10, '',border_top)
            
            sheet.write(10, 1, "ONBOARD",border_bottom)
            sheet.write(10, 2, onboard_date,border_bottom)
            sheet.write(10, 3, '',border_bottom)
            sheet.write(10, 4, '',border_bottom)
            sheet.write(10, 5, '',border_bottom)
            sheet.write(10, 6, "TO",text_right2)
            sheet.write(10, 7, to_city_country,border_bottom)
            sheet.write(10, 8, '',border_bottom)
            sheet.write(10, 9, '',border_bottom)
            sheet.write(10, 10, '',border_bottom)

            sheet.write(11, 1, "ITEM NO.", bold_border2)
            sheet.write(11, 2, "SKU", bold_border2)
            sheet.write(11, 3, "DESCRIPTION", bold_border2)
            sheet.write(11, 4, "QTY", bold_border2)
            sheet.write(11, 5, '', bold_border2)
            sheet.write(11, 6, "PACK (CTN)", bold_border2)
            sheet.write(11, 7, '', bold_border2)
            sheet.write(11, 8, "N.W (KGS)", bold_border2)
            sheet.write(11, 9, "G.W (KGS)", bold_border2) 
            sheet.write(11, 10, "MEANS (CBM)", bold_border2)
            row = 12
            for cp in obj.container_operation_ids:
                container_no = cp.container_no if cp.container_no else ''
                seal_no = cp.seal_no if cp.seal_no else ''
                from_packing_city = cp.packing_id.from_packing_city if cp.packing_id.from_packing_city else ''
                from_packing_country_id = cp.packing_id.from_packing_country_id.name if cp.packing_id.from_packing_country_id.name else ''
                fob_term_id = cp.packing_id.fob_term_id.name if cp.packing_id.fob_term_id.name else ''
                from_city_country = f"{fob_term_id}, {from_packing_city}, {from_packing_country_id}"

                for i in range(0, 11):  # Loop through columns 0 to 7 (inclusive)
                    sheet.write(row-1, i, '')
                    sheet.write(row + 3, i, '')
                    sheet.write(row + 4, i, '')
                
                sheet.write(row, 3, from_city_country)
                sheet.write(row+1, 3, f"CONTAINER NO.# {container_no}")
                sheet.write(row + 2, 3, f"SEAL NO.# {seal_no}")
                
                subtotal_qty_pcs = 0.0
                subtotal_qty_set = 0.0
                subtotal_pack = 0.0
                net_weight = 0.0
                total_weight_gross = 0.0
                subtotal_means = 0.0
                
                container_index += 1  
                row += 4
                # row += 3

                for line in cp.container_operation_line_ids:
                    picking_names = ', '.join([picking.name for picking in cp.picking_ids])
                    
                    buyer_po = line.buyer_po if line.buyer_po else ''
                    sku = line.sku if line.sku else ''
                    product_container_qty = int(line.product_container_qty) if line.product_container_qty else ''

                    for i in range(0, 11):  # Loop through columns 0 to 7 (inclusive)
                        sheet.write(row-1, i, '')
                    
                    sheet.write(row, 3, f"PO. NO:{buyer_po}")
                    sheet.write(row+1, 3, f"SJ. NO:{picking_names}")
                    sheet.write(row+2, 1, line.product_id.name)
                    sheet.write(row+2, 2, sku)
                    sheet.write(row+2, 4, product_container_qty,text_left)
                    sheet.write(row+2, 5, line.product_uom.name)
                    sheet.write(row+2, 6, "{:,.2f}".format(line.pack))
                    sheet.write(row+2, 7,'')
                    sheet.write(row+2, 8, "{:,.2f}".format(line.net_weight))
                    sheet.write(row+2, 9, "{:,.2f}".format(line.gross_weight))
                    sheet.write(row+2, 10, "{:,.2f}".format(line.means))
                    
                                        # sheet.write(row, 4, "{:,.2f}".format(unit_price),)

                    
                    for i in range(1, 11):  # Loop through columns 0 to 7 (inclusive)
                        sheet.write(row+3, i, '')
                        sheet.write(row+4, i, '')
                        sheet.write(row+5, i, '')
                    
                    if line.product_uom.name == 'pcs':
                        subtotal_qty_pcs += int(product_container_qty)
                    elif line.product_uom.name == 'set':
                        subtotal_qty_set += int(product_container_qty)

                    subtotal_pack += line.pack
                    net_weight += line.net_weight
                    total_weight_gross += line.gross_weight
                    subtotal_means += line.means
                    
                    border_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
                    sheet.conditional_format(row, 0, row + 2, 7, {'type': 'no_errors', 'format': border_format})
                    row += 6
                
                sheet.write(row-2, 1, f"TOTAL CONTAINER {container_index}",bold_border)  # # Hitung nomor kontainer secara manual
                sheet.write(row-2, 2, '',bold_border) 
                sheet.write(row-2, 3, '',bold_border)   
                sheet.write(row-2, 4, f"{int(subtotal_qty_pcs)} \n{int(subtotal_qty_set)}",bold_border)  
                sheet.write(row-2, 5, f"PCS \n SET",bold_border)
                sheet.write(row-2, 6, "{:,.2f}".format(subtotal_pack),bold_border)
                sheet.write(row-2, 7, f"CTN",bold_border)
                sheet.write(row-2, 8, "{:,.2f}".format(net_weight),bold_border)
                sheet.write(row-2, 9, "{:,.2f}".format(total_weight_gross),bold_border)
                sheet.write(row-2, 10, "{:,.2f}".format(subtotal_means),bold_border)
                # for i in range(0, 8):  # Loop through columns 0 to 7 (inclusive)
                #         sheet.write(row-1, i, '')
                #         sheet.write(row, i, '')
                        
            # for i in range(0, 8):  # Loop through columns 0 to 7 (inclusive)
            #             sheet.write(row-3, i, '')
            #             # sheet.write(row, i, '')
            sheet.write(row, 1, f"****GRAND TOTAL****",bold_border)  
            sheet.write(row, 2, '',bold_border)  
            sheet.write(row, 3, '',bold_border)  
            sheet.write(row, 4, f"{total_qty_pcs} \n{total_qty_set}",bold_border)  
            sheet.write(row, 5, f"PCS \n SET",bold_border)
            sheet.write(row, 6, "{:,.2f}".format(total_pack),bold_border)
            sheet.write(row, 7, f"CTN",bold_border)
            sheet.write(row, 8, "{:,.2f}".format(total_net_wght),bold_border)
            sheet.write(row, 9, "{:,.2f}".format(total_gross_wght),bold_border)
            sheet.write(row, 10, "{:,.2f}".format(total_means),bold_border)
            
            # row += 3
            # sheet.merge_range(row,1,row,4,obj.env.company.name,text_center)
            # row += 5
            # sheet.write(row,1,f"MADE IN INDONESIA")
            # row += 1
            # sheet.write(row,1,f"PO #")
            # row += 1
            # sheet.write(row+3,1,f"DESCRIPT")
            # row += 1
            # sheet.write(row+2,2,f":")
            # row += 1
            # sheet.write(row+2,1,f"SKU #")
            # row += 1
            # sheet.write(row,2,f":")
            # row += 1
            # sheet.write(row,1,f"PCS / SP")
            # row += 1
            # sheet.write(row,2,f":")
            # row += 1
            # sheet.write(row,1,f"TTL / SP'S")
            # row += 1
            # sheet.write(row,2,f":")
            # row += 1
            # sheet.write(row,1,f"TTL / PCS")
            # row += 1
            # sheet.write(row,2,f":")
            # row += 1
            # sheet.write(row,1,f"N.W.")
            # row += 1
            # sheet.write(row,2,f":")
            # row += 1
            # sheet.write(row,1,f"G.W.")
            # row += 1
            # sheet.write(row,2,f":")
            # row += 1
            # sheet.write(row,1,f"CBM")
            # row += 1
            # sheet.write(row,2,f":")
            # row += 1
            # sheet.write(row,1,f"CTN NO.")
            # row += 1
            # sheet.write(row,2,f":")
        return workbook