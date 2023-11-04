# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class JidokaWorklocation(models.Model):
    _inherit = 'jidoka.worklocation'


    submission_aproval_ids = fields.One2many('submission.approval','work_location_id', string='Approval Pengajuan Petty Cash')
    disbursement_aproval_ids = fields.One2many('disbursement.approval','work_location_id', string='Approval Pengeluaran Petty Cash')


class SubmissionApproval(models.Model):
    _name = "submission.approval"


    work_location_id = fields.Many2one('jidoka.worklocation', string='Work Location', ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', track_visibility='always')
    name = fields.Char(related='user_id.name', store=True)
    sequence = fields.Integer(string='Level', default=1, track_visibility='always')


    @api.constrains('user_id','sequence')
    def check_duplicate_data(self):
        for this in self:
            same_data_user = self.search_count([
                ('work_location_id','=', this.work_location_id.id),
                ('user_id', '=', this.user_id.id),
            ])

            if same_data_user > 1:
                raise ValidationError(_("User %s is already in use" %(this.user_id.name)))

            same_data_sequence = self.search_count([
                ('work_location_id','=', this.work_location_id.id),
                ('sequence', '=', this.sequence),
            ])

            if same_data_sequence > 1:
                raise ValidationError(_("Level %s is already in use" %(this.sequence)))

            if this.sequence < 1:
                raise ValidationError(_("Level cannot be 0 or (-)Minus"))


class DisbursementApproval(models.Model):
    _name = "disbursement.approval"


    work_location_id = fields.Many2one('jidoka.worklocation', string='Work Location', ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', track_visibility='always')
    name = fields.Char(related='user_id.name', store=True)
    sequence = fields.Integer(string='Level', default=1, track_visibility='always')


    @api.constrains('user_id','sequence')
    def check_duplicate_data(self):
        for this in self:
            same_data_user = self.search_count([
                ('work_location_id','=', this.work_location_id.id),
                ('user_id', '=', this.user_id.id),
            ])

            if same_data_user > 1:
                raise ValidationError(_("User %s is already in use" %(this.user_id.name)))

            same_data_sequence = self.search_count([
                ('work_location_id','=', this.work_location_id.id),
                ('sequence', '=', this.sequence),
            ])

            if same_data_sequence > 1:
                raise ValidationError(_("Level %s is already in use" %(this.sequence)))

            if this.sequence < 1:
                raise ValidationError(_("Level cannot be 0 or (-)Minus"))