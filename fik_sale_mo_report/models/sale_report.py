from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import date


class SaleReport(models.Model):
    _inherit = 'sale.order'

