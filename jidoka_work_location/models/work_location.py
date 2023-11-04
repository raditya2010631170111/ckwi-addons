from odoo import _, api, fields, models
import pytz


class JidokaWorkLocation(models.Model):
    _name = 'jidoka.worklocation'
    _description = 'Lokasi Kerja'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')
    latitude = fields.Char('Latitude', required=True,)
    longitude = fields.Char('Logitude', required=True,)
    max_distance = fields.Float('Max Distance (m)', default=0)
    location_address = fields.Char('Location Address', required=True,)
    is_req_geolocation = fields.Boolean('Require Geolocation')
    is_req_image = fields.Boolean('Require Image')
    date_tz = fields.Selection(string='Timezone', required=True, default=lambda self: self.env.user.tz or 'Asia/Jakarta',
                               selection=[('Asia/Jakarta', 'Asia/Jakarta'), ('Asia/Makassar', 'Asia/Makassar'), ('Asia/Jayapura', 'Asia/Jayapura')])
    is_ho = fields.Boolean(string='Head Office', default=False)
    area = fields.Many2one('jidoka.area', string="Area")

    employee_ids = fields.One2many(
        string='Employee',
        comodel_name='hr.employee',
        inverse_name='work_location_id',
    )

    @api.model
    def _tz_get(self):
        return [('Asia/Jakarta', 'Asia/Jakarta'), ('Asia/Makassar', 'Asia/Makassar'), ('Asia/Jayapura', 'Asia/Jayapura')]
