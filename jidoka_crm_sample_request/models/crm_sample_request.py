# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
from odoo.exceptions import ValidationError, UserError
import base64
_logger = logging.getLogger(__name__)

class CrmSampleRequest(models.Model):
    _name = 'crm.sample.request'
    _description = 'Sample Request from CRM'
    _inherit = ['mail.thread']
    _order = "id desc"

    #signature data
    name_rnd_manager = fields.Char(string='R&D Manager')
    name_marketing_department = fields.Char(string='Marketing Department')
    name_rnd_department = fields.Char('R&D Department')
    name_marketing_manager = fields.Char('Marketing Manager')
    ttd_rnd_manager = fields.Binary('Signature R&D Manager')
    ttd_marketing_department = fields.Binary('Signature Marketing Department')
    ttd_rnd_department = fields.Binary('Signature R&D Department')
    ttd_marketing_manager = fields.Binary('Signature Marketing Manager')

    name = fields.Char(string='Sample Request No', readonly=True, copy=False, required=True, 
        default=lambda self: self._generate_request_no(), tracking=True)

    @api.model
    def _generate_request_no(self):
        last_request = self.search([], order='id desc', limit=1)
        if last_request:
            last_no = last_request.name.split('.')[-1]
            year = fields.Date.today().year
            month = fields.Date.today().month
            new_no = int(last_no) + 1
            return f"C{year}.{str(month).zfill(2)}.{str(new_no).zfill(2)}"
        else:
            year = fields.Date.today().year
            month = fields.Date.today().month
            requests = self.search([], order='id asc')
            if requests:
                return requests[0].name
            else:
                return f"C{year}.{str(month).zfill(2)}.01"

        
    # name = fields.Char(string='Sample Request No', readonly=True, copy=False, required=True, 
    #     default=lambda self: _("New"), tracking=True)
    buyer_request_no = fields.Char(string='Buyer Request No', tracking=True)
 
    lead_id = fields.Many2one(comodel_name='crm.lead', string='Spec Design')
    # lead_id = fields.Many2one(comodel_name='crm.lead', string='Spec Design',
    #                       domain=[('stage_id.name', '=', 'Assigned')])
    request_no = fields.Char("No. Spec Design", copy=False)
    # partner_id = fields.Many2one(comodel_name='res.partner', string='Customer', required=True,
    #     tracking=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer', required=True,
        tracking=True)
    
    partner_team = fields.Many2one('res.partner', string='Teams')
    
    is_rev = fields.Boolean()

    purpose = fields.Char(string='Purpose', required=True, tracking=True)
    date_issued = fields.Datetime(string='Date Issued', copy=False, required=True, 
        default=fields.Datetime.now, tracking=True)
    date_deadline = fields.Date(string='Date Deadline', required=True, tracking=True)
    # material_ids = fields.Many2many(comodel_name='design.material', string='Material',
    #     tracking=True)
    # detail_finish_ids = fields.Many2many(comodel_name='design.finish',string='Finish', tracking=True)
    material_ids = fields.Many2many(comodel_name='design.material', string='Material')
    detail_finish_ids = fields.Many2many(comodel_name='design.finish',string='Finish')
    is_show = fields.Boolean("Is Show", default=False)

    state = fields.Selection(
        [('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('rev', 'Revised'),],
        'Status', required=True, copy=False, default='draft', tracking=True)
    line_ids = fields.One2many(comodel_name='crm.sample.request.line', inverse_name='sample_request_id', 
        string='Sample Request Details')

    line_detail_ids = fields.One2many(comodel_name='crm.sample.request.line1', inverse_name='sample_request_id', 
        string='Sample Request Details')

    note = fields.Text(string='Note')
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, tracking=True, 
        default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', index=True, 
        default=lambda self: self.env.company.id)
    department_id = fields.Many2one('hr.department', string='Department', 
        default=lambda self: self.env.user.employee_ids.department_id)
    # untuk notif
    user_rnd_id = fields.Many2one("res.partner", string='Team RnD', 
        tracking=True)
    user_team_id = fields.Many2one("res.users", string='Person')
    rnd_team_id = fields.Many2one("team.rnd","Teams")
    department_rnd_id = fields.Many2one('hr.department', string='Department')
    user_production_id = fields.Many2one("res.partner", string='Team Production',
        tracking=True)
    mo_ids = fields.One2many(comodel_name='mrp.production', inverse_name='sample_request_id',
        string='Data MO')
    rnd_ids = fields.One2many(comodel_name='design.process', inverse_name='sample_request_id',
        string='Data RND')
    count_mo = fields.Integer(string='Count MO', compute='_compute_count_mo', store=True)
    count_rnd = fields.Integer(string='Count RND', compute='_compute_count_rnd', store=True)
    pricelist_id = fields.Many2one('product.pricelist', "Currency")
    sale_count = fields.Integer("Sale", compute="_sale_count")
    internal_notes = fields.Text(string="Internal Notes")

    # def create_rev(self, default=None):
    #     old_request_no = self.request_no or 'New'

    #     if old_request_no.endswith('.Rev'):
    #         if old_request_no.split('.Rev-')[-1].isdigit():
    #             rev_number = int(old_request_no.split('.Rev-')[-1])
    #             new_rev_number = rev_number + 1
    #             new_request_no = f"{old_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"
    #         else:
    #             new_request_no = f"{old_request_no}.Rev-01"
    #     else:
    #         new_request_no = f"{old_request_no}.Rev-01"

    #     rev_numbers = [
    #         int(x.split('.Rev-')[-1]) 
    #         for x in self.search([('request_no', 'like', f'{old_request_no.rsplit(".Rev-", 1)[0]}%.Rev-')]).mapped('request_no')
    #     ]
        
    #     if rev_numbers:
    #         new_rev_number = max(rev_numbers) + 1
    #         new_request_no = f"{old_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"

    #     while self.env['crm.sample.request'].search_count([('request_no', '=', new_request_no)]) > 0:
    #         rev_number = int(new_request_no.split('.Rev-')[-1])
    #         new_rev_number = rev_number + 1
    #         new_request_no = f"{new_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"

    #     self.write({
    #         'request_no': new_request_no,
    #         'lead_id': self.lead_id.id,
    #         'partner_id': self.partner_id.id,
    #         'partner_team': self.partner_team.id,
    #         'purpose': self.purpose,
    #         'date_issued': self.date_issued,
    #         'date_deadline': self.date_deadline,
    #         'material_ids': [(6, 0, self.material_ids.ids)],
    #         'detail_finish_ids': [(6, 0, self.detail_finish_ids.ids)],
    #         'state': self.state,
    #         'note': self.note,
    #         'user_id': self.user_id.id,
    #         'company_id': self.company_id.id,
    #         'department_id': self.department_id.id,
    #         'user_rnd_id': self.user_rnd_id.id,
    #         'user_team_id': self.user_team_id.id,
    #         'rnd_team_id': self.rnd_team_id.id,
    #         'department_rnd_id': self.department_rnd_id.id,
    #         'user_production_id': self.user_production_id.id,
    #         'count_mo': self.count_mo,
    #         'count_rnd': self.count_rnd,
    #         'pricelist_id': self.pricelist_id.id,
    #         'sale_count': self.sale_count,
    #         'internal_notes': self.internal_notes,
    #     })

    #     line_spec = []
    #     for line_ids in self.line_ids:
    #         line_spec.append((0, 0, {
    #             'product_id': line_ids.product_id.id,
    #             'qty': line_ids.qty,
    #             'uom_id': line_ids.uom_id.id,
    #             'remark': line_ids.remark,
    #             'description': line_ids.description,
    #             'attachment': line_ids.attachment,
    #         }))

    #     self.write({'line_ids': line_spec})

    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'crm.sample.request',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_id': self.id,
    #         'target': 'current',
    #     }
    def v_rnd_sample(self):
        self.ensure_one()
        picking = self.env['sample.request'].search([('no_sample', '=', self.name)], limit=1)
        if not picking:
            raise UserError("Transfer not found")
        return {
            'type': 'ir.actions.act_window',
            'name': _('Transfer'),
            'res_model': 'sample.request',
            'view_mode': 'form',
            'res_id': picking.id,
            'target': 'current',
        }

    def coba(self):
        to_rnd = self.env['sample.request'].create({
            'request_no' : self.request_no,
            'no_sample' : self.name,
            'crm_id': self.lead_id.id,
            'partner_id': self.partner_id.id,
            'pricelist_id': self.pricelist_id.id,
            'schedule_date': self.date_issued,
            'deadline': self.date_deadline,
            'user_id': self.user_id.id,
            'department_id':self.department_id.id,
            'user_team_id':self.user_team_id.id,
            'partner_team' : self.partner_team.id,
            'department_rnd_id' : self.department_rnd_id.id,
            'detail_material_ids': [(6, 0, self.material_ids.ids)],
            'detail_finish_ids': [(6, 0, self.detail_finish_ids.ids)],
        })

        rnd_s_lines = []
        for line in self.line_ids:
            rnd_s_lines.append((0, 0, {
                'item_id': line.product_id.id,
                'quantity': line.qty,
                'uom_id': line.uom_id.id,
                'remark': line.remark,
                'description': line.description,
                'attachment': line.attachment,
                'attachment2': line.attachment2,
                'attachment3': line.attachment3,
            }))
        to_rnd.write({'sample_ids': rnd_s_lines})
        return to_rnd

    def create_rev(self, default=None):
        self.write({
            'state': 'rev'
        })
        
        old_request_no = self.name or 'New'

        if old_request_no.endswith('.Rev'):
            if old_request_no.split('.Rev-')[-1].isdigit():
                rev_number = int(old_request_no.split('.Rev-')[-1])
                new_rev_number = rev_number + 1
                new_request_no = f"{old_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"
            else:
                new_request_no = f"{old_request_no}.Rev-01"
        else:
            new_request_no = f"{old_request_no}.Rev-01"

        rev_numbers = [
            int(x.split('.Rev-')[-1]) 
            for x in self.search([('name', 'like', f'{old_request_no.rsplit(".Rev-", 1)[0]}%.Rev-')]).mapped('name')
        ]
        
        if rev_numbers:
            new_rev_number = max(rev_numbers) + 1
            new_request_no = f"{old_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"

        while self.env['crm.sample.request'].search_count([('name', '=', new_request_no)]) > 0:
            rev_number = int(new_request_no.split('.Rev-')[-1])
            new_rev_number = rev_number + 1
            new_request_no = f"{new_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"

        vals = {
            'name': new_request_no,
            'request_no': self.request_no,
            'lead_id': self.lead_id.id,
            'partner_id': self.partner_id.id,
            'partner_team': self.partner_team.id,
            'purpose': self.purpose,
            'date_issued': self.date_issued,
            'date_deadline': self.date_deadline,
            'material_ids': [(6, 0, self.material_ids.ids)],
            'detail_finish_ids': [(6, 0, self.detail_finish_ids.ids)],
            'state': 'draft',
            'note': self.note,
            'user_id': self.user_id.id,
            'company_id': self.company_id.id,
            'department_id': self.department_id.id,
            'user_rnd_id': self.user_rnd_id.id,
            'user_team_id': self.user_team_id.id,
            'rnd_team_id': self.rnd_team_id.id,
            'department_rnd_id': self.department_rnd_id.id,
            'user_production_id': self.user_production_id.id,
            'count_mo': self.count_mo,
            'count_rnd': self.count_rnd,
            'pricelist_id': self.pricelist_id.id,
            'sale_count': self.sale_count,
            'internal_notes': self.internal_notes,
            'name_rnd_manager': self.name_rnd_manager,
            'name_marketing_department': self.name_marketing_department,
            'name_rnd_department': self.name_rnd_department,
            'name_marketing_manager': self.name_marketing_manager,
            'ttd_rnd_manager': self.ttd_rnd_manager,
            'ttd_marketing_department': self.ttd_marketing_department,
            'ttd_rnd_department': self.ttd_rnd_department,
            'ttd_marketing_manager': self.ttd_marketing_manager,

        }

        new_record = self.env['crm.sample.request'].create(vals)

        line_spec = []
        for line_ids in self.line_ids:
            line_spec.append((0, 0, {
                'product_id': line_ids.product_id.id,
                'qty': line_ids.qty,
                'uom_id': line_ids.uom_id.id,
                'remark': line_ids.remark,
                'description': line_ids.description,
                'attachment': line_ids.attachment,
                'attachment2': line_ids.attachment2,
                'attachment3': line_ids.attachment3,
            }))

        new_record.write({'line_ids': line_spec})
        self.is_rev = True
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.sample.request',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': new_record.id,
            'target': 'current',
        }


    # @api.onchange('lead_id')
    # def _onchange_lead_id(self):
    #     # if self.lead_id and self.lead_id.stage_id.name == 'Done':
    #     if self.lead_id :
    #         self.partner_id = self.lead_id.partner_id
    #         self.pricelist_id = self.lead_id.pricelist_id
    #         self.date_deadline = self.lead_id.date_deadline
    #         self.user_id = self.lead_id.user_id
    #         self.department_id = self.lead_id.department_id
    #         self.material_ids = self.lead_id.detail_material_ids
    #         # self.detail_finish_ids = self.lead_id.detail_finish_ids
    #         self.user_rnd_id = self.lead_id.user_rnd_id
    #         self.user_team_id = self.lead_id.user_team_id
    #         self.rnd_team_id = self.lead_id.rnd_team_id
    #         self.department_rnd_id = self.lead_id.department_rnd_id
    #         self.request_no = self.lead_id.request_no
    #         self.detail_finish_ids = self.lead_id.detail_finish_ids
            

    # @api.onchange('lead_id')
    # def update_line_ids(self):
    #     self.line_ids = False
    #     if self.lead_id:
    #         line_vals = []
    #         for line in self.lead_id.spec_design_ids:
    #             line_vals.append((0, 0, {
    #                 'product_id': line.item_id.id,
    #                 'qty': line.quantity,
    #                 'uom_id': line.uom_id.id,
    #                 'attachment':line.attachment,
    #                 'description':line.description,
    #                 # 'process_state':line.process_state,
    #             }))
    #         self.line_ids = line_vals
    


    # @api.onchange('line_ids')
    # def _onchange_line_ids(self):
    #     for line in self.line_ids:
    #         if line.sample_request_id.lead_id and line.sample_request_id.lead_id.stage_id.name == 'Done':
    #             line.product_id = line.sample_request_id.lead_id.item_id
   
   
   
    def _sale_count(self):
        sale = self.env['sale.order'].search_count([('sample_request_id','=', self.id)])
        self.sale_count = sale

    def action_qoutations(self):
        vals = {
            'partner_id': self.partner_id.id,
            # 'state' : 'draft',
            'origin': self.purpose,
            'department_id': self.department_id.id,
            'pricelist_id' : self.pricelist_id.id,
            'sample_request_id': self.id,

        }

        sale = self.env['sale.order'].create(vals)
        sale._prepare_product_so()





    # @api.onchange("user_team_id")
    # def get_teams_rnd(self):
    #     user = self.user_team_id
    #     if user:
    #         self.user_rnd_id = user.partner_id.id
            # self.department_rnd_id = user.department_id.id
            # self.rnd_team_id = user.team_rnd_id.id

    # --- compute ---
    @api.depends('mo_ids')
    def _compute_count_mo(self):
        for rec in self:
            rec.count_mo = len(rec.mo_ids)
    
    @api.depends('rnd_ids')
    def _compute_count_rnd(self):
        for rec in self:
            rec.count_rnd = len(rec.rnd_ids)
    

    # --- on change ---
    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id
        else:
            self.uom_id = False

    # --- actions ---
    def action_submit(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError(_('Required Sample Request Detail!'))
        
        self.write({
            'state': 'submitted'
        })

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&model=%s&view_type=form' % (self.id, self._name)

        group_mgr = self.env['ir.config_parameter'].get_param('crm.group_approve_manager_marketing')
        users = self.env.ref(group_mgr).users

        # send email when user validate / send email to approver
        mail_param = self.env['ir.config_parameter'].get_param('crm_sample.validate_sample_request_template')
        mail_temp = self.env.ref(mail_param)
        email_template = mail_temp
        for user in users:
            partner_id = user.partner_id.id
            email = user.login
            email_template.email_to = email
            email_values = {'url': base_url, 'name': user.name}
            email_template.sudo().with_context(email_values).send_mail(self.id, force_send=True)

            # send notif to approver
            url = ('<br></br><a href="%s">%s</a>') % (base_url, self.name)
            name = ('Halo, %s.') % (user.name)
            body = name + ' Ada Sample Request yang harus di approve ' + url
            self.send_notif(partner_id, body, 'manager')

    def action_approve(self):
        self.is_show= True
        #entar diaktifkan apabila sudah ada model sample request rnd yang baru
        to_rnd = self.env['sample.request'].create({
            'request_no' : self.request_no,
            'no_sample' : self.name,
            'crm_id': self.lead_id.id,
            'partner_id': self.partner_id.id,
            'pricelist_id': self.pricelist_id.id,
            'schedule_date': self.date_issued,
            'deadline': self.date_deadline,
            'user_id': self.user_id.id,
            'department_id':self.department_id.id,
            'user_team_id':self.user_team_id.id,
            'partner_team' : self.partner_team.id,
            'department_rnd_id' : self.department_rnd_id.id,
            'detail_material_ids': [(6, 0, self.material_ids.ids)],
            'detail_finish_ids': [(6, 0, self.detail_finish_ids.ids)],
        })

        rnd_s_lines = []
        for line in self.line_ids:
            rnd_s_lines.append((0, 0, {
                'item_id': line.product_id.id,
                'quantity': line.qty,
                'uom_id': line.uom_id.id,
                'remark': line.remark,
                'description': line.description,
                'attachment': line.attachment,
                'attachment2': line.attachment2,
                'attachment3': line.attachment3,
            }))
        to_rnd.write({'sample_ids': rnd_s_lines})
        return {
            'name': _("Approve With Comment"),
            'view_type': 'form',
            'res_model': 'approval.history.sample.wizard',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_reject(self):
        return {
            'name': _("Reject With Reason"),
            'view_type': 'form',
            'res_model': 'approval.history.sample.wizard.reject',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def send_notif(self, partner_id, body, type):
        bot = self.env['res.partner'].search([('name', '=', 'Marketing Bot')]).id

        if type == 'user':
            channel = self.env['mail.channel'].channel_get([partner_id])
            channel_id = self.env['mail.channel'].browse(channel["id"])
            channel_id.message_post(
                body=(body),
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
            )

        if type == 'manager':
            channel_odoo_bot_users = 'Marketing Approval'
            channel_obj = self.env['mail.channel']
            channel_id = channel_obj.search([('name', 'like', channel_odoo_bot_users)])
            if not channel_id:
                channel_id = channel_obj.create({
                    'name': channel_odoo_bot_users,
                    'email_send': False,
                    'channel_type': 'channel',
                    'public': 'public',
                    'channel_partner_ids': [(4, partner_id), (4, bot)]
                })
            channel_id.message_post(
                body=body,
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
            )

    def action_setdraft(self):
        if self:
            return self.write({'state': 'draft'})

    def _create_design_process(self):
        self.ensure_one()
        vals = {
            'partner_id': self.partner_id.id,
            'deadline': self.date_deadline,
            'schedule_date': self.date_deadline,
            'schedule_design': self.date_deadline,
            'schedule_image': self.date_deadline,
            'user_id': self.user_id.id,
            'department_id': self.department_id.id,
            'department_rnd_id': self.department_rnd_id.id,
            'user_rnd_id': self.user_rnd_id.id,
            'user_team_id': self.user_team_id.id,
            'rnd_team_id': self.rnd_team_id.id,
            'sample_request_id': self.id,
            'detail_material_ids': self.material_ids,
            'detail_finish_ids': self.detail_finish_ids,
            'request_no': self.request_no,
            'crm_id': self.lead_id.id,
            'type_rnd': 'is_sample',
            'name_rnd_manager': self.name_rnd_manager,
            'name_marketing_department': self.name_marketing_department,
            'name_rnd_department': self.name_rnd_department,
            'name_marketing_manager': self.name_marketing_manager,
            'ttd_rnd_manager': self.ttd_rnd_manager,
            'ttd_marketing_department': self.ttd_marketing_department,
            'ttd_rnd_department': self.ttd_rnd_department,
            'ttd_marketing_manager': self.ttd_marketing_manager,
            
        }
        dp = self.env['design.process'].create(vals)
        dp.sample_request_line()
        # update state & nomor
        stage_sample = self.env["design.process.stage"].search([('code','=','sample')])
        dp.stage_id = stage_sample.id
        dp.name = self.env['ir.sequence'].next_by_code(
                   'rnd.request') or 'New RND'
        # notif if any
        user_id = self.env.user.id
        user = self.env.user.name
        message = ("Sample Request %s from %s has been assigned") % (self.name, user)
        if self.user_rnd_id:
            notification_ids = [((0, 0, {
                        'res_partner_id': self.user_rnd_id.id,
                        'notification_type': 'inbox'
                        }))]
            self.with_user(user_id).message_post(author_id=user_id,
                                body=(message),
                                message_type='notification',
                                subtype_xmlid="mail.mt_comment",
                                notification_ids=notification_ids,
                                partner_ids=[self.user_rnd_id.id],
                                notify_by_email=False,
                            )
        if self.user_production_id:
            notification_ids = [((0, 0, {
                        'res_partner_id': self.user_production_id.id,
                        'notification_type': 'inbox'
                        }))]
            self.with_user(user_id).message_post(author_id=user_id,
                                body=(message),
                                message_type='notification',
                                subtype_xmlid="mail.mt_comment",
                                notification_ids=notification_ids,
                                partner_ids=[self.user_rnd_id.id],
                                notify_by_email=False,
                            )

    def _create_mo(self):
        self.ensure_one()
        if self.state != 'approved':
            raise ValidationError(_('Only available if Approved!'))
        if not self.line_ids:
            raise ValidationError(_('Required Sample Request Detail!'))
        rnd = self.env['design.process'].search([('sample_request_id', '=', self.id)])
        for line in self.line_ids:
            vals = {
                'product_id': line.product_id.id,
                'product_qty': line.qty,
                'product_uom_id': line.product_id.uom_id.id,
                'origin': self.name,
                'sample_request_id': self.id,
                'request_no': self.request_no,
                'rnd_id': rnd and rnd.id or False,
                'is_sample_request': True,
            }
            mrp = self.env['mrp.production'].create(vals)
            mrp.onchange_company_id()
            mrp.onchange_product_id()
            mrp._onchange_product_qty()
            mrp._onchange_bom_id()
            mrp._onchange_date_planned_start()
            mrp._onchange_move_raw()
            mrp._onchange_move_finished_product()
            mrp._onchange_move_finished()
            mrp._onchange_location()
            mrp._onchange_location_dest()
            mrp.onchange_picking_type()
            mrp._onchange_producing()
            mrp._onchange_lot_producing()
            mrp._onchange_workorder_ids()
            if not mrp.bom_id:
                # raise ValidationError(_('Please Check BoM on product %s!' %(mrp.bom_id.name)))
                raise ValidationError(_('Please Check BoM on product %s!' %(mrp.product_id.name)))

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'MO Has Been Created',
                'type': 'rainbow_man',
            }
        }
    
    # --- inherit orm ---
    @api.model
    def create(self, vals):
        if vals.get('name',  _("New")) ==  _("New"):
            seq = self.env['ir.sequence'].next_by_code('crm.sample.request') or '/'
            vals['name'] = seq
        return super(CrmSampleRequest, self).create(vals)
    
    # --- action view ---
    # def action_view_rnd(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Research And Development',
    #         'view_mode': 'kanban,tree,form',
    #         'res_model': 'design.process',
    #         'domain': [('sample_request_id', '=', self.id)],
    #     }
    
    def action_view_rnd(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'R & D',
            'view_mode': 'kanban,form',
            'res_model': 'design.process',
            'domain': [('crm_id', '=', self.lead_id.id)],
            'context': {'default_crm_id': self.lead_id.id},
        }

    def action_view_mo(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Manufacturing Orders',
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'domain': [('sample_request_id', '=', self.id)],
        }

    def action_view_sale(self): 
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('sample_request_id', '=', self.id)],
        }

    

