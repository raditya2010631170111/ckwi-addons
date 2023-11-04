# -*- coding: utf-8 -*-
from odoo import api, models, _
from datetime import date
import calendar
from dateutil.relativedelta import relativedelta


class InsReportBalanceSheetChugai(models.AbstractModel):
    _name = 'report.jidoka_dynamic_accounts_report.balance_sheet'

    @api.model
    def _get_report_values(self, docids, data=None):
        if self.env.context.get('bs_report'):
            if data.get('report_data'):
                filters = data.get('report_data')['filters']
                title = data.get('report_data')['name']
                if title == 'Profit and Loss':
                    head = 'Total'
                else:
                    head = 'All'
                headers_table = [head]
                if filters.get('previous_periode', False):
                    for i in range(filters['previous_periode']+1):
                        today = date.today()-relativedelta(months=i)
                        last_day = calendar.monthrange(
                            today.year, today.month)[1]
                        end_date = today.replace(day=last_day)
                        headers_table.append(end_date.strftime('%d/%m/%Y'))

                headers_table.reverse()
                data.update({
                    'Filters': data.get('report_data')['filters'],
                    'account_data': data.get('report_data')['report_lines'],
                    'report_lines': data.get('report_data')['bs_lines'],
                    'report_name': data.get('report_name'),
                    'title': data.get('report_data')['name'],
                    'company': self.env.company,
                    'headers_table': headers_table,
                })

        return data