# -*- coding: utf-8 -*-
import re
import time
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import calendar
import json
import io
import logging
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

_logger = logging.getLogger(__name__)


class BalanceSheetInherit(models.TransientModel):
    _inherit = "dynamic.balance.sheet.report"

    previous_periode = fields.Integer(string='Number of comparation')
    periode_start = fields.Char(string='Periode Start')
    periode_end = fields.Char(string='Periode End')

    # OVERRIDE
    @api.model
    def view_report(self, option, tag):
        if tag == 'Profit and Loss':
            head = 'Total'
        else:
            head = 'All'
        headers_table = [head]
        r = self.env['dynamic.balance.sheet.report'].search(
            [('id', '=', option[0])])
        data = {
            'display_account': r.display_account,
            'model': self,
            'journals': r.journal_ids,
            'target_move': r.target_move,
            'accounts': r.account_ids,
            'account_tags': r.account_tag_ids,
            'analytics': r.analytic_ids,
            'analytic_tags': r.analytic_tag_ids,
            'tag': tag,
        }
        if r.date_from:
            data.update({
                'date_from': r.date_from,
            })
        if r.date_to:
            data.update({
                'date_to': r.date_to,
            })
        selisih = 0
        date_periode_start = date_periode_end = False

        if not r.periode_start and r.periode_end:
            raise UserError(_('Please fill periode start'))
        else:
            if r.periode_start:
                try:
                    date_periode_start = datetime.strptime(
                        r.periode_start, '%Y-%m')
                except:
                    raise UserError(
                        _("Format 'Periode start' tidak sesuai dengan 'yyyy-mm'. contoh: 2022-10 (untuk bulan oktober 2022)"))
            if r.periode_end:
                try:
                    date_periode_end = datetime.strptime(
                        r.periode_end, '%Y-%m')
                except:
                    raise UserError(
                        _("Format 'Periode end' tidak sesuai dengan 'yyyy-mm'. contoh: 2022-10 (untuk bulan oktober 2022)"))
            else:
                # jika tidak ada end gunakan awal bulan ini
                date_periode_end = datetime.now().replace(day=1, hour=0, minute=0, second=0)

        # untuk Profit & lost wajib ada periode start, jika tidak ada maka set awal tahun ini
        if tag == 'Profit and Loss':
            if date_periode_end and not date_periode_start:
                date_periode_start = date_periode_end.replace(month=1,
                                                              day=1, hour=0, minute=0, second=0)

        if date_periode_start and date_periode_end:
            if date_periode_start > date_periode_end:
                raise UserError(
                    _('Periode start harus lebih awal dari periode end'))
            else:
                selisih = ((date_periode_end.year-date_periode_start.year) *
                           12+(date_periode_end.month-date_periode_start.month))+1
                data.update({
                    'periode_start': date_periode_start,
                    'periode_end': date_periode_end,
                })

        if selisih:
            data.update({
                'previous_periode': selisih,
            })
            for i in range(selisih):
                today = date_periode_end-relativedelta(months=i)
                last_day = calendar.monthrange(today.year, today.month)[1]
                end_date = today.replace(day=last_day)
                headers_table.append(end_date.strftime('%d/%m/%Y'))

        company_id = self.env.company
        company_domain = [('company_id', '=', company_id.id)]
        if r.account_tag_ids:
            company_domain.append(
                ('tag_ids', 'in', r.account_tag_ids.ids))
        if r.account_ids:
            company_domain.append(('id', 'in', r.account_ids.ids))

        new_account_ids = self.env['account.account'].search(company_domain)
        data.update({'accounts': new_account_ids, })

        filters = self.get_filter(option)
        records = self._get_report_values(data)

        if filters['account_tags'] != ['All']:
            tag_accounts = list(map(lambda x: x.code, new_account_ids))

            def filter_code(rec_dict):
                if rec_dict['code'] in tag_accounts:
                    return True
                else:
                    return False

            new_records = list(filter(filter_code, records['Accounts']))
            records['Accounts'] = new_records

        account_report_id = self.env['account.financial.report'].search([
            ('name', 'ilike', tag)])
        # jika Profit & Loss date_from harus dari awal tahun yang sama, atau dari from secara default
        if tag == 'Profit and Loss':
            date_from = date_periode_start or date_periode_end.replace(
                month=1, day=1, hour=0, minute=0, second=0)
        else:
            date_from = False
            
        if data.get('previous_periode', False):
            # function untuk merubuah struktur list dict menjadi dict dengan key
            # sesuai yang diinginkan
            def build_dict(seq, key):
                return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))

            report_lines = False

            # simpan account_res per periode nya
            list_report_lines = []
            for i in range(data['previous_periode']+1):
                if i:
                    today = data['periode_end'] - relativedelta(months=(i-1))
                    last_day = calendar.monthrange(today.year, today.month)[1]
                    if tag == 'Profit and Loss':
                        date_from = today.replace(day=1)
                    date_to = today.replace(day=last_day)
                else:
                    date_to = False

                new_data_custom = {'id': self.id,
                                    'date_from': date_from,
                                   'enable_filter': True,
                                   'debit_credit': True,
                                   'date_to': date_to,
                                   'account_report_id': account_report_id,
                                   'target_move': filters['target_move'],
                                   'view_format': 'vertical',
                                   'company_id': self.company_id,
                                   'previous_periode': data.get('previous_periode', False),
                                   'used_context': {'journal_ids': False,
                                                    'state': filters['target_move'].lower(),
                                                    'date_from': date_from,
                                                    'date_to': date_to,
                                                    'strict_range': False,
                                                    'company_id': self.company_id,
                                                    'lang': 'en_US'}}

                account_lines_custom = self.get_account_lines(new_data_custom)
                report_lines_custom = self.view_report_pdf(
                    account_lines_custom, new_data_custom)['report_lines']

                list_report_lines.append(report_lines_custom)

            if not report_lines and list_report_lines:
                report_lines = list_report_lines[0].copy()
                i = 0
                for ls in list_report_lines:
                    if i:
                        # key balance periode sebelumnya
                        key = 'balance_{}'.format(str(i))
                    else:
                        key = 'balance'  # key balance periode sekarang

                    for res in report_lines:
                        account_by_id = build_dict(ls, key="id")
                        account_info = account_by_id.get(res['id'])

                        # mencari account berdasarkan id saat periode ini (yang di looping)
                        if account_info:
                            account_index = account_info['index']
                            balance = ls[account_index]['balance']
                        else:
                            balance = 0

                        res[key] = balance
                    i += 1
        else:
            # jika tidak ada parameter comparasion, ikuti default odoo
            new_data = {'id': self.id, 'date_from': date_from,
                        'enable_filter': True,
                        'debit_credit': True,
                        'date_to': False, 'account_report_id': account_report_id,
                        'target_move': filters['target_move'],
                        'view_format': 'vertical',
                        'company_id': self.company_id,
                        'previous_periode': data.get('previous_periode', False),
                        'used_context': {'journal_ids': False,
                                         'state': filters['target_move'].lower(),
                                         'date_from': date_from,
                                         'date_to': filters['date_to'],
                                         'strict_range': False,
                                         'company_id': self.company_id,
                                         'lang': 'en_US'}}

            account_lines = self.get_account_lines(new_data)
            report_lines = self.view_report_pdf(
                account_lines, new_data)['report_lines']

        move_line_accounts = []
        move_lines_dict = {}

        for rec in records['Accounts']:
            move_line_accounts.append(rec['code'])
            move_lines_dict[rec['code']] = {}
            move_lines_dict[rec['code']]['debit'] = rec['debit']
            move_lines_dict[rec['code']]['credit'] = rec['credit']
            # move_lines_dict[rec['code']]['balance'] = rec['balance']

            if data.get('previous_periode', False):
                for i in range(data['previous_periode']+1):
                    if i:
                        key = 'balance_{}'.format(str(i))
                    else:
                        key = 'balance'
                    move_lines_dict[rec['code']][key] = rec[key]
            else:
                move_lines_dict[rec['code']]['balance'] = rec['balance']
        report_lines_move = []
        parent_list = []

        def filter_movelines_parents(obj):
            for each in obj:
                if each['report_type'] == 'accounts':
                    if 'code' in each and each['code'] in move_line_accounts:
                        report_lines_move.append(each)
                        parent_list.append(each['p_id'])

                elif each['report_type'] == 'account_report':
                    report_lines_move.append(each)
                else:
                    report_lines_move.append(each)

        filter_movelines_parents(report_lines)

        for rec in report_lines_move:
            if rec['report_type'] == 'accounts':
                if rec['code'] in move_line_accounts:
                    rec['debit'] = move_lines_dict[rec['code']]['debit']
                    rec['credit'] = move_lines_dict[rec['code']]['credit']
                    # rec['balance'] = move_lines_dict[rec['code']]['balance']

                    if data.get('previous_periode', False):
                        for i in range(data['previous_periode']+1):
                            if i:
                                key = 'balance_{}'.format(str(i))
                            else:
                                key = 'balance'
                            rec[key] = move_lines_dict[rec['code']][key]
                    else:
                        rec['balance'] = move_lines_dict[rec['code']]['balance']

        parent_list = list(set(parent_list))
        max_level = 0
        for rep in report_lines_move:
            if rep['level'] > max_level:
                max_level = rep['level']

        def get_parents(obj):
            for item in report_lines_move:
                for each in obj:
                    if item['report_type'] != 'account_type' and \
                            each in item['c_ids']:
                        obj.append(item['r_id'])
                if item['report_type'] == 'account_report':
                    obj.append(item['r_id'])
                    # tidak break, karena mungkin banyak report value!!!
                    # break

        get_parents(parent_list)

        for i in range(max_level):
            get_parents(parent_list)

        parent_list = list(set(parent_list))
        final_report_lines = []

        for rec in report_lines_move:
            # append, jika type bukan akun dan ada di list parent
            if rec['report_type'] != 'accounts':
                if rec['r_id'] in parent_list:
                    final_report_lines.append(rec)
            else:
                # append, jika type accounts
                final_report_lines.append(rec)

        def filter_sum(obj):
            sum_list = {}
            for pl in parent_list:
                sum_list[pl] = {}
                sum_list[pl]['s_debit'] = 0
                sum_list[pl]['s_credit'] = 0
                if data.get('previous_periode', False):
                    for i in range(data['previous_periode']+1):
                        if i:
                            s_key = 's_balance_{}'.format(str(i))
                        else:
                            s_key = 's_balance'
                        sum_list[pl][s_key] = 0
                else:
                    sum_list[pl]['s_balance'] = 0
            for each in obj:
                if each['p_id'] and each['p_id'] in parent_list:
                    sum_list[each['p_id']]['s_debit'] += each['debit']
                    sum_list[each['p_id']]['s_credit'] += each['credit']
                    # sum_list[each['p_id']]['s_balance'] += each['balance']

                    # Total balance parent
                    if data.get('previous_periode', False):
                        for i in range(data['previous_periode']+1):
                            if i:
                                s_key = 's_balance_{}'.format(str(i))
                                key = 'balance_{}'.format(str(i))
                            else:
                                s_key = 's_balance'
                                key = 'balance'
                            sum_list[each['p_id']][s_key] += each[key]
                    else:
                        sum_list[each['p_id']]['s_balance'] += each['balance']

            return sum_list

        def assign_sum(obj):
            for each in obj:
                if each['r_id'] in parent_list and \
                        each['report_type'] != 'account_report':
                    if 'not_total' in each and each['not_total']:
                        each['debit'] = 0
                        each['credit'] = 0
                    else:
                        each['debit'] = sum_list_new[each['r_id']]['s_debit']
                        each['credit'] = sum_list_new[each['r_id']]['s_credit']
                    if data.get('previous_periode', False):
                        for i in range(data['previous_periode']+1):
                            if i:
                                s_key = 's_balance_{}'.format(str(i))
                                key = 'balance_{}'.format(str(i))
                            else:
                                s_key = 's_balance'
                                key = 'balance'
                            if 'not_total' in each and each['not_total']:
                                each[key] = 0
                            else:
                                each[key] = sum_list_new[each['r_id']][s_key]

        for p in range(max_level):
            sum_list_new = filter_sum(final_report_lines)
            assign_sum(final_report_lines)

        company_id = self.env.company
        currency = company_id.currency_id
        symbol = currency.symbol
        rounding = currency.rounding
        position = currency.position

        # berlaku untuk semua
        # if tag == 'Profit and Loss':
        for rec in final_report_lines:
            total_balance = 0
            if data.get('previous_periode', False):
                for i in range(data['previous_periode']+1):
                    if i:
                        key = 'balance_{}'.format(str(i))
                        total_balance += rec[key]

            rec['total_balance'] = total_balance

        for rec in final_report_lines:
            rec['debit'] = round(rec['debit'], 2)
            rec['credit'] = round(rec['credit'], 2)
            rec['balance'] = rec['debit'] - rec['credit']
            rec['balance'] = round(rec['balance'], 2)
            if (rec['balance_cmp'] < 0 and rec['balance'] > 0) or (rec['balance_cmp'] > 0 and rec['balance'] < 0):
                rec['balance'] = rec['balance'] * -1

            if position == "before":
                rec['m_debit'] = symbol + " " + "{:,.2f}".format(rec['debit'])
                rec['m_credit'] = symbol + " " + \
                    "{:,.2f}".format(rec['credit'])
                rec['m_balance'] = symbol + " " + "{:,.2f}".format(
                    rec['balance'])

                if data.get('previous_periode', False):
                    for i in range(data['previous_periode']+1):
                        if i:
                            m_key = 'm_balance_{}'.format(str(i))
                            key = 'balance_{}'.format(str(i))
                        else:
                            m_key = 'm_balance'
                            key = 'balance'

                        if 'not_total' in rec and rec['not_total']:
                            rec[m_key] = ""
                        else:
                            rec[m_key] = symbol + " " + \
                                "{:,.2f}".format(rec[key]*int(rec['sign']))
                else:
                    rec['m_balance'] = symbol + " " + \
                        "{:,.2f}".format(rec['balance'])

                if tag == 'Profit and Loss' and 'total_balance' in rec:
                    rec['m_total_balance'] = symbol + " " + \
                        "{:,.2f}".format(rec['total_balance']*int(rec['sign']))
            else:
                rec['m_debit'] = "{:,.2f}".format(rec['debit']) + " " + symbol
                rec['m_credit'] = "{:,.2f}".format(
                    rec['credit']) + " " + symbol
                rec['m_balance'] = "{:,.2f}".format(
                    rec['balance']) + " " + symbol

                if data.get('previous_periode', False):
                    for i in range(data['previous_periode']+1):
                        if i:
                            m_key = 'm_balance_{}'.format(str(i))
                            key = 'balance_{}'.format(str(i))
                        else:
                            m_key = 'm_balance'
                            key = 'balance'
                        if 'not_total' in rec and rec['not_total']:
                            rec[m_key] = ""
                        else:
                            rec[m_key] = "{:,.2f}".format(
                                rec[key]*int(rec['sign'])) + " " + symbol
                else:
                    rec['m_balance'] = "{:,.2f}".format(
                        rec['balance']) + " " + symbol

                if tag == 'Profit and Loss' and 'total_balance' in rec:
                    rec['m_total_balance'] = "{:,.2f}".format(
                        rec['total_balance']) + " " + symbol

            if 'not_total' in rec and rec['not_total']:
                rec['m_debit'] = ''
                rec['m_credit'] = ''
                rec['m_balance'] = ''
                rec['m_total_balance'] = ''

        headers_table.reverse()
        filters['previous_periode'] = data.get('previous_periode', False)
        filters['periode_start'] = data.get('periode_start', False)
        filters['periode_end'] = data.get('periode_end', False)

        # delete 0 balance (balance_cmp) from final_report_lines
        def _is_all_nol(list_amt):
            if not list_amt:
                return True
            for l in list_amt:
                if l:
                    return False
            return True

        if data.get('previous_periode', False):
            final_report_lines = [rec for rec in final_report_lines if rec['report_type'] != 'accounts' or (
                    rec['report_type'] == 'accounts' and not _is_all_nol(
                        [rec['balance_%s' % x] for x in range(data.get('previous_periode',0)+1) if x != 0]
                    )
                )]
        else:
            final_report_lines = [rec for rec in final_report_lines if rec['report_type'] != 'accounts' or (
                rec['report_type'] == 'accounts' and rec['balance'])]

        return {
            'name': tag,
            'type': 'ir.actions.client',
            'tag': tag,
            'filters': filters,
            'report_lines': records['Accounts'],
            'debit_total': records['debit_total'],
            'credit_total': records['credit_total'],
            'debit_balance': records['debit_balance'],
            'currency': currency,
            'bs_lines': final_report_lines,
            'headers_table': headers_table,
            'today': date.today().strftime('%d/%m/%Y'),
        }

    # OVERRIDE
    def _get_report_values(self, data):
        docs = data['model']
        display_account = data['display_account']
        init_balance = True
        journals = data['journals']
        accounts = self.env['account.account'].search([])
        if not accounts:
            raise UserError(_("No Accounts Found! Please Add One"))
        # Jika ada parameter comparasion
        # Tujuannya hanya menambahkan nilai balance di periode sebelumnya ke variabel 
        # account_res bawaan odoo
        if data.get('previous_periode', False):
            # function untuk merubuah struktur list dict menjadi dict dengan key sesuai yang diinginkan
            def build_dict(seq, key):
                return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))

            account_res = False

            # simpan account_res per periode nya
            list_account_res = []
            for i in range(data['previous_periode']+1):
                # jika bukan 0
                if i:
                    today = data['periode_end'] - relativedelta(months=(i-1))
                    last_day = calendar.monthrange(today.year, today.month)[1]
                    # jika PL date_from selalu awal bulan bersangkutan
                    if data['tag'] == 'Profit and Loss':
                        date_from = today.replace(day=1)
                        data['date_from'] = date_from
                    # date to selalu akhir bulan bersangkutan
                    date_to = today.replace(day=last_day)
                    data['date_to'] = date_to
                account_res_custom = self._get_accounts(accounts, init_balance,
                                                        display_account, data)
                list_account_res.append(account_res_custom)

            if not account_res and list_account_res:
                account_res = list_account_res[0].copy()
                i = 0
                for ls in list_account_res:
                    if i:
                        # key balance periode sebelumnya
                        key = 'balance_{}'.format(str(i))
                    else:
                        key = 'balance'  # key balance periode sekarang

                    for res in account_res:
                        account_by_id = build_dict(ls, key="id")
                        account_info = account_by_id.get(res['id'])

                        # mencari account berdasarkan id saat periode ini (yang di looping)
                        if account_info:
                            account_index = account_info['index']
                            balance = ls[account_index]['balance']
                        else:
                            balance = 0

                        res[key] = balance
                    i += 1

                if 'tag' in data and data['tag'] == 'Profit and Loss':
                    for rec in account_res:
                        total_balance = 0
                        if data.get('previous_periode', False):
                            for i in range(data['previous_periode']+1):
                                if i:
                                    key = 'balance_{}'.format(str(i))
                                    total_balance += rec[key]

                        rec['total_balance'] = total_balance
        else:
            # jika tidak ada parameter comparasion, ikuti default odoo
            account_res = self._get_accounts(accounts, init_balance,
                                             display_account, data)
        debit_total = 0
        debit_total = sum(x['debit'] for x in account_res)
        credit_total = sum(x['credit'] for x in account_res)
        debit_balance = round(debit_total, 2) - round(credit_total, 2)
        return {
            'doc_ids': self.ids,
            'debit_total': debit_total,
            'credit_total': credit_total,
            'debit_balance': debit_balance,
            'docs': docs,
            'time': time,
            'Accounts': account_res,
        }
    # method to analysis
    # def _compute_report_balance
    # def get_account_lines

    def get_account_lines(self, data):
        lines = []
        account_report = data['account_report_id']
        child_reports = account_report._get_children_by_order()
        res = self.with_context(
            data.get('used_context'))._compute_report_balance(child_reports)
        if data['enable_filter']:
            comparison_res = self._compute_report_balance(child_reports)
            for report_id, value in comparison_res.items():
                res[report_id]['comp_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in \
                            comparison_res[report_id].get('account').items():
                        report_acc[account_id]['comp_bal'] = val['balance']

        for report in child_reports:
            r_name = str(report.name)
            r_name = re.sub('[^0-9a-zA-Z]+', '', r_name)
            if report.parent_id:
                p_name = str(report.parent_id.name)
                p_name = re.sub('[^0-9a-zA-Z]+', '', p_name) + str(
                    report.parent_id.id)
            else:
                p_name = False

            child_ids = []
            for chd in report.children_ids:
                child_ids.append(chd.id)

            vals = {
                'r_id': report.id,
                'p_id': report.parent_id.id,
                'report_type': report.type,
                'c_ids': child_ids,
                'id': r_name + str(report.id),
                'sequence': report.sequence,
                'parent': p_name,
                'name': report.name,
                'sign': report.sign,
                'balance': res[report.id]['balance'] * int(report.sign),
                'type': 'report',
                'level': bool(
                    report.style_overwrite) and report.style_overwrite or
                report.level,
                'account_type': report.type or False,
                'is_present': False,
                'is_no_children': report.is_no_children or False,
                'is_hidden': report.is_hidden or False,
                # used to underline the financial report balances
                # TODO remove me, name alias
                # 'name_alias': report.name_alias or '',
            }
            if data['debit_credit']:
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']

            if data['enable_filter']:
                vals['balance_cmp'] = res[report.id]['comp_bal'] * int(
                    report.sign)

            lines.append(vals)

            if report.display_detail == 'no_detail':
                # the rest of the loop is
                # used to display the details of the
                #  financial report, so it's not needed here.
                continue

            if res[report.id].get('account'):
                sub_lines = []
                for account_id, value \
                        in res[report.id]['account'].items():
                    # if there are accounts to display,
                    #  we add them to the lines with a level equals
                    #  to their level in
                    # the COA + 1 (to avoid having them with a too low level
                    #  that would conflicts with the level of data
                    # financial reports for Assets, liabilities...)
                    flag = False
                    account = self.env['account.account'].browse(account_id)
                    vals = {
                        'r_id': False,
                        'p_id': report.id,
                        'report_type': 'accounts',
                        'c_ids': [],
                        'account': account.id,
                        'code': account.code,
                        'id': account.code + re.sub('[^0-9a-zA-Z]+', 'acnt',
                                                    account.name) + str(
                            account.id),
                        'a_id': account.code + re.sub('[^0-9a-zA-Z]+', 'acnt',
                                                      account.name) + str(
                            account.id),
                        'name': account.code + '-' + account.name,
                        'sign': report.sign,
                        'balance': value['balance'] * int(report.sign) or 0.0,
                        'type': 'account',
                        'parent': r_name + str(report.id),
                        'level': (
                                report.display_detail == 'detail_with_hierarchy' and
                                4),
                        'account_type': account.internal_type,
                        'is_no_children': report.is_no_children or False,
                        'is_hidden': report.is_hidden or False,
                        # TODO remove me, name alias
                        # 'name_alias': account.name_alias or '',

                    }
                    if data['debit_credit']:
                        vals['debit'] = value['debit']
                        vals['credit'] = value['credit']
                        if not account.company_id.currency_id.is_zero(
                                vals['debit']) or \
                                not account.company_id.currency_id.is_zero(
                                    vals['credit']):
                            flag = True
                    if not account.company_id.currency_id.is_zero(
                            vals['balance']):
                        flag = True
                    if data['enable_filter']:
                        vals['balance_cmp'] = value['comp_bal'] * int(
                            report.sign)
                        if not account.company_id.currency_id.is_zero(
                                vals['balance_cmp']):
                            flag = True
                    if flag:
                        sub_lines.append(vals)

                if not report.is_no_children:
                    # Duplicate data parent
                    line_parent = lines[-1].copy()
                    line_parent.update({
                        'id': 'Wakwaw'+line_parent['id'],
                        'name': 'Total '+line_parent['name'],
                    })
                    lines[-1].update({
                        'not_total': True,
                        'debit': 0,
                        'credit': 0,
                        'balance': 0,
                        'balance_cmp': 0,
                    })

                    sub_lines.append(line_parent)

                lines += sorted(sub_lines,
                                key=lambda sub_line: sub_line['name'])

            if report.type == 'total':
                def build_dict(seq, key):
                    return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))

                account_by_r_id = build_dict(lines, 'r_id')
                account_info = account_by_r_id.get(report.parent_id.id)
                if account_info:
                    account_parent = lines[account_info['index']]
                    acc_total = account_parent.copy()
                    acc_total.update({
                        'id': r_name + str(report.id),
                        'name': report.name,
                    })
                    account_parent.update({
                        'not_total': True,
                        'debit': 0,
                        'credit': 0,
                        'balance': 0,
                        'balance_cmp': 0,
                    })
                    lines.append(acc_total)
        return lines

    # REPORT EXCEL
    # OVERRIDE

    def get_dynamic_xlsx_report(self, options, response, report_data, dfr_data):
        i_data = str(report_data)
        filters = json.loads(options)
        j_data = dfr_data
        rl_data = json.loads(j_data)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        # buat style untuk mengatur jenis font, ukuran font, border dan alligment
        title_style = workbook.add_format({
            'font_name': 'Times',
            'font_size': 14,
            'bold': True,
            'align': 'center',
        })
        title_style_red = workbook.add_format({
            'font_name': 'Times',
            'font_size': 14,
            'bold': True,
            'align': 'center',
            'font_color': '#7e0000',
        })
        text_style = workbook.add_format({
            'font_name': 'Times',
            'align': 'right',
        })
        text_style_bold = workbook.add_format(
            {'font_name': 'Times', 'bold': True, 'align': 'center', })
        money = workbook.add_format({
            'num_format': '_(Rp* #,##0_);[Red]_(Rp* (#,##0);_(Rp* "-"_);_(@_)',
            'align': 'right',
        })
        money_total = workbook.add_format({
            'bold': True,
            'num_format': '_(Rp* #,##0_);[Red]_(Rp* (#,##0);_(Rp* "-"_);_(@_)',
            'align': 'right',
            # 'font_color': '#00007e',
        })

        head = workbook.add_format({
            'align': 'center',
            'bold': True,
            'font_size': '20px',
        })
        sub_heading = workbook.add_format({
            'align': 'center',
            'bold': True,
            'font_size': '10px',
            # 'border': 1,
            'bold': True,
            'border_color': 'black',
            'font_color': '#5159af',
        })
        side_heading_main = workbook.add_format({
            'align': 'left',
            'bold': True,
            'font_size': '10px',
            # 'border': 1,
            'border_color': 'black',
        })

        side_heading_sub = workbook.add_format({
            'align': 'left',
            'bold': True,
            'font_size': '10px',
            # 'border': 1,
            'border_color': 'black',
        })

        side_heading_sub.set_indent(1)
        txt_name = workbook.add_format({
            'font_size': '10px',
            # 'border': 1,
        })
        txt_name_bold = workbook.add_format({
            'font_size': '10px',
            # 'border': 1,
            'bold': True,
        })
        txt_name.set_indent(2)
        txt_name_bold.set_indent(2)

        # txt = workbook.add_format({'font_size': '10px', 'border': 1})

        # sheet.merge_range('A2:D3',
        #                   filters.get('company_name') + ' : ' + i_data,
        #                   head)
        # title
        sheet.merge_range(
            'A1:F1', filters.get('company_name'), title_style)
        sheet.merge_range(
            'A2:F2', i_data, title_style_red)

        period_end_str = filters.get('period_end')

        today = period_end_str and datetime.strptime(filters['periode_end'], '%Y-%m-%d %H:%M:%S') \
            or datetime.now()

        period_from = False
        period_to = today.strftime('%B %Y')
        if filters.get('previous_periode', False):
            filters['previous_periode'] = filters['previous_periode']-1
            period_from = (
                today - relativedelta(months=filters['previous_periode'])).strftime('%B %Y')

        if period_from:
            periode = 'Period {} to {}'.format(period_from, period_to)
        else:
            periode = 'Period {}'.format(period_to)
        # periode
        sheet.merge_range(
            'A3:F3', periode, text_style_bold)

        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 1, 30)
        sheet.set_column(2, 2, 30)
        sheet.set_column(3, 20, 20)

        row = 5
        col = 0
        sheet.write(row, col, '', sub_heading)
        sheet.write(row, col+1, 'Account Name', sub_heading)
        sheet.write(row, col+ 2, '日本語勘定科目名', sub_heading)
        if i_data == 'Profit and Loss':
            head = 'Total'
        else:
            head = 'All'
        headers_table = [head]
        if filters.get('previous_periode', False):
            for i in range(filters.get('previous_periode')+1):
                today = datetime.strptime(filters.get(
                    'periode_end'), '%Y-%m-%d %H:%M:%S')-relativedelta(months=i)
                last_day = calendar.monthrange(today.year, today.month)[1]
                end_date = today.replace(day=last_day)
                headers_table.append(end_date.strftime('%d/%m/%Y'))

        headers_table.reverse()
        if len(headers_table) > 1:
            i = 0
            for header in headers_table:
                if i_data == 'Profit and Loss':
                    sheet.write(row, col+3 + i, header, sub_heading)
                else:
                    if header != headers_table[-1]:
                        sheet.write(row, col+3 + i, header, sub_heading)
                i += 1
        else:
            sheet.write(row, col+3, head, sub_heading)

        if rl_data:
            for fr in rl_data:
                if fr != rl_data[0]:
                    if fr.get('code', ''):
                        if not fr.get('is_no_children'):
                            row += 1
                            # code
                            sheet.write(row, col, fr.get(
                                'code', ''), text_style)
                            # name & alias name
                            if fr['level'] == 1:
                                sheet.write(
                                    row, col+1, fr['name'], side_heading_main)
                                # TODO remove me, name alias
                                # sheet.write(
                                #     row, col+2, fr['name_alias'], side_heading_main)
                            elif fr['level'] == 2:
                                sheet.write(
                                    row, col+1, fr['name'], side_heading_sub)
                                # TODO remove me, name alias
                                # sheet.write(
                                #     row, col+2, fr['name_alias'], side_heading_sub)
                            else:
                                sheet.write(row, col+1, fr['name'], txt_name)
                                # TODO remove me, name alias
                                # sheet.write(row, col+2, fr['name_alias'], txt_name)
                            
                            # sheet.write(row, col + 3, fr['balance'], txt)
                            if filters.get('previous_periode', False):
                                x = filters['previous_periode']+1
                                for i in range(filters['previous_periode']+2):
                                    if i_data == 'Profit and Loss':
                                        if x:
                                            key = 'balance_{}'.format(x)
                                        else:
                                            key = 'total_balance'
                                        sheet.write(
                                            row, col+3+i, fr[key]*int(fr['sign']), money)
                                    else:
                                        if x:
                                            key = 'balance_{}'.format(x)
                                            sheet.write(
                                                row, col+3+i, fr[key]*int(fr['sign']), money)
                                    x -= 1
                            else:
                                sheet.write(row, col + 3, fr['balance'], money)
                    else:
                        if not fr['is_hidden']:
                            row += 1
                            # tidak ada code
                            # sheet.write(row, col, fr.get('code', ''), text_style)
                            if fr['level'] == 1:
                                sheet.write(
                                    row, col, fr['name'], side_heading_main)
                                # TODO remove me, name alias
                                # sheet.write(
                                #     row, col+2, fr['name_alias'], side_heading_main)
                            elif fr['level'] == 2:
                                sheet.write(
                                    row, col, fr['name'], side_heading_sub)
                                # TODO remove me, name alias
                                # sheet.write(
                                #     row, col+2, fr['name_alias'], side_heading_sub)
                            else:
                                sheet.write(row, col, fr['name'], side_heading_sub)
                                # TODO remove me, name alias
                                # sheet.write(row, col+2, fr['name_alias'], side_heading_sub)
                            # sheet.write(row, col + 3, fr['balance'], txt)
                            if filters.get('previous_periode', False):
                                x = filters['previous_periode']+1
                                for i in range(filters['previous_periode']+2):
                                    if i_data == 'Profit and Loss':
                                        if x:
                                            key = 'balance_{}'.format(x)
                                        else:
                                            key = 'total_balance'
                                        total = fr[key]*int(fr['sign'])
                                        if not total:
                                            total = ''  # sebagai string jika 0
                                        sheet.write(
                                            row, col+3+i, total, money_total)
                                    else:
                                        if x:
                                            key = 'balance_{}'.format(x)
                                            total = fr[key]*int(fr['sign'])
                                            if not total:
                                                total = ''  # sebagai string jika 0
                                            sheet.write(
                                                row, col+3+i, total, money_total)
                                    x -= 1
                            else:
                                total = fr['balance']
                                if not total:
                                    total = ''  # sebagai string jika 0
                                sheet.write(row, col + 3, total, money_total)

            if i_data == 'Profit and Loss':
                fr = rl_data[0]
                row += 1
                # tidak pakai code
                # sheet.write(row, col, fr.get('code', ''), text_style)
                if fr['level'] == 1:
                    sheet.write(row, col, 'NET PROFIT/LOSS',
                                side_heading_main)
                    sheet.write(row, col+2, '当期純利益/損失', side_heading_main)
                elif fr['level'] == 2:
                    sheet.write(row, col, 'NET PROFIT/LOSS',
                                side_heading_sub)
                    sheet.write(row, col+2, '当期純利益/損失',
                                side_heading_sub)
                else:
                    sheet.write(row, col, 'NET PROFIT/LOSS', txt_name)
                    sheet.write(row, col+2, '当期純利益/損失', txt_name)
                # sheet.write(row, col + 3, fr['balance'], txt)
                if filters.get('previous_periode', False):
                    x = filters['previous_periode']+1
                    for i in range(filters['previous_periode']+2):
                        if i_data == 'Profit and Loss':
                            if x:
                                key = 'balance_{}'.format(x)
                            else:
                                key = 'total_balance'
                            sheet.write(
                                row, col+3+i, fr[key]*int(fr['sign']), money_total)
                        else:
                            if x:
                                key = 'balance_{}'.format(x)
                                sheet.write(
                                    row, col+3+i, fr[key]*int(fr['sign']), money_total)
                        x -= 1
                else:
                    sheet.write(row, col + 3, fr['balance'], money_total)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
