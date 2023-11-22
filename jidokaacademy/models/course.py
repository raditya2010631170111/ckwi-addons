from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError

class Course(models.Model): #object relational mapping (orm)
    _name = 'jidokaacademy.course'
    _description = 'jidokaacademy.course'

    name = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    user_id = fields.Many2one('res.users', string='Responsible User')
    session_ids = fields.One2many('jidokaacademy.session', 'course_id', string='session')
    def copy (self, default = None):
        default = dict(default or {})

        copied_count = self.search_count(
             [('name', '=like', "Copy of {}%".format(self.name))])

        if not copied_count:
            new_name = "Copy of {}".format(self.name)

        else:
            new_name = "Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name
        return super(Course, self).copy(default)

    _sql_constraints = [
        ('check_name_description_different','CHECK (name != description)','Name and description must be different'),
        ('check_name_unique','UNIQUE(name)','Name must be unique')
    ]

class Session(models.Model):
    _name = 'jidokaacademy.session' 
    _inherit = 'mail.thread'
    _description = 'jidokaacademy.session'
    
    name = fields.Char(string='Title', required=True, track_visibility=True) #kolom #field tracking
    start_date = fields.Date(string='Start Date', default=fields.date.today(), track_visibility=True)
    duration = fields.Float(string='Duration', track_visibility=True)
    number_of_seats = fields.Float('Number Of Seats', track_visibility=True)
    description = fields.Text('Description', track_visibility=True)
    partner_id = fields.Many2one('res.partner', string='Instructor', domain="[('is_instructor','=',True)]", track_visibility=True)
    partner_ids = fields.Many2many('res.partner', string='Attendees', track_visibility=True)
    course_id = fields.Many2one('jidokaacademy.course', string='Course', required=True, track_visibility=True)
    taken_seats = fields.Float('Taken seats', compute ='_count_taken_seats', tracking=True, track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)
    number_of_attendees = fields.Float('Number of attendees', compute='_count_attendees', store=True, track_visibility=True)

    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                            ('done', 'Done'), ('cancel', 'Cancelled')], default='draft', string="Status")
    image = fields.Binary(string="Instructor Image")

    @api.depends('partner_ids')
    def _count_attendees(self):
        for rec in self:
            rec.number_of_attendees = len(rec.partner_ids)

    def _count_taken_seats(self):
        for rec in self:
            if rec.partner_ids and rec.number_of_seats:
                rec.taken_seats = len(rec.partner_ids) / rec.number_of_seats * 100
            else:
                rec.taken_seats = 0

    @api.onchange('number_of_seats', 'partner_ids')
    def _onchange_number_of_seats(self):
        if self.number_of_seats < 0:
            return {
                'warning': {
                        'title': 'Invalid value',
                        'message': 'The number of available seats may not be negative'
                }
            }
        if self.number_of_seats < len(self.partner_ids):
            return {
                'warning': {
                        'title': 'something bad happend',
                        'message': 'Participants cannot be more than the number of seats'
                }
            }
    
    @api.constrains('partner_ids','partner_ids')
    def _check_attendees(self):
        for record in self:
            if record.partner_id in record.partner_ids:
                raise ValidationError("Instructor annot be attendees: %s" % record.partner_id.name)

    # @api.multi = Odoo 13.0 makes it default
    def unlink(self):
        if self.filtered(lambda line: line.state != 'draft'):
            raise exceptions.UserError('Cannot erase data except Draft')
        return super(Session, self).unlink()
    
    def action_confirm(self):
        self.state = 'confirm'
    def action_done(self):
        self.state = 'done'
    def action_draft(self):
        self.state = 'draft'
    def action_cancel(self):
        self.state = 'cancel'

class InheritPartner(models.Model):
    _inherit = 'res.partner'

    is_instructor = fields.Boolean('Instructor', default=False)

class WizardAttendees(models.TransientModel):
	_name = 'wizard.attendees'
	
	session_id = fields.Many2one('jidokaacademy.session', string='Session')
	partner_ids = fields.Many2many('res.partner', string='Attendees')
	
	def process(self):
		self.session_id.partner_ids |= self.partner_ids