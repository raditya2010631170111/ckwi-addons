# -*- coding: utf-8 -*-
import time
from odoo import fields, models, api, _

import io
import json
from odoo.exceptions import AccessError, UserError, AccessDenied
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class GeneralView(models.TransientModel):
    _inherit = 'account.general.ledger'

    # OVERRIDE
    def get_dynamic_xlsx_report(self, data, response ,report_data, dfr_data):
        report_data_main = json.loads(report_data)
        output = io.BytesIO()
        name_data = json.loads(dfr_data)
        filters = json.loads(data)
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        head = workbook.add_format({'align': 'center', 'bold': True,
                                    'font_size': '20px'})
        sub_heading = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '10px',
             'border': 1,
             'border_color': 'black'})
        txt = workbook.add_format({'font_size': '10px', 'border': 1})
        txt_l = workbook.add_format({'font_size': '10px', 'border': 1, 'bold': True})
        sheet.merge_range('A2:J3', filters.get('company_name') + ':' + name_data.get('name'), head)
        date_head = workbook.add_format({'align': 'center', 'bold': True,
                                         'font_size': '10px'})
        date_style = workbook.add_format({'align': 'center',
                                          'font_size': '10px'})
        money = workbook.add_format({
            'num_format': '_(Rp* #,##0_);[Red]_(Rp* (#,##0);_(Rp* "-"_);_(@_)',
            'align': 'right',
            'font_size': '10px', 'border': 1,
            })
        if filters.get('date_from'):
            sheet.merge_range('B4:C4', 'From: ' + filters.get('date_from'), date_head)
        if filters.get('date_to'):
            sheet.merge_range('H4:I4', 'To: ' + filters.get('date_to'), date_head)
        # sheet.merge_range('A5:J6', 'Journals: ' + ', '.join(
        #     [lt or '' for lt in filters['journals']]) + '  Target Moves: ' + filters.get('target_move'), date_head)

        sheet.merge_range('A5:J6', '  Journals: ' + ', '.join(
            [lt or '' for lt in
             filters['journals']]) + '  Accounts: ' + ', '.join(
            [lt or '' for lt in
             filters['accounts']]) + '  Account Tags: ' + ', '.join(
            [lt or '' for lt in
             filters['analytic_tags']]) + '  Analytic: ' + ', '.join(
            [at or '' for at in
             filters['analytics']]) + '  Target Moves : ' + filters.get('target_move'),
                          date_head)


        sheet.write('A8', 'Code', sub_heading)
        sheet.write('B8', 'Amount', sub_heading)
        sheet.write('C8', 'Date', sub_heading)
        sheet.write('D8', 'JRNL', sub_heading)
        sheet.write('E8', 'Partner', sub_heading)
        sheet.write('F8', 'Move', sub_heading)
        sheet.write('G8', 'Entry Label', sub_heading)
        sheet.write('H8', 'Debit', sub_heading)
        sheet.write('I8', 'Credit', sub_heading)
        sheet.write('J8', 'Balance', sub_heading)

        row = 6
        col = 0
        sheet.set_column(8, 0, 15)
        sheet.set_column('B:B', 40)
        sheet.set_column(8, 2, 15)
        sheet.set_column(8, 3, 15)
        sheet.set_column(8, 4, 15)
        sheet.set_column(8, 5, 15)
        sheet.set_column(8, 6, 50)
        sheet.set_column(8, 7, 26)
        sheet.set_column(8, 8, 15)
        sheet.set_column(8, 9, 15)

        for rec_data in report_data_main:

            row += 1
            sheet.write(row + 1, col, rec_data['code'], txt)
            sheet.write(row + 1, col + 1, rec_data['name'], txt)
            sheet.write(row + 1, col + 2, '', txt)
            sheet.write(row + 1, col + 3, '', txt)
            sheet.write(row + 1, col + 4, '', txt)
            sheet.write(row + 1, col + 5, '', txt)
            sheet.write(row + 1, col + 6, '', txt)

            sheet.write(row + 1, col + 7, rec_data['debit'], money)
            sheet.write(row + 1, col + 8, rec_data['credit'], money)
            sheet.write(row + 1, col + 9, rec_data['balance'], money)
            for line_data in rec_data['move_lines']:
                row += 1
                sheet.write(row + 1, col, '', txt)
                sheet.write(row + 1, col + 1, '', txt)
                sheet.write(row + 1, col + 2, line_data.get('ldate'), txt)
                sheet.write(row + 1, col + 3, line_data.get('lcode'), txt)
                sheet.write(row + 1, col + 4, line_data.get('partner_name') or line_data.get('parent_partner_name'), txt)
                if line_data.get('invoice_no_supplier'):
                    move_name = '%s - %s' % (line_data.get('invoice_no_supplier'), line_data.get('move_name'))
                elif line_data.get('source_picking_id_name'):
                    move_name = '%s - %s' % (line_data.get('source_picking_id_name'), line_data.get('move_name'))
                else:
                    move_name = line_data.get('move_name')
                sheet.write(row + 1, col + 5, move_name, txt)
                sheet.write(row + 1, col + 6, line_data.get('lname'), txt)
                sheet.write(row + 1, col + 7, line_data.get('debit'), money)
                sheet.write(row + 1, col + 8, line_data.get('credit'), money)
                sheet.write(row + 1, col + 9, line_data.get('balance'), money)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

    # OVERRIDE, menambahkan kolom source_picking_id_name & 
    def _get_accounts(self, accounts, init_balance, display_account, data):
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = {x: [] for x in accounts.ids}

        # Prepare initial sql query and Get the initial move lines
        if init_balance and data.get('date_from'):
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(
                date_from=self.env.context.get('date_from'), date_to=False,
                initial_bal=True)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id',
                                           'm').replace('account_move_line',
                                                        'l')
            new_filter = filters
            if data['target_move'] == 'posted':
                new_filter += " AND m.state = 'posted'"
            else:
                new_filter += " AND m.state in ('draft','posted')"
            if data.get('date_from'):
                new_filter += " AND l.date < '%s'" % data.get('date_from')
            if data['journals']:
                new_filter += ' AND j.id IN %s' % str(tuple(data['journals'].ids) + tuple([0]))
            if data.get('accounts'):
                WHERE = "WHERE l.account_id IN %s" % str(tuple(data.get('accounts').ids) + tuple([0]))
            else:
                WHERE = "WHERE l.account_id IN %s"
            if data.get('analytics'):
                WHERE += ' AND anl.id IN %s' % str(tuple(data.get('analytics').ids) + tuple([0]))
            if data.get('analytic_tags'):
                WHERE += ' AND anltag.account_analytic_tag_id IN %s' % str(
                    tuple(data.get('analytic_tags').ids) + tuple([0]))


            sql = ("""SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, 0.0 AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
                        '' AS move_name, '' AS mmove_id, '' AS currency_code,\
                        NULL AS currency_id,\
                        '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
                        '' AS partner_name
                        FROM account_move_line l\
                        LEFT JOIN account_move m ON (l.move_id=m.id)\
                        LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                        LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                        LEFT JOIN account_move i ON (m.id =i.id)\
                        LEFT JOIN account_account_tag_account_move_line_rel acc ON (acc.account_move_line_id=l.id)
                        LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                        LEFT JOIN account_analytic_tag_account_move_line_rel anltag ON (anltag.account_move_line_id=l.id)
                        JOIN account_journal j ON (l.journal_id=j.id)"""
                        + WHERE + new_filter + ' GROUP BY l.account_id ORDER BY move_name')
            if data.get('accounts'):
                params = tuple(init_where_params)
            else:
                params = (tuple(accounts.ids),) + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                row['m_id'] = row['account_id']
                move_lines[row.pop('account_id')].append(row)

        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        final_filters = " AND ".join(wheres)
        final_filters = final_filters.replace('account_move_line__move_id', 'm').replace(
            'account_move_line', 'l')
        new_final_filter = final_filters
        if data['target_move'] == 'posted':
            new_final_filter += " AND m.state = 'posted'"
        else:
            new_final_filter += " AND m.state in ('draft','posted')"
        if data.get('date_from'):
            new_final_filter += " AND l.date >= '%s'" % data.get('date_from')
        if data.get('date_to'):
            new_final_filter += " AND l.date <= '%s'" % data.get('date_to')

        if data['journals']:
            new_final_filter += ' AND j.id IN %s' % str(tuple(data['journals'].ids) + tuple([0]))
        if data.get('accounts'):
            WHERE = "WHERE l.account_id IN %s" % str(tuple(data.get('accounts').ids) + tuple([0]))
        else:
            WHERE = "WHERE l.account_id IN %s"
        if data.get('analytics'):
            WHERE += ' AND anl.id IN %s' % str(tuple(data.get('analytics').ids) + tuple([0]))

        if data.get('analytic_tags'):
            WHERE += ' AND anltag.account_analytic_tag_id IN %s' % str(
                tuple(data.get('analytic_tags').ids) + tuple([0]))

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT l.id AS lid,m.id AS move_id, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.balance),0) AS balance,\
                    m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name,\
                    pr.name AS parent_partner_name\
                    FROM account_move_line l\
                    JOIN account_move m ON (l.move_id=m.id)\
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                    LEFT JOIN res_partner pr ON (p.parent_id = pr.id)\
                    LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    LEFT JOIN account_account_tag_account_move_line_rel acc ON (acc.account_move_line_id=l.id)
                    LEFT JOIN account_analytic_tag_account_move_line_rel anltag ON (anltag.account_move_line_id=l.id)
                    JOIN account_journal j ON (l.journal_id=j.id)\
                    JOIN account_account a ON (l.account_id = a.id) '''
                    + WHERE + new_final_filter + ''' GROUP BY l.id, m.id,  l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, c.position, p.name, pr.name ORDER BY move_name''' )
        # import pdb;pdb.set_trace()
        if data.get('accounts'):
            params = tuple(where_params)
        else:
            params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += round(line['debit'],2) - round(line['credit'],2)
            row['balance'] += round(balance,2)
            row['m_id'] = row['account_id']
            move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['id'] = account.id
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += round(line['debit'],2)
                res['credit'] += round(line['credit'],2)
                res['balance'] = round(line['balance'],2)
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(
                    res['balance']):
                account_res.append(res)

        return account_res