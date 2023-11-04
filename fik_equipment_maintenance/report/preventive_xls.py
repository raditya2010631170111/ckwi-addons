
from odoo import models, fields, _
import datetime

class ReportPreventiveXLSX(models.AbstractModel):
    _name = 'report.fik_equipment_maintenance.report_preventive_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Report Preventive Maintenance Excel'


    def generate_xlsx_report(self, workbook, data, objects):
        for obj in objects:
            # for obj in objects:

            sheet = workbook.add_worksheet('Preventive Maintenance')
            sheet.set_margins(0.5, 0.5, 0.5, 0.5)
            currency_header_format = workbook.add_format({'bold': True, 'num_format': '[$Rp-421]#,##0.00', 'font_size': 10})
            currency_header_format.set_bottom(1)
            currency_header_format.set_top(1)
            table_header = workbook.add_format ({'border' :1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'font_size': 11})
            table_body = workbook.add_format({'border': 1, 'text_wrap': True, 'font_size': 10})
            table_body_center = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'font_size': 10})
            header_title_center = workbook.add_format({'bold': True, 'font_size': 30, 'align': 'center', 'valign': 'vcenter'})
            header_title_left = workbook.add_format({'bold': True, 'font_size': 30})
            title_style = workbook.add_format({'font_name': 'Times', 'font_size': 12})
            header_style = workbook.add_format({'font_name': 'Times', 'font_size': 12, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
            header_ttd = workbook.add_format({'font_name': 'Times', 'font_size': 12, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
            year_format = workbook.add_format({'num_format': 'yyyy', 'font_size': 12, 'align': 'left' ,})
            
            sheet.set_column('A:A', 3)
            sheet.set_column('B:B', 20)
            sheet.set_column('C:C', 15)
            sheet.set_column('B:E', 15)
            sheet.set_column('D:AZ', 3)
            sheet.set_row(0, 30)
            
            sheet.merge_range('A1:C2', 'CKWI', header_title_left)
            sheet.merge_range('E1:AN2', 'TOTAL PREVENTIF MAINTENACE', header_title_center)
            sheet.write('A3', obj.company_id.name, title_style)
            sheet.merge_range('A5:B5', 'BAGIAN', title_style)
            sheet.merge_range('A6:B6', 'TAHUN', title_style)
            sheet.merge_range('AO1:AR1', 'DISETUJUI', header_style)
            sheet.merge_range('AO2:AR5', '', header_style)
            sheet.merge_range('AS1:AV1', 'DIPERIKSA', header_style)
            sheet.merge_range('AS2:AV5', '', header_style)
            sheet.merge_range('AW1:AZ1', 'DIPERIKSA', header_style)
            sheet.merge_range('AW2:AZ5', '', header_style)
            
            sheet.merge_range('A7:A8', 'NO', table_header)
            sheet.merge_range('B7:B8', 'NAMA MESIN', table_header)
            sheet.merge_range('C7:C8', 'NO MESIN', table_header)
            sheet.write('D7', 'P', table_header)
            sheet.write('D8', 'A', table_header)
            sheet.merge_range('E7:H7', 'JANUARI', table_header)
            sheet.merge_range('I7:L7', 'FEBRUARI', table_header)
            sheet.merge_range('M7:P7', 'MARET', table_header)
            sheet.merge_range('Q7:T7', 'APRIL', table_header)
            sheet.merge_range('U7:X7', 'MEI', table_header)
            sheet.merge_range('Y7:AB7', 'JUNI', table_header)
            sheet.merge_range('AC7:AF7', 'JULI', table_header)
            sheet.merge_range('AG7:AJ7', 'AGUSTUS', table_header)
            sheet.merge_range('AK7:AN7', 'SEPTEMBER', table_header)
            sheet.merge_range('AO7:AR7', 'OKTOBER', table_header)
            sheet.merge_range('AS7:AV7', 'NOPEMBER', table_header)
            sheet.merge_range('AW7:AZ7', 'DESEMBER', table_header)
            sheet.write('E8', '1', table_header)
            sheet.write('F8', '2', table_header)
            sheet.write('G8', '3', table_header)
            sheet.write('H8', '4', table_header)
            sheet.write('I8', '1', table_header)
            sheet.write('J8', '2', table_header)
            sheet.write('K8', '3', table_header)
            sheet.write('L8', '4', table_header)
            sheet.write('M8', '1', table_header)
            sheet.write('N8', '2', table_header)
            sheet.write('O8', '3', table_header)
            sheet.write('P8', '4', table_header)
            sheet.write('Q8', '1', table_header)
            sheet.write('R8', '2', table_header)
            sheet.write('S8', '3', table_header)
            sheet.write('T8', '4', table_header)
            sheet.write('U8', '1', table_header)
            sheet.write('V8', '2', table_header)
            sheet.write('W8', '3', table_header)
            sheet.write('X8', '4', table_header)
            sheet.write('Y8', '1', table_header)
            sheet.write('Z8', '2', table_header)
            sheet.write('AA8', '3', table_header)
            sheet.write('AB8', '4', table_header)
            sheet.write('AC8', '1', table_header)
            sheet.write('AD8', '2', table_header)
            sheet.write('AE8', '3', table_header)
            sheet.write('AF8', '4', table_header)
            sheet.write('AG8', '1', table_header)
            sheet.write('AH8', '2', table_header)
            sheet.write('AI8', '3', table_header)
            sheet.write('AJ8', '4', table_header)
            sheet.write('AK8', '1', table_header)
            sheet.write('AL8', '2', table_header)
            sheet.write('AM8', '3', table_header)
            sheet.write('AN8', '4', table_header)
            sheet.write('AO8', '1', table_header)
            sheet.write('AP8', '2', table_header)
            sheet.write('AQ8', '3', table_header)
            sheet.write('AR8', '4', table_header)
            sheet.write('AS8', '1', table_header)
            sheet.write('AT8', '2', table_header)
            sheet.write('AU8', '3', table_header)
            sheet.write('AV8', '4', table_header)
            sheet.write('AW8', '1', table_header)
            sheet.write('AX8', '2', table_header)
            sheet.write('AY8', '3', table_header)
            sheet.write('AZ8', '4', table_header)
            
            sheet.write('C5', obj.category_id.name, title_style)
            sheet.write('C6', obj.date_from, year_format)

            # python data
            row = 8
            number = 1
            for prev in data['preventive']:
                #check month date
                current_month_plan = datetime.datetime.strptime(str(prev['schedule_date']),'%Y-%m-%d %H:%M:%S').month
                current_date_plan = datetime.datetime.strptime(str(prev['schedule_date']),'%Y-%m-%d %H:%M:%S').day
                # current_month_actual = datetime.datetime.strptime(str(prev['date_actual']), '%Y-%m-%d').month
                # current_date_actual = datetime.datetime.strptime(str(prev['date_actual']), '%Y-%m-%d').day
                if (prev['date_actual'] == False):
                    current_month_actual = 100
                    current_date_actual = 25
                else:
                    current_month_actual = datetime.datetime.strptime(str(prev['date_actual']), '%Y-%m-%d').month
                    current_date_actual = datetime.datetime.strptime(str(prev['date_actual']), '%Y-%m-%d').day
                # if prev['state'] in 'in_progress':
                #     current_month_actual = datetime.datetime.strptime(str(prev['date_actual']), '%Y-%m-%d').month
                #     current_date_actual = datetime.datetime.strptime(str(prev['date_actual']),'%Y-%m-%d').day
                # else:
                #     current_month_actual = 100
                #     current_date_actual = 1

                # actual plan january
                jan_week1_plan = ''
                jan_week1_actual = ''
                jan_week2_plan = ''
                jan_week2_actual = ''
                jan_week3_plan = ''
                jan_week3_actual = ''
                jan_week4_plan = ''
                jan_week4_actual = ''
                # actual plan february
                feb_week1_plan = ''
                feb_week1_actual = ''
                feb_week2_plan = ''
                feb_week2_actual = ''
                feb_week3_plan = ''
                feb_week3_actual = ''
                feb_week4_plan = ''
                feb_week4_actual = ''
                # actual plan maret
                mar_week1_plan = ''
                mar_week1_actual = ''
                mar_week2_plan = ''
                mar_week2_actual = ''
                mar_week3_plan = ''
                mar_week3_actual = ''
                mar_week4_plan = ''
                mar_week4_actual = ''
                # actual plan april
                apr_week1_plan = ''
                apr_week1_actual = ''
                apr_week2_plan = ''
                apr_week2_actual = ''
                apr_week3_plan = ''
                apr_week3_actual = ''
                apr_week4_plan = ''
                apr_week4_actual = ''
                # actual plan mei
                mei_week1_plan = ''
                mei_week1_actual = ''
                mei_week2_plan = ''
                mei_week2_actual = ''
                mei_week3_plan = ''
                mei_week3_actual = ''
                mei_week4_plan = ''
                mei_week4_actual = ''
                # actual plan juni
                jun_week1_plan = ''
                jun_week1_actual = ''
                jun_week2_plan = ''
                jun_week2_actual = ''
                jun_week3_plan = ''
                jun_week3_actual = ''
                jun_week4_plan = ''
                jun_week4_actual = ''
                # actual plan juli
                jul_week1_plan = ''
                jul_week1_actual = ''
                jul_week2_plan = ''
                jul_week2_actual = ''
                jul_week3_plan = ''
                jul_week3_actual = ''
                jul_week4_plan = ''
                jul_week4_actual = ''
                # actual plan agustus
                ags_week1_plan = ''
                ags_week1_actual = ''
                ags_week2_plan = ''
                ags_week2_actual = ''
                ags_week3_plan = ''
                ags_week3_actual = ''
                ags_week4_plan = ''
                ags_week4_actual = ''
                # actual plan september
                sep_week1_plan = ''
                sep_week1_actual = ''
                sep_week2_plan = ''
                sep_week2_actual = ''
                sep_week3_plan = ''
                sep_week3_actual = ''
                sep_week4_plan = ''
                sep_week4_actual = ''
                # actual plan oktober
                okt_week1_plan = ''
                okt_week1_actual = ''
                okt_week2_plan = ''
                okt_week2_actual = ''
                okt_week3_plan = ''
                okt_week3_actual = ''
                okt_week4_plan = ''
                okt_week4_actual = ''
                # actual plan november
                nov_week1_plan = ''
                nov_week1_actual = ''
                nov_week2_plan = ''
                nov_week2_actual = ''
                nov_week3_plan = ''
                nov_week3_actual = ''
                nov_week4_plan = ''
                nov_week4_actual = ''
                # actual plan desember
                des_week1_plan = ''
                des_week1_actual = ''
                des_week2_plan = ''
                des_week2_actual = ''
                des_week3_plan = ''
                des_week3_actual = ''
                des_week4_plan = ''
                des_week4_actual = ''
                #
                if current_month_plan == 1:
                    if 1 <= current_date_plan <= 7:
                        jan_week1_plan = 'P'
                    elif 8 <= current_date_plan <= 14:
                        jan_week2_plan = 'P'
                    elif 15 <= current_date_plan <= 21:
                        jan_week3_plan = 'P'
                    else:
                        jan_week4_plan = 'P'
                elif current_month_plan == 2:
                    if 1 <= current_date_plan <= 7:
                        feb_week1_plan = 'P'
                    elif 8 <= current_date_plan <= 14:
                        feb_week2_plan = 'P'
                    elif 15 <= current_date_plan <= 21:
                        feb_week3_plan = 'P'
                    else:
                        feb_week4_plan = 'P'
                elif current_month_plan == 3:
                    if 1 <= current_date_plan <= 7:
                        mar_week1_plan = 'P'
                    elif 8 <= current_date_plan <= 14:
                        mar_week2_plan = 'P'
                    elif 15 <= current_date_plan <= 21:
                        mar_week3_plan = 'P'
                    else:
                        mar_week4_plan = 'P'
                elif current_month_plan == 4:
                    if 1 <= current_date_plan <= 7:
                        apr_week1_plan = 'P'
                    elif 8 <= current_date_plan <= 14:
                        apr_week2_plan = 'P'
                    elif 15 <= current_date_plan <= 21:
                        apr_week3_plan = 'P'
                    else:
                        apr_week4_plan = 'P'                
                elif current_month_plan == 5:
                    if 1 <= current_date_plan <= 7:
                        mei_week1_plan = 'P'
                    elif 8 <= current_date_plan <= 14:
                        mei_week2_plan = 'P'
                    elif 15 <= current_date_plan <= 21:
                        mei_week3_plan = 'P'
                    else:
                        mei_week4_plan = 'P'
                elif current_month_plan == 6:
                    if 1 <= current_date_plan <= 7:
                        jun_week1_plan = 'P'
                    elif 8 <= current_date_plan <= 14:
                        jun_week2_plan = 'P'
                    elif 15 <= current_date_plan <= 21:
                        jun_week3_plan = 'P'
                    else:
                        jun_week4_plan = 'P'
                elif current_month_plan == 7:
                    if 1 <= current_date_plan <= 7:
                        jul_week1_plan = 'P'
                    elif 8 <= current_date_plan <= 14:
                        jul_week2_plan = 'P'
                    elif 15 <= current_date_plan <= 21:
                        jul_week3_plan = 'P'
                    else:
                        jul_week4_plan = 'P'        
                elif current_month_plan == 8:
                    if 1 <= current_date_plan <= 7:
                        ags_week1_plan = 'P'
                    elif 8 <= current_date_plan <= 14:
                        ags_week2_plan = 'P'
                    elif 15 <= current_date_plan <= 21:
                        ags_week3_plan = 'P'
                    else:
                        ags_week4_plan = 'P'
                elif current_month_plan == 9:
                    if 1 <= current_date_plan <= 7:
                        sep_week1_plan = 'P'
                    elif 8 <= current_date_plan <= 14:
                        sep_week2_plan = 'P'
                    elif 15 <= current_date_plan <= 21:
                        sep_week3_plan = 'P'
                    else:
                        sep_week4_plan = 'P'
                elif current_month_plan == 10:
                    if 1 <= current_date_plan <= 7:
                        okt_week1_plan = 'P'
                    elif 8 <= current_date_plan <= 14:
                        okt_week2_plan = 'P'
                    elif 15 <= current_date_plan <= 21:
                        okt_week3_plan = 'P'
                    else:
                        okt_week4_plan = 'P'
                elif current_month_plan == 11:
                    if 1 <= current_date_plan <= 7:
                        nov_week1_plan = 'P'
                    elif 8 <= current_date_plan <= 14:
                        nov_week2_plan = 'P'
                    elif 15 <= current_date_plan <= 21:
                        nov_week3_plan = 'P'
                    else:
                        nov_week4_plan = 'P'
                else:
                    if 1 <= current_date_plan <= 7:
                        des_week1_plan = 'P'
                    elif 8 <= current_date_plan <= 14:
                        des_week2_plan = 'P'
                    elif 15 <= current_date_plan <= 21:
                        des_week3_plan = 'P'
                    else:
                        des_week4_plan = 'P'                         
                #
                if current_month_actual == 100:
                    if 1 <= current_date_actual <= 7:
                        jan_week1_actual = '-'
                    elif 8 <= current_date_actual <= 14:
                        jan_week2_actual = '-'
                    elif 15 <= current_date_actual <= 21:
                        jan_week3_actual = '-'
                    else:
                        jan_week4_actual = '-'
                if current_month_actual == 1:
                    if 1 <= current_date_actual <= 7:
                        jan_week1_actual = 'A'
                    elif 8 <= current_date_actual <= 14:
                        jan_week2_actual = 'A'
                    elif 15 <= current_date_actual <= 21:
                        jan_week3_actual = 'A'
                    else:
                        jan_week4_actual = 'A'
                elif current_month_actual == 2:
                    if 1 <= current_date_actual <= 7:
                        feb_week1_actual = 'A'
                    elif 8 <= current_date_actual <= 14:
                        feb_week2_actual = 'A'
                    elif 15 <= current_date_actual <= 21:
                        feb_week3_actual = 'A'
                    else:
                        feb_week4_actual = 'A'
                elif current_month_actual == 3:
                    if 1 <= current_date_actual <= 7:
                        mar_week1_actual = 'A'
                    elif 8 <= current_date_actual <= 14:
                        mar_week2_actual = 'A'
                    elif 15 <= current_date_actual <= 21:
                        mar_week3_actual = 'A'
                    else:
                        mar_week4_actual = 'A'
                elif current_month_actual == 4:
                    if 1 <= current_date_actual <= 7:
                        apr_week1_actual = 'A'
                    elif 8 <= current_date_actual <= 14:
                        apr_week2_actual = 'A'
                    elif 15 <= current_date_actual <= 21:
                        apr_week3_actual = 'A'
                    else:
                        apr_week4_actual = 'A'
                elif current_month_actual == 5:
                    if 1 <= current_date_actual <= 7:
                        mei_week1_actual = 'A'
                    elif 8 <= current_date_actual <= 14:
                        mei_week2_actual = 'A'
                    elif 15 <= current_date_actual <= 21:
                        mei_week3_actual = 'A'
                    else:
                        mei_week4_actual = 'A'
                elif current_month_actual == 6:
                    if 1 <= current_date_actual <= 7:
                        jun_week1_actual = 'A'
                    elif 8 <= current_date_actual <= 14:
                        jun_week2_actual = 'A'
                    elif 15 <= current_date_actual <= 21:
                        jun_week3_actual = 'A'
                    else:
                        jun_week4_actual = 'A'
                elif current_month_actual == 7:
                    if 1 <= current_date_actual <= 7:
                        jul_week1_actual = 'A'
                    elif 8 <= current_date_actual <= 14:
                        jul_week2_actual = 'A'
                    elif 15 <= current_date_actual <= 21:
                        jul_week3_actual = 'A'
                    else:
                        jul_week4_actual = 'A'
                elif current_month_actual == 8:
                    if 1 <= current_date_actual <= 7:
                        ags_week1_actual = 'A'
                    elif 8 <= current_date_actual <= 14:
                        ags_week2_actual = 'A'
                    elif 15 <= current_date_actual <= 21:
                        ags_week3_actual = 'A'
                    else:
                        ags_week4_actual = 'A'
                elif current_month_actual == 9:
                    if 1 <= current_date_actual <= 7:
                        sep_week1_actual = 'A'
                    elif 8 <= current_date_actual <= 14:
                        sep_week2_actual = 'A'
                    elif 15 <= current_date_actual <= 21:
                        sep_week3_actual = 'A'
                    else:
                        sep_week4_actual = 'A'
                elif current_month_actual == 10:
                    if 1 <= current_date_actual <= 7:
                        okt_week1_actual = 'A'
                    elif 8 <= current_date_actual <= 14:
                        okt_week2_actual = 'A'
                    elif 15 <= current_date_actual <= 21:
                        okt_week3_actual = 'A'
                    else:
                        okt_week4_actual = 'A'
                elif current_month_actual == 11:
                    if 1 <= current_date_actual <= 7:
                        nov_week1_actual = 'A'
                    elif 8 <= current_date_actual <= 14:
                        nov_week2_actual = 'A'
                    elif 15 <= current_date_actual <= 21:
                        nov_week3_actual = 'A'
                    else:
                        nov_week4_actual = 'A'
                else:
                    if 1 <= current_date_actual <= 7:
                        des_week1_actual = 'A'
                    elif 8 <= current_date_actual <= 14:
                        des_week2_actual = 'A'
                    elif 15 <= current_date_actual <= 21:
                        des_week3_actual = 'A'
                    else:
                        des_week4_actual = 'A'                                        
                #         
                sheet.merge_range(row, 0, row + 1, 0, number, table_body_center)
                sheet.merge_range(row, 1, row + 1, 1, prev['nama_mesin'], table_body_center)
                sheet.merge_range(row, 2, row + 1, 2, prev['no_mesin'], table_body_center)
                sheet.write(row, 3, 'P', table_body_center)
                row+=1
                sheet.write(row, 3, 'A', table_body_center)
                #
                sheet.write(row - 1, 4, jan_week1_plan, table_body_center)
                sheet.write(row, 4, jan_week1_actual, table_body_center)
                sheet.write(row - 1, 5, jan_week2_plan, table_body_center)
                sheet.write(row, 5, jan_week2_actual, table_body_center)
                sheet.write(row - 1, 6, jan_week3_plan, table_body_center)
                sheet.write(row, 6, jan_week3_actual, table_body_center)
                sheet.write(row - 1, 7, jan_week4_plan, table_body_center)
                sheet.write(row, 7, jan_week4_actual, table_body_center)
                #
                sheet.write(row - 1, 8, feb_week1_plan, table_body_center)
                sheet.write(row, 8, feb_week1_actual, table_body_center)
                sheet.write(row - 1, 9, feb_week2_plan, table_body_center)
                sheet.write(row, 9, feb_week2_actual, table_body_center)
                sheet.write(row - 1, 10, jan_week3_plan, table_body_center)
                sheet.write(row, 10, feb_week3_actual, table_body_center)
                sheet.write(row - 1, 11, feb_week4_plan, table_body_center)
                sheet.write(row, 11, feb_week4_actual, table_body_center)
                #
                sheet.write(row - 1, 12, mar_week1_plan, table_body_center)
                sheet.write(row, 12, mar_week1_actual, table_body_center)
                sheet.write(row - 1, 13, mar_week2_plan, table_body_center)
                sheet.write(row, 13, mar_week2_actual, table_body_center)
                sheet.write(row - 1, 14, mar_week3_plan, table_body_center)
                sheet.write(row, 14, mar_week3_actual, table_body_center)
                sheet.write(row - 1, 15, mar_week4_plan, table_body_center)
                sheet.write(row, 15, mar_week4_actual, table_body_center)
                #
                sheet.write(row - 1, 16, apr_week1_plan, table_body_center)
                sheet.write(row, 16, apr_week1_actual, table_body_center)
                sheet.write(row - 1, 16, apr_week2_plan, table_body_center)
                sheet.write(row, 17, apr_week2_actual, table_body_center)
                sheet.write(row - 1, 18, apr_week3_plan, table_body_center)
                sheet.write(row, 18, apr_week3_actual, table_body_center)
                sheet.write(row - 1, 19, apr_week4_plan, table_body_center)
                sheet.write(row, 19, apr_week4_actual, table_body_center)
                #
                sheet.write(row - 1, 20, mei_week1_plan, table_body_center)
                sheet.write(row, 20, mei_week1_actual, table_body_center)
                sheet.write(row - 1, 21, mei_week2_plan, table_body_center)
                sheet.write(row, 21, mei_week2_actual, table_body_center)
                sheet.write(row - 1, 22, mei_week3_plan, table_body_center)
                sheet.write(row, 22, mei_week3_actual, table_body_center)
                sheet.write(row - 1, 23, mei_week4_plan, table_body_center)
                sheet.write(row, 23, mei_week4_actual, table_body_center)
                #
                sheet.write(row - 1, 24, jun_week1_plan, table_body_center)
                sheet.write(row, 24, jun_week1_actual, table_body_center)
                sheet.write(row - 1, 25, jun_week2_plan, table_body_center)
                sheet.write(row, 25, jun_week2_actual, table_body_center)
                sheet.write(row - 1, 26, jun_week3_plan, table_body_center)
                sheet.write(row, 26, jun_week3_actual, table_body_center)
                sheet.write(row - 1, 27, jun_week4_plan, table_body_center)
                sheet.write(row, 27, jun_week4_actual, table_body_center)
                #
                sheet.write(row - 1, 28, jul_week1_plan, table_body_center)
                sheet.write(row, 28, jul_week1_actual, table_body_center)
                sheet.write(row - 1, 29, jul_week2_plan, table_body_center)
                sheet.write(row, 29, jul_week2_actual, table_body_center)
                sheet.write(row - 1, 30, jul_week3_plan, table_body_center)
                sheet.write(row, 30, jul_week3_actual, table_body_center)
                sheet.write(row - 1, 31, jul_week4_plan, table_body_center)
                sheet.write(row, 31, jul_week4_actual, table_body_center)
                #
                sheet.write(row - 1, 32, ags_week1_plan, table_body_center)
                sheet.write(row, 32, ags_week1_actual, table_body_center)
                sheet.write(row - 1, 33, ags_week2_plan, table_body_center)
                sheet.write(row, 33, ags_week2_actual, table_body_center)
                sheet.write(row - 1, 34, ags_week3_plan, table_body_center)
                sheet.write(row, 34, ags_week3_actual, table_body_center)
                sheet.write(row - 1, 35, ags_week4_plan, table_body_center)
                sheet.write(row, 35, ags_week4_actual, table_body_center)
                #
                sheet.write(row - 1, 36, sep_week1_plan, table_body_center)
                sheet.write(row, 36, sep_week1_actual, table_body_center)
                sheet.write(row - 1, 37, sep_week2_plan, table_body_center)
                sheet.write(row, 37, sep_week2_actual, table_body_center)
                sheet.write(row - 1, 38, sep_week3_plan, table_body_center)
                sheet.write(row, 38, sep_week3_actual, table_body_center)
                sheet.write(row - 1, 39, sep_week4_plan, table_body_center)
                sheet.write(row, 39, sep_week4_actual, table_body_center)
                #
                sheet.write(row - 1, 40, okt_week1_plan, table_body_center)
                sheet.write(row, 40, okt_week1_actual, table_body_center)
                sheet.write(row - 1, 41, okt_week2_plan, table_body_center)
                sheet.write(row, 41, okt_week2_actual, table_body_center)
                sheet.write(row - 1, 42, okt_week3_plan, table_body_center)
                sheet.write(row, 42, okt_week3_actual, table_body_center)
                sheet.write(row - 1, 43, okt_week4_plan, table_body_center)
                sheet.write(row, 43, okt_week4_actual, table_body_center)
                #
                sheet.write(row - 1, 44, nov_week1_plan, table_body_center)
                sheet.write(row, 44, nov_week1_actual, table_body_center)
                sheet.write(row - 1, 45, nov_week2_plan, table_body_center)
                sheet.write(row, 45, nov_week2_actual, table_body_center)
                sheet.write(row - 1, 46, nov_week3_plan, table_body_center)
                sheet.write(row, 46, nov_week3_actual, table_body_center)
                sheet.write(row - 1, 47, nov_week4_plan, table_body_center)
                sheet.write(row, 47, nov_week4_actual, table_body_center)
                #
                sheet.write(row - 1, 48, des_week1_plan, table_body_center)
                sheet.write(row, 48, des_week1_actual, table_body_center)
                sheet.write(row - 1, 49, des_week2_plan, table_body_center)
                sheet.write(row, 49, des_week2_actual, table_body_center)
                sheet.write(row - 1, 50, des_week3_plan, table_body_center)
                sheet.write(row, 50, des_week3_actual, table_body_center)
                sheet.write(row - 1, 51, des_week4_plan, table_body_center)
                sheet.write(row, 51, des_week4_actual, table_body_center)
                #
                row += 1
                number+=1
            