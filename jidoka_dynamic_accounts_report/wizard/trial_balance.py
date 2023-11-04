# -*- coding: utf-8 -*-
from odoo import models, api

import io
import json
import time
from odoo.exceptions import AccessError, UserError, AccessDenied

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

import logging

_logger = logging.getLogger(__name__)


class TrialBalanceInherit(models.TransientModel):
    _inherit = 'account.trial.balance'

    # Override
    @api.model
    def view_report(self, option):
        r = self.env['account.trial.balance'].search([('id', '=', option[0])])

        data = {
            'display_account': r.display_account,
            'model': self,
            'journals': r.journal_ids,
            'target_move': r.target_move,

        }
        if r.date_from:
            data.update({
                'date_from': r.date_from,
            })
        if r.date_to:
            data.update({
                'date_to': r.date_to,
            })

        filters = self.get_filter(option)
        records = self._get_report_values(data)
        currency = self._get_currency()

        return {
            'name': "Trial Balance",
            'type': 'ir.actions.client',
            'tag': 't_b',
            'filters': filters,
            'report_lines': records['Accounts'],
            'debit_total': records['debit_total'],
            'credit_total': records['credit_total'],
            'Init_debit_total': records['Init_debit_total'],
            'Init_credit_total': records['Init_credit_total'],
            'End_debit_total': records['End_debit_total'],
            'End_credit_total': records['End_credit_total'],
            'currency': currency,
        }

    # Override
    def _get_report_values(self, data):
        docs = data['model']
        display_account = data['display_account']
        journals = data['journals']
        accounts = self.env['account.account'].search([])
        if not accounts:
            raise UserError(_("No Accounts Found! Please Add One"))
        account_res = self._get_accounts(accounts, display_account, data)
        debit_total = 0
        debit_total = sum(x['debit'] for x in account_res)
        credit_total = sum(x['credit'] for x in account_res)
        Init_debit_total = sum(x['Init_balance']['debit']
                               for x in account_res if 'Init_balance' in x and x['Init_balance'])
        Init_credit_total = sum(x['Init_balance']['credit']
                                for x in account_res if 'Init_balance' in x and x['Init_balance'])
        End_debit_total = sum(x['End_balance']['debit']
                              for x in account_res if 'End_balance' in x and x['End_balance'])
        End_credit_total = sum(x['End_balance']['credit']
                               for x in account_res if 'End_balance' in x and x['End_balance'])
        return {
            'doc_ids': self.ids,
            'debit_total': debit_total,
            'credit_total': credit_total,
            'Init_debit_total': Init_debit_total,
            'Init_credit_total': Init_credit_total,
            'End_debit_total': End_debit_total,
            'End_credit_total': End_credit_total,
            'docs': docs,
            'time': time,
            'Accounts': account_res,
        }

    # Override
    def _get_accounts(self, accounts, display_account, data):

        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get(
        )
        tables = tables.replace('"', '')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        if data['target_move'] == 'posted':
            filters += " AND account_move_line__move_id.state = 'posted'"
        else:
            filters += " AND account_move_line__move_id.state in ('draft','posted')"
        if data.get('date_from'):
            filters += " AND account_move_line.date >= '%s'" % data.get(
                'date_from')
        if data.get('date_to'):
            filters += " AND account_move_line.date <= '%s'" % data.get(
                'date_to')

        if data['journals']:
            filters += ' AND jrnl.id IN %s' % str(
                tuple(data['journals'].ids) + tuple([0]))
        tables += 'JOIN account_journal jrnl ON (account_move_line.journal_id=jrnl.id)'
        # compute the balance, debit and credit for the provided accounts
        request = (
            "SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +
            " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        account_res = []
        display_account = 'all'
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['name'] = account.name
            res['id'] = account.id
            # _logger.info(
            #     '=================================================================')
            if data.get('date_from'):

                res['Init_balance'] = self.get_init_bal(
                    account, display_account, data)
                _logger.info(res['Init_balance'])

            if account.id in account_result:
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')

            if data.get('date_from'):
                debit = res['debit']
                credit = res['credit']
                balance = res['balance']
                if 'Init_balance' in res and res['Init_balance']:
                    debit += res['Init_balance']['debit']
                    credit += res['Init_balance']['credit']
                    balance += res['Init_balance']['balance']

                balance_cmp = debit-credit
                if balance_cmp < 0:
                    debit = 0
                    credit = abs(balance_cmp)
                else:
                    debit = abs(balance_cmp)
                    credit = 0

                res['End_balance'] = {
                    'id': account.id,
                    'debit': debit,
                    'credit': credit,
                    'balance': balance,
                }

                _logger.info(res['End_balance'])
            # _logger.info(
            #     '=================================================================')

            if data.get('date_from'):
                if 'Init_balance' in res and res['Init_balance']:
                    init_balance = res['Init_balance']['debit'] - \
                        res['Init_balance']['credit']
                    if init_balance > 0:
                        res['Init_balance']['debit'] = abs(init_balance)
                        res['Init_balance']['credit'] = 0
                    elif init_balance < 0:
                        res['Init_balance']['debit'] = 0
                        res['Init_balance']['credit'] = abs(init_balance)
                    else:
                        res['Init_balance']['debit'] = 0
                        res['Init_balance']['credit'] = 0
            else:
                # Manipulasi End Bal
                end_balance = res['debit']-res['credit']
                if end_balance > 0:
                    res['debit'] = abs(end_balance)
                    res['credit'] = 0
                elif end_balance < 0:
                    res['debit'] = 0
                    res['credit'] = abs(end_balance)
                else:
                    res['debit'] = 0
                    res['credit'] = 0

            if display_account == 'all':
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(
                    res['balance']):
                account_res.append(res)
            if display_account == 'movement' and (
                    not currency.is_zero(res['debit']) or not currency.is_zero(
                    res['credit'])):
                account_res.append(res)
        return account_res

    # REPORT EXCEL

    def get_dynamic_xlsx_report(self, data, response, report_data, dfr_data):
        report_data_main = json.loads(report_data)
        output = io.BytesIO()
        total = json.loads(dfr_data)
        filters = json.loads(data)
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        # buat style untuk mengatur jenis font, ukuran font, border dan alligment
        title_style = workbook.add_format(
            {'font_name': 'Times', 'font_size': 14, 'bold': True, 'align': 'center'})
        title_style_red = workbook.add_format(
            {'font_name': 'Times', 'font_size': 14, 'bold': True, 'align': 'center', 'font_color': '#7e0000'})
        header_style = workbook.add_format(
            {'font_name': 'Times', 'bold': True, 'bottom': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'font_color': '#00007e'})
        text_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right'})
        text_style_bold = workbook.add_format(
            {'font_name': 'Times', 'bold': True, 'align': 'center', })
        # text_style_bold = workbook.add_format(
        #     {'font_name': 'Times', 'bold': True, 'align': 'center', 'bottom': 6}) # double underline
        number_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center'})
        money = workbook.add_format(
            {'num_format': '_(Rp* #,##0_);[Red]_(Rp* (#,##0);_(Rp* "-"_);_(@_)', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right'})
        money_total = workbook.add_format(
            {'bold': True, 'num_format': '_(Rp *  # ,##0_);[Red]_(Rp* (#,##0);_(Rp* "-"_);_(@_)', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right'})

        head = workbook.add_format({'align': 'center', 'bold': True,
                                    'font_size': '20px'})
        sub_heading = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '10px',
             'border': 1,
             'border_color': 'black',
             'font_color': '#5159af'})
        txt = workbook.add_format({'font_size': '10px', 'border': 1})
        txt_l = workbook.add_format(
            {'font_size': '10px', 'border': 1, 'bold': True})
        # sheet.merge_range('A2:D3', filters.get(
        #     'company_name') + ':' + ' Trial Balance', head)
        sheet.merge_range(
            'A1:F1', filters.get('company_name'), title_style)
        sheet.merge_range(
            'A2:F2', 'Trial Balance', title_style_red)

        date_head = workbook.add_format({'align': 'center', 'bold': True,
                                         'font_size': '10px'})
        date_style = workbook.add_format({'align': 'center',
                                          'font_size': '10px'})

        periode = ''
        if filters.get('date_from'):
            periode += 'From: ' + filters.get('date_from')
        if filters.get('date_to'):
            periode += 'To: ' + filters.get('date_to')

        sheet.merge_range(
            'A3:F3', periode, text_style_bold)
        # sheet.merge_range('A5:D6', 'Journals: ' + ', '.join(
        #     [lt or '' for lt in filters['journals']]) + '  Target Moves: ' + filters.get('target_move'), date_head)
        sheet.write('A7', 'Account  No', sub_heading)
        sheet.write('B7', 'Account Name', sub_heading)
        if filters.get('date_from'):
            sheet.write('C7', 'Op Bal Debit', sub_heading)
            sheet.write('D7', 'Op Bal Credit', sub_heading)
            sheet.write('E7', 'Change Debit', sub_heading)
            sheet.write('F7', 'Change Credit', sub_heading)
            sheet.write('G7', 'End Bal Debit', sub_heading)
            sheet.write('H7', 'End Bal Credit', sub_heading)
        else:
            sheet.write('C7', 'End Bal Debit', sub_heading)
            sheet.write('D7', 'End Bal Credit', sub_heading)

        row = 6
        col = 0
        sheet.set_column(5, 0, 15)
        sheet.set_column(6, 1, 15)
        sheet.set_column('C:H', 26)

        for rec_data in report_data_main:

            row += 1
            sheet.write(row, col, rec_data['code'], txt)
            sheet.write(row, col + 1, rec_data['name'], txt)
            if filters.get('date_from'):
                if rec_data.get('Init_balance'):
                    sheet.write(
                        row, col + 2, rec_data['Init_balance']['debit'], money)
                    sheet.write(
                        row, col + 3, rec_data['Init_balance']['credit'], money)
                else:
                    sheet.write(row, col + 2, 0, money)
                    sheet.write(row, col + 3, 0, money)

                sheet.write(row, col + 4, rec_data['debit'], money)
                sheet.write(row, col + 5, rec_data['credit'], money)

                if rec_data.get('End_balance'):
                    sheet.write(
                        row, col + 6, rec_data['End_balance']['debit'], money)
                    sheet.write(
                        row, col + 7, rec_data['End_balance']['credit'], money)
                else:
                    sheet.write(row, col + 6, 0, money)
                    sheet.write(row, col + 7, 0, money)

            else:
                sheet.write(row, col + 2, rec_data['debit'], money)
                sheet.write(row, col + 3, rec_data['credit'], money)
        sheet.write(row+1, col, 'Total', sub_heading)
        if filters.get('date_from'):
            sheet.write(row + 1, col + 2,
                        total.get('Init_debit_total'), money_total)
            sheet.write(row + 1, col + 3,
                        total.get('Init_credit_total'), money_total)
            sheet.write(row + 1, col + 4,
                        total.get('debit_total'), money_total)
            sheet.write(row + 1, col + 5,
                        total.get('credit_total'), money_total)
            sheet.write(row + 1, col + 6,
                        total.get('End_debit_total'), money_total)
            sheet.write(row + 1, col + 7,
                        total.get('End_credit_total'), money_total)
        else:
            sheet.write(row + 1, col + 2,
                        total.get('debit_total'), money_total)
            sheet.write(row + 1, col + 3,
                        total.get('credit_total'), money_total)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
