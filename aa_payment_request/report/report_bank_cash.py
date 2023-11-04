from odoo import api, fields, models
from datetime import timedelta, datetime


class BankCashXlsx(models.AbstractModel):
    _name = 'report.aa_payment_request.report_bank_and_cash'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        sheet = workbook.add_worksheet('Report')
        text_top_style = workbook.add_format(
            {'font_size': 12, 'bold': True, 'font_color': 'black', 'valign': 'vcenter', 'text_wrap': True})
        text_header_style = workbook.add_format(
            {'font_size': 12, 'bold': True, 'font_color': 'black', 'valign': 'vcenter', 'text_wrap': True, 'align': 'center'})
        text_style = workbook.add_format(
            {'font_size': 12, 'valign': 'vcenter', 'text_wrap': True, 'align': 'center'})
        number_style = workbook.add_format(
            {'num_format': '#,##0', 'font_size': 12, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True})

        if obj.date_from and obj.date_to:
            date = "%s s/d %s" % (str(obj.date_from), str(obj.date_to))
        else:
            date = "All Date"

        if obj.company_id.id:
            company = obj.company_id.name
        else:
            company = '-'
        # sheet.merge_range(0, 0, 0, 1, "Entitas", text_top_style)
        # sheet.write(0, 2, company)
        # sheet.merge_range(1, 0, 1, 1, "Kas/Bank", text_top_style)
        # sheet.write(1, 2, obj.account_id.name)
        # sheet.merge_range(2, 0, 2, 1, "No. Rekening", text_top_style)
        # sheet.write(2, 2, '-')
        # sheet.merge_range(3, 0, 3, 1, "Valuta", text_top_style)
        # sheet.write(3, 2, 'Indonesia Rupiah (IDR)')
        # sheet.merge_range(4, 0, 4, 1, "Periode", text_top_style)
        # sheet.write(4, 2, date)

        sheet.merge_range(0, 0, 0, 1, "Entitas", text_top_style)
        sheet.write(0, 2, 'PT. Magma Sigma Utama')
        # sheet.merge_range(1, 0, 1, 1, "Account", text_top_style)
        # sheet.write(1, 2, '-')
        # sheet.merge_range(2, 0, 2, 1, "No. Rekening", text_top_style)
        # sheet.write(2, 2, '-')
        sheet.merge_range(2, 0, 2, 1, "Valuta", text_top_style)
        sheet.write(2, 2, 'Indonesia Rupiah (IDR)')
        sheet.merge_range(3, 0, 3, 1, "Periode", text_top_style)
        sheet.write(3, 2, date)

        row = 6
        sheet.freeze_panes(7, 10)
        sheet.set_column(0, 0, 6)
        sheet.set_column(1, 9, 15)

        header = ['No', 'Tanggal', 'No. Cek/BG', 'No. Voucher', 'No. BPH/Invoice',
                  'Dari/ Kepada', 'Uraian', 'Debit', 'Credit', 'Saldo']
        sheet.write_row(row, 0, header, text_header_style)

        no_list = []
        tanggal = []
        no_cek_bg = []
        no_voucher = []
        no_bph = []
        dari_kepada = []
        uraian = []
        debit = []
        debit_awal = []
        credit = []
        saldo = []
        no = 1
        i = 0
        saldo_int = 0
        value = 0
        array = []
        acc_name = ""
        for zz, x in enumerate(obj.account_ids):
            array.append(x.id)
            if zz != len(obj.account_ids)-1:
                acc_name += x.name + ', '
            else:
                acc_name += x.name
        sheet.merge_range(1, 0, 1, 1, "Account", text_top_style)
        sheet.write(1, 2, acc_name)
        if obj.date_from and obj.date_to and obj.account_ids[0]:
            pettycash = self.env['account.move.line'].search([('account_id', 'in',
                                                             array),
                                                              ('date', '>=',
                                                             obj.date_from),
                                                              ('date', '<=',
                                                             obj.date_to),
                                                              ], order='debit desc, date asc')
            for iteration, x in enumerate(pettycash):
                no_list.append(no)
                dt = x.date
                date_report = dt.strftime("%d.%m.%Y")
                tanggal.append(date_report)
                if x.move_id.name == False:
                    move_name = ''
                else:
                    move_name = x.move_id.name
                if x.partner_id.name == False:
                    partner_name = ''
                else:
                    partner_name = x.partner_id.name
                no_bph.append(move_name)
                dari_kepada.append(partner_name)
                no_cek_bg.append('-')
                no_voucher.append('-')
                debit.append(x.debit)
                credit.append(x.credit*(-1))
                if iteration == 0 and x.debit != 0:
                    saldo_int += int(x.debit)
                    value += saldo_int
                    uraian.append('Saldo Awal')
                elif x.debit != 0 and x.credit == 0:
                    saldo_int += int(x.debit)
                    value += saldo_int
                    uraian.append(x.name)
                elif x.debit == 0 and x.credit != 0:
                    saldo_int += (x.credit*(-1))
                    value += saldo_int
                    uraian.append(x.name)
                else:
                    saldo_int += ((x.debit) + (x.credit*(-1)))
                    value += saldo_int
                    uraian.append(x.name)
                saldo.append(saldo_int)
                no += 1
                i += 1
            # debit_cash = self.env['account.move.line'].search([('account_id', 'in',
            #                                                     array),
            #                                                   ('date', '>=',
            #                                                    obj.date_from),
            #                                                   ('date', '<=',
            #                                                    obj.date_to), ('debit', '!=', 0), ('credit', '=', 0)
            #                                                    ], order='date asc')
            # credit_cash = self.env['account.move.line'].search([('account_id', 'in',
            #                                                      array),
            #                                                     ('date', '>=',
            #                                                    obj.date_from),
            #                                                     ('date', '<=',
            #                                                      obj.date_to), ('debit', '=', 0), ('credit', '!=', 0)
            #                                                     ], order='date asc')

            # for iteration, x in enumerate(debit_cash):
            #     no_list.append(no)
            #     dt = x.date
            #     date_report = dt.strftime("%d.%m.%Y")
            #     tanggal.append(date_report)
            #     if x.move_id.name == False:
            #         move_name = ''
            #     else:
            #         move_name = x.move_id.name
            #     if x.partner_id.name == False:
            #         partner_name = ''
            #     else:
            #         partner_name = x.move_id.name
            #     no_bph.append(move_name)
            #     dari_kepada.append(partner_name)
            #     no_cek_bg.append('-')
            #     no_voucher.append('-')
            #     debit.append(x.debit)
            #     credit.append(x.credit)
            #     if iteration == 0 and x.debit != 0:
            #         saldo_int += int(x.debit)
            #         value += saldo_int
            #         uraian.append('Saldo Awal')
            #     elif x.debit != 0:
            #         saldo_int += int(x.debit)
            #         value += saldo_int
            #         uraian.append(x.name)
            #     saldo.append(saldo_int)
            #     no += 1
            #     i += 1
            # for iteration, x in enumerate(credit_cash):
            #     no_list.append(no)
            #     dt = x.date
            #     date_report = dt.strftime("%d.%m.%Y")
            #     tanggal.append(date_report)
            #     if x.move_id.name == False:
            #         move_name = ''
            #     else:
            #         move_name = x.move_id.name
            #     if x.partner_id.name == False:
            #         partner_name = ''
            #     else:
            #         partner_name = x.move_id.name
            #     no_bph.append(move_name)
            #     dari_kepada.append(partner_name)
            #     no_cek_bg.append('-')
            #     no_voucher.append('-')
            #     debit.append(x.debit)
            #     credit.append(x.credit)
            #     if x.debit == 0 and x.credit != 0:
            #         saldo_int += (x.credit*(-1))
            #         value += saldo_int
            #         uraian.append(x.name)
            #     saldo.append(saldo_int)
            #     no += 1
            #     i += 1
        else:
            pettycash = self.env['account.move.line'].search([('account_id', 'in',
                                                             array)
                                                              ], order='debit desc, date asc')
            for iteration, x in enumerate(pettycash):
                no_list.append(no)
                dt = x.date
                date_report = dt.strftime("%d.%m.%Y")
                tanggal.append(date_report)
                if x.move_id.name == False:
                    move_name = ''
                else:
                    move_name = x.move_id.name
                if x.partner_id.name == False:
                    partner_name = ''
                else:
                    partner_name = x.partner_id.name
                no_bph.append(move_name)
                dari_kepada.append(partner_name)
                no_cek_bg.append('-')
                no_voucher.append('-')
                debit.append(x.debit)
                credit.append(x.credit*(-1))
                if iteration == 0 and x.debit != 0:
                    saldo_int += int(x.debit)
                    value += saldo_int
                    uraian.append('Saldo Awal')
                elif x.debit != 0 and x.credit == 0:
                    saldo_int += int(x.debit)
                    value += saldo_int
                    uraian.append(x.name)
                elif x.debit == 0 and x.credit != 0:
                    saldo_int += (x.credit*(-1))
                    value += saldo_int
                    uraian.append(x.name)
                else:
                    saldo_int += ((x.debit) + (x.credit*(-1)))
                    value += saldo_int
                    uraian.append(x.name)
                saldo.append(saldo_int)
                no += 1
                i += 1
            # debit_cash = self.env['account.move.line'].search([('account_id', 'in',
            #                                                     array), ('debit', '!=', 0), ('credit', '=', 0)
            #                                                    ], order='date asc')
            # credit_cash = self.env['account.move.line'].search([('account_id', 'in',
            #                                                      array), ('debit', '=', 0), ('credit', '!=', 0)
            #                                                     ], order='date asc')
            # for iteration, x in enumerate(debit_cash):
            #     no_list.append(no)
            #     dt = x.date
            #     date_report = dt.strftime("%d.%m.%Y")
            #     tanggal.append(date_report)
            #     if x.move_id.name == False:
            #         move_name = ''
            #     else:
            #         move_name = x.move_id.name
            #     if x.partner_id.name == False:
            #         partner_name = ''
            #     else:
            #         partner_name = x.move_id.name
            #     no_bph.append(move_name)
            #     dari_kepada.append(partner_name)
            #     no_cek_bg.append('-')
            #     no_voucher.append('-')
            #     debit.append(x.debit)
            #     credit.append(x.credit)
            #     if iteration == 0 and x.debit != 0:
            #         saldo_int += int(x.debit)
            #         value += saldo_int
            #         uraian.append('Saldo Awal')
            #     elif x.debit != 0:
            #         saldo_int += int(x.debit)
            #         value += saldo_int
            #         uraian.append(x.name)
            #     saldo.append(saldo_int)
            #     no += 1
            #     i += 1
            # for iteration, x in enumerate(credit_cash):
            #     no_list.append(no)
            #     dt = x.date
            #     date_report = dt.strftime("%d.%m.%Y")
            #     tanggal.append(date_report)
            #     if x.move_id.name == False:
            #         move_name = ''
            #     else:
            #         move_name = x.move_id.name
            #     if x.partner_id.name == False:
            #         partner_name = ''
            #     else:
            #         partner_name = x.move_id.name
            #     no_bph.append(move_name)
            #     dari_kepada.append(partner_name)
            #     no_cek_bg.append('-')
            #     no_voucher.append('-')
            #     debit.append(x.debit)
            #     credit.append(x.credit)
            #     if x.debit == 0 and x.credit != 0:
            #         saldo_int += (x.credit*(-1))
            #         value += saldo_int
            #         uraian.append(x.name)
            #     saldo.append(saldo_int)
            #     no += 1
            #     i += 1

        row += 1
        sheet.write_column(row, 0, no_list, text_style)
        sheet.write_column(row, 1, tanggal, text_style)
        sheet.write_column(row, 2, no_cek_bg, text_style)
        sheet.write_column(row, 3, no_voucher, text_style)
        sheet.write_column(row, 4, no_bph, text_style)
        sheet.write_column(row, 5, dari_kepada, text_style)
        sheet.write_column(row, 6, uraian, text_style)
        sheet.write_column(row, 7, debit, number_style)
        sheet.write_column(row, 8, credit, number_style)
        sheet.write_column(row, 9, saldo, number_style)