class CrmSampleRequestLine(models.Model):
    _name = 'crm.sample.request.line'
    _description = 'Sample Request Detail'

    # name = fields.Char(string='Name')
    sample_request_id = fields.Many2one(comodel_name='crm.sample.request', string='Sample Request')
    product_id = fields.Many2one(comodel_name='product.product', string='Item', required=True)
    description = fields.Text(string='Description')
    qty = fields.Float(string='Quantity', required=True)
    uom_id = fields.Many2one(comodel_name='uom.uom', string='Unit of Measure', required=True,)
    attachment = fields.Binary(string='Image1', )
    attachment2 = fields.Binary(string='Image2', )
    attachment3 = fields.Binary(string='Image3', )
    remark = fields.Text('Remark', strip_style=True)
    # parent_state = fields.Selection(string='Status', related='sample_request_id.state', store=True)

    # mo_id = fields.Many2one(comodel_name='mrp.production', string='MO Created', copy=False)
    # process_state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('waiting', 'Waiting'),
    #     ('process', 'Process'),
    #     ('done', 'Done')],
    #     string='State',default='draft')

    @api.onchange("product_id")
    def get_prod(self):
        for x in self:
            prod = x.product_id
            x.qty = 1
            x.uom_id = prod.uom_id.id


class CrmSampleRequestLine1(models.Model):
    _name = 'crm.sample.request.line1'
    _description = 'Details Sample Request'

    name = fields.Char(string='Name')
    sample_request_id = fields.Many2one(comodel_name='crm.sample.request', string='Sample Request')
    product_id = fields.Many2one(comodel_name='product.product', string='Spec. Design Item', required=True)
    design_detail_date = fields.Date('Design Detail Created Date',default=fields.Date.context_today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('to_review', 'To Review'),
        ('marketing_review', 'Marketing Review'),
        ('in_review', 'Assign Buyer'),
        ('confirm', 'Confirmed'),
        ('need_revised', 'Need Revised'),
        ('revised', 'Revised')
    ], string='Status',default='draft')

