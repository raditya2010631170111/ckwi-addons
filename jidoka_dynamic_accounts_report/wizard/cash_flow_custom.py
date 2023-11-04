# -*- coding: utf-8 -*-
import time
from odoo import fields, models, api, _
import calendar
import io
import json
from odoo.exceptions import  UserError
from datetime import datetime

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
import logging

_logger = logging.getLogger(__name__)


class CashFlowCustomWizard(models.TransientModel):
    _inherit = "account.common.report"
    _name = 'cash.flow.custom'

    def _default_periode(self):
        return time.strftime("%Y-%m")
    periode = fields.Char(string='Periode', default=_default_periode)

    @api.model
    def view_report(self, option, tag):
        wizard = self.env['cash.flow.custom'].search(
            [('id', '=', option[0])])
        filters = wizard.read([
            'periode'
        ])[0]

        fmt = '%d %b %Y'

        periode = ''
        date_of_periode = False
        date_before_periode = False 
        # TODO ini masih valid?
        # periode sebelum 2022-01 dianggap tidak valid -> 0
        valid_period = False
        try:
            wiz_periode = datetime.now().strftime('%Y-%m')
            if wizard and wizard.periode:
                wiz_periode = wizard.periode
            date_of_periode = datetime.strptime(wiz_periode, '%Y-%m').date()
            if date_of_periode.year >= 2022:
                valid_period = True
            if date_of_periode:
                date_first_of_periode= date_of_periode.replace(month=1, day=1)
                date_end_before_periode=  date_of_periode.replace(month=12, day=31, year= date_of_periode.year-1)
                date_first_before_periode=  date_of_periode.replace(month=1, day=1, year= date_of_periode.year-1)
            periode = date_of_periode.strftime('%B %Y')
        except:
            raise UserError(
                _("Format periode tidak sesuai dengan 'yyyy-mm'. contoh: 2022-10 (untuk bulan oktober 2022)"))

        search_list = []
        configs = self.env['cash.flow.config'].sudo().search(search_list)

        # Convert to string
        str_date_of_periode = date_of_periode.strftime('%Y-%m-%d')
        str_date_end_of_period = date_of_periode.replace(day = calendar.monthrange(
                            date_of_periode.year, date_of_periode.month)[1]).strftime('%Y-%m-%d')
        str_date_first_of_periode = date_first_of_periode.strftime('%Y-%m-%d')
        str_date_end_before_periode = date_end_before_periode.strftime('%Y-%m-%d')

        report_lines = []
        no = 1

        if not valid_period:
            amount = 0
        else:
            # Cari untuk Loss Before Income Tax Expenses (jan tahun ini sd akhir bulan ini)
            query_pnl = """ select sum(al.balance) as amount 
                        from account_move_line al
                        left join account_move am on am.id = al.move_id
                        left join account_account aa on aa.id = al.account_id
                        left join account_account_type aat on aa.user_type_id =  aat.id
                        where
                            am.state = 'posted'
                            and am.date <= '{}' 
                            and am.date >= '{}' 
                            and aat.internal_group in ('income', 'expense') 
                    """.format(
                        str_date_end_of_period,
                        str_date_first_of_periode
                    )
            self.env.cr.execute(query_pnl)
            amount = self.env.cr.fetchone()[0]
            # negative
            amount = -1 * float(amount)
        
        # DEMO / TEMPLATE DATA
        report_lines.append({
            'name': 'CASH FLOWS FROM OPERATING ACTIVITIES',
            'level': 1,
            'amount': '',
        })

        report_lines.append({
            'name': 'Loss Before Income Tax Expenses',
            'level': 2,
            'amount': amount,
        })

        report_lines.append({
            'name': 'Adjustment for:',
            'level': 2,
            'amount': '',
        })

        if not valid_period:
            net_cash_at_begining_year = 0
        else:
            # Cari Cash begining year
            query_liquid = """ select sum(al.balance) as amount
                        from account_move_line al
                        left join account_move am on am.id = al.move_id
                        left join account_account aa on aa.id = al.account_id
                        where 
                            aa.user_type_id = 3  
                            and am.state = 'posted'
                            and am.date <= '{}'
                    """.format(str_date_end_before_periode)
            self.env.cr.execute(query_liquid)
            net_cash_at_begining_year = self.env.cr.fetchone()[0]
         
        amount_tot = amount
        net_operating_activities = amount
        net_investing_activities = 0
        net_financing_activities = 0
        report_type_operating = [
            'Depreciation Of Fixed Assets',
            'Correction Retained Earnings',
            'Account Receivable',
            'Other Receivable',
            'Inventory',
            'Prepaid Tax',
            'Advance and Prepayment',
            'Refundable Deposit - Non Current',
            'Other Assets',
            'Account Payable',
            'Taxes Payable',
            'Accrued Payable',
            'Other Payable',
        ]
        for conf in configs:
            amount = 0
            if valid_period:
                # Cari untuk Loss Before Income Tax Expenses
                groups = ''
                if conf.account_ids:
                    groups = ' IN %s' % str(tuple(x.id for x in conf.account_ids) + tuple(['0']))

                if conf.account_ids and conf.calculation_type == 'type_1':
                    # BS di periode berjalan (jan tahun ini sd akhir bulan ini)
                    query = """ select sum(al.balance) as amount
                                from account_move_line al
                                left join account_move am on am.id = al.move_id
                                left join account_account aa on aa.id = al.account_id
                                where 
                                    am.state = 'posted'
                                    and al.account_id {} 
                                    and am.date >= '{}' 
                                    and am.date <= '{}' 
                            """.format(groups, str_date_first_of_periode, str_date_end_of_period)
                    self.env.cr.execute(query)
                    amount = self.env.cr.fetchone()[0]

                if conf.account_ids and conf.calculation_type == 'type_2':
                    # BS di akhir tahun sebelum tahun ini (saldo awal tahun ini)
                    query1 = """ select sum(al.balance) as amount 
                                from account_move_line al
                                left join account_move am on am.id = al.move_id
                                left join account_account aa on aa.id = al.account_id
                                where 
                                    am.state = 'posted' 
                                    and al.account_id {} 
                                    and am.date <= '{}' 
                            """.format(groups, str_date_end_before_periode)
                    self.env.cr.execute(query1)
                    amount1 = self.env.cr.fetchone()[0]

                    # BS s/d akhir bulan ini (saldo akhir bulan ini)
                    query2 = """ select sum(al.balance) as amount 
                                from account_move_line al
                                left join account_move am on am.id = al.move_id
                                left join account_account aa on aa.id = al.account_id
                                where 
                                    am.state = 'posted' 
                                    and al.account_id {} 
                                    and am.date <= '{}' 
                            """.format(groups, str_date_end_of_period)
                    self.env.cr.execute(query2)
                    amount2 = self.env.cr.fetchone()[0]

                    amount = float(amount1 or 0.0) - float(amount2 or 0.0)
                
                if conf.account_ids and conf.calculation_type == 'type_3':
                    # BS di akhir tahun sebelum tahun ini (saldo awal tahun ini)
                    query1 = """ select sum(al.balance) as amount 
                                from account_move_line al
                                left join account_move am on am.id = al.move_id
                                left join account_account aa on aa.id = al.account_id
                                where 
                                    am.state = 'posted' 
                                    and al.account_id {} 
                                    and am.date <= '{}' 
                            """.format(groups, str_date_end_before_periode)
                    self.env.cr.execute(query1)
                    amount1 = self.env.cr.fetchone()[0]

                    # BS s/d akhir bulan ini (saldo akhir bulan ini)
                    query2 = """ select sum(al.balance) as amount 
                                from account_move_line al
                                left join account_move am on am.id = al.move_id
                                left join account_account aa on aa.id = al.account_id
                                where 
                                    am.state = 'posted' 
                                    and al.account_id {} 
                                    and am.date <= '{}' 
                            """.format(groups, str_date_end_of_period)
                    self.env.cr.execute(query2)
                    amount2 = self.env.cr.fetchone()[0]

                    amount = float(amount2 or 0.0) - float(amount1 or 0.0)

            # negative sign
            if conf.report_type in [
                # payable
                'Account Payable',
                'Accrued Payable',
                'Taxes Payable',
                'Other Payable',
                'Related Party Loan',
                # equity
                'Intangible Assets',
                'Additional Shared',
                ]:
                amount = -1 * float(amount)
            vals = {
                'name': conf.report_type,
                'level': 3,
                'amount': amount or 0.0,
            }
            report_lines.append(vals)

            # Hitung total
            # CASH FLOWS FROM INVESTING ACTIVITIES 
            if conf.report_type in ['Fixed Assets','Intangible Assets']:
                net_investing_activities = net_investing_activities + float(amount or 0.0)
            # CASH FLOWS FROM FINANCING ACTIVITIES
            if conf.report_type in ['Related Party Loan','Additional Shared']:
                net_financing_activities = net_financing_activities + float(amount or 0.0)
            # CASH FLOWS FROM OPERATING ACTIVITIES

            if conf.report_type in report_type_operating:
                net_operating_activities = net_operating_activities + float(amount or 0.0)
            
            # TOTAL
            amount_tot = amount_tot + float(amount or 0)

            if conf.report_type == 'Correction Retained Earnings':
                report_lines.append({
                    'name': 'Changes In Operating Assets:',
                    'level': 2,
                    'amount': '',
                })
            
            if conf.report_type == 'Other Assets':
                report_lines.append({
                    'name': 'Changes In Operating Liabilities',
                    'level': 2,
                    'amount': '',
                })
            
            if conf.report_type == 'Other Payable':
                report_lines.append({
                    'name': 'Net Cash Use in by Operating Activities',
                    'level': 2,
                    'amount': net_operating_activities,
                    'total': True,
                })
                
                report_lines.append({
                    'name': 'CASH FLOWS FROM INVESTING ACTIVITIES',
                    'level': 1,
                    'amount': '',
                })
            
            if conf.report_type == 'Intangible Assets':
                report_lines.append({
                    'name': 'Net Cash Use In By Investing Activities',
                    'level': 1,
                    'amount': net_investing_activities,
                    'total': True,
                })
                
                report_lines.append({
                    'name': 'CASH FLOWS FROM FINANCING ACTIVITIES',
                    'level': 1,
                    'amount': '',
                })
            
            if conf.report_type == 'Additional Shared':
                report_lines.append({
                    'name': 'Net Cash Use In By Financing Activities',
                    'level': 1,
                    'amount': net_financing_activities,
                    'total': True,
                })
                
                report_lines.append({
                    'name': 'NET INREASE IN CASH ON HAND AND IN BANKS',
                    'level': 1,
                    'amount': amount_tot,
                    'total': True,
                })

                report_lines.append({
                    'name': 'CASH ON HAND AND IN BANKS AT BEGINNING OF YEARS',
                    'level': 1,
                    'amount': net_cash_at_begining_year,
                    'total': True,
                })

                report_lines.append({
                    'name': 'CASH ON HAND AND IN BANKS AT END OF YEARS',
                    'level': 1,
                    'amount': float(amount_tot or 0.0) + float(net_cash_at_begining_year or 0.0),
                    'total': True,
                })
                
        # formatted amount
        company_id = self.env.company
        currency = company_id.currency_id
        symbol = currency.symbol
        for line in report_lines:
            if line.get('amount') and line.get('amount') != '':
                line['f_amount'] = symbol + " " + "{:,.2f}".format(line['amount'])
        vals_total = {}
        datas = {
            'title': tag,
            'filters': filters,
            'total': vals_total,
            'report_lines': report_lines,
        }
        return datas

    @api.model
    def create(self, vals):
        vals['periode'] = self._default_periode()
        res = super(CashFlowCustomWizard, self).create(vals)
        return res

    def get_dynamic_xlsx_report(self, data, response, report_data, dfr_data):
        report_data_main = json.loads(report_data)
        output = io.BytesIO()
        # datas = json.loads(dfr_data)
        filters = json.loads(data)
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        title_style = workbook.add_format(
            {'font_name': 'Times', 'font_size': 13, 'bold': True, 'align': 'center'})
        subtitle_style = workbook.add_format(
            {'font_name': 'Times', 'align': 'center'})
        text_style_bold = workbook.add_format(
            {'font_name': 'Times', 'bold': True, 'align': 'left'})
        # header_style = workbook.add_format(
        #     {'font_name': 'Times', 'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, })
        text_style = workbook.add_format(
            {'font_name': 'Times', 'align': 'left'})
        # number_style = workbook.add_format(
        #     {'font_name': 'Times', 'align': 'center'})
        # percent_style = workbook.add_format(
        #     {'num_format': 10, 'align': 'center'})
        money = workbook.add_format(
            {'num_format': 'Rp#,##0', 'font_name': 'Times', 'align': 'right'})
        money_header_style = workbook.add_format(
            {'num_format': 'Rp#,##0', 'font_name': 'Times', 'bold': True, 'align': 'right'})

        # fmt = '%d %b %Y'

        periode = ''
        date_of_periode = False
        try:
            date_of_periode = datetime.strptime(
                filters['periode'], '%Y-%m').date()
            periode = date_of_periode.strftime('%B %Y')
        except:
            raise UserError(
                _("Format periode tidak sesuai dengan 'yyyy-mm'. contoh: 2022-10 (untuk bulan oktober 2022)"))

        # set lebar kolom
        sheet.set_column('A:A', 4)
        sheet.set_column('B:B', 4)
        sheet.set_column('C:C', 25)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 5)

        # set tinggi
        sheet.set_row(0, 20)
        sheet.set_row(1, 20)
        sheet.set_row(2, 20)
        sheet.set_row(3, 20)

        # Profil PT
        company = self.env.user.company_id

        # judul report
        sheet.merge_range(
            'A1:F1', '')
        sheet.merge_range(
            'A2:F2', company.name, title_style)
        sheet.merge_range(
            'A3:F3', 'CASH FLOW REPORT', title_style)
        sheet.merge_range(
            'A4:F4', 'For The Years Ended {}'.format(periode), title_style)
        sheet.merge_range(
            'A5:F5', '(Expressed in Rupiah, Unless otherwise stated)', subtitle_style)
        row = 6
        col = 0
        no = 1
        for asset in report_data_main:
            col = int(asset['level'])
            if col > 0:
                col = col - 1
            if col != 2:
                style = text_style_bold
                money_style = money_header_style
            else:
                style = text_style
                money_style = money
            # Name
            sheet.write(row, col, asset['name'], style)
            col = 4
            # Amount
            sheet.write(row, col, asset['amount'], money_style)
            row += 1
            no += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
