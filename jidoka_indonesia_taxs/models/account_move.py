# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    faktur_number = fields.Char(string='Faktur No', related='l10n_id_tax_number')
    faktur_date = fields.Date(string='Faktur Date')
    uraian = fields.Text(string='Struktur/Uraian')
    document_number = fields.Char(string='Document Number')
    surat_jalan_number = fields.Char(string='Surat Jalan No')
    surat_jalan_date = fields.Date(string='Surat Jalan Date')
    
