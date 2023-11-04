from odoo import fields, models, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class CrmSample(models.TransientModel):
    """Ask a reason for the purchase order cancellation."""
    _name = "approval.history.crm.wizard"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__

    reason = fields.Text(string="Comment")
    attachment = fields.Binary(string="Attachments")
    
    # def tes_confirm(self):
    #     lead = self._context.get("active_id")
    #     if lead is None:
    #         return
    #     lead = self.env["crm.lead"].browse(lead)
    #     lead.create_design_detail()

    def action_confirm(self):
        lead = self._context.get("active_id")
        if lead is None:
            return
        lead = self.env["crm.lead"].browse(lead)
        exim = lead.partner_id.exim_code
        if not exim:
             raise UserError(_("Please Check Code Buyer!"))
        crm_lead = self.env['crm.lead'].browse(self._context.get('active_id'))
        old_request_no = crm_lead.request_no
        state = lead.stage_id.name
        stage_draft = lead.stage_id.search([('code','=','draft')])
        stage_process = lead.stage_id.search([('code','=','process')])
        stage_research = lead.stage_id.search([('code','=','research')])
        stage_assigned = lead.stage_id.search([('code','=','assigned')])
        stage_done = lead.stage_id.search([('code','=','done')])
        user = self.env.user
        # lead.create_design_detail()

        mstr = [(0,0,{
            'stage_id' : state,
            'comment' : self.reason,
            'user_id' : user.id,
            'request_no' :old_request_no,
            'attachment' : self.attachment
            })]

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&model=%s&view_type=form' % (lead.id, lead._name)

        lead.approval_history_ids = mstr
        type = []
        if lead.state_type == stage_draft.code:
            lead.stage_id = stage_process.id

            group_mgr = self.env['ir.config_parameter'].get_param('crm.group_approve_manager_marketing')
            users = self.env.ref(group_mgr).users

            #send email when user validate / send email to approver
            mail_param = self.env['ir.config_parameter'].get_param('crm.validate_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            for user in users:
                partner_id = user.partner_id.id
                #send email to approver
                email = user.login
                email_template.email_to = email
                email_values = {'url': base_url, 'name': user.name}
                email_template.sudo().with_context(email_values).send_mail(lead.id, force_send=True)

                # send notif to approver
                
                # url = ('<br></br><a href="%s">%s</a>') % (base_url, lead.name)
                # name = ('Halo, %s.') % (user.name)
                # body = name + ' Ada CRM yang harus approve ' + url
                # self.send_notif(partner_id, body, 'manager')

            # if lead.request_no == 'New':
            #     no_seq = self.env['ir.sequence'].next_by_code('new.request') or 'New'
            #     month = fields.Date.today().strftime("%m")
            #     years = fields.Date.today().strftime("%y")
            #     lead.request_no = str(no_seq) +'/'+ month +'/'+ 'SP'+ '/' + years
            #     lead.origin_req =  str(lead.request_no)
        elif lead.state_type == stage_process.code:
            #send email when approve / send email to creator record
            email = lead.create_uid.login
            name = lead.create_uid.name
            partner_id = lead.create_uid.partner_id.id
            
            mail_param = self.env['ir.config_parameter'].get_param('crm.manager_approve_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            email_template.email_to = email
            email_values = {'url': base_url, 'name': name}
            email_template.sudo().with_context(email_values).send_mail(lead.id, force_send=True)

            #send notif to user
            url = ('<br></br><a href="%s">%s</a>') % (base_url, lead.name)
            name = ('Halo, %s.') % (name)
            body = name + ' CRM berikut sudah di approve ' + url
            self.send_notif(partner_id, body, 'user')

            lead.stage_id = stage_research.id
            _logger.info('================LEAD STAGE ID RESEARCH================')
            _logger.info(lead.stage_id)
            _logger.info('================LEAD STAGE ID RESEARCH================')
            # exim = lead.partner_id.exim_code
            # no_seq = self.env['ir.sequence'].next_by_code('no.mo.mrp') or 'New'
            # if lead.no_mo == 'New':
            #     lead.no_mo =  str(exim) + str(no_seq)
            #     lead.origin_mo =  str(exim) + str(no_seq)


        elif lead.state_type == stage_research.code:
            lead.stage_id = stage_assigned.id
            # lead.action_validate_design()
            # lead.stage_id = stage_assigned.id
            # _logger.info('================lead.state_type================')
            # _logger.info(lead.state_type)
            # _logger.info('================lead.state_type================')
            
            # _logger.info('================LEAD STAGE ID================')
            # _logger.info(lead.stage_id)
            # _logger.info('================LEAD STAGE ID================')
            
            lead = self._context.get("active_id")
            lead = self.env["crm.lead"].browse(lead)
            lead.ensure_one()
            
            # lead.create_design_detail()

            
            # lead.action_validate_design()

            #send email to team rnd
            email = lead.user_team_id.login
            name = lead.user_team_id.name
            partner_id = lead.user_team_id.partner_id.id
            email_cc = lead.rnd_team_id.email
            print('cek', email_cc, email, partner_id, name)

            mail_param = self.env['ir.config_parameter'].get_param('crm.assign_design_email_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            email_template.email_to = email
            email_template.email_cc = email_cc
            email_values = {'url': base_url, 'name': name}
            email_template.sudo().with_context(email_values).send_mail(lead.id, force_send=True)

            #send notif to user
            url = ('<br></br><a href="%s">%s</a>') % (base_url, lead.name)
            name = ('Halo, %s.') % (name)
            body = name + ' CRM berikut sudah dipindah ke Assign Design ' + url
            type = "user"
            # self.send_notif(partner_id, body, type)
            lead.action_validate_design()
            # lead.stage_id = stage_assigned.id
            self.send_notif(partner_id, body, type='user')

        elif lead.state_type == stage_assigned.code:
            lead.stage_id = stage_done.id
            rnd = self.env['design.process'].search([('crm_id','=', lead.id),('state_type','=','process')], limit=1)
            rnd.is_asigned = False
            no_seq = lead.partner_id.number_sample
            mounth_mo = lead.date_deadline.strftime("%m")
            yeard_mo = lead.date_deadline.strftime("%y")


    def send_notif(self, partner_id, body, type):
        bot = self.env['res.partner'].search([('name', '=', 'Marketing Bot')]).id

        if type == 'user':
            channel = self.env['mail.channel'].channel_get([partner_id])
            # channel = self.env['mail.channel'].channel_get([21])
            channel_id = self.env['mail.channel'].browse(channel["id"])
            # channel_id = self.env['mail.channel'].browse(self.env['mail.channel'].channel_get([21])["id"])
            channel_id.message_post(
                body=(body),
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
            )
            
            # self.env['mail.channel'].channel_get([3])

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
                    # 'channel_partner_ids': [(4, partner_id), (4, bot)]
                    'channel_partner_ids': [(4, partner_id)]

                })
            if len(channel_id) > 1:
                for chn in channel_id:
                    chn.message_post(
                        body=body,
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment',
                    )
            else:
                channel_id.message_post(
                    body=body,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                )
            # channel_id.message_post(
            #     body=body,
            #     message_type='comment',
            #     subtype_xmlid='mail.mt_comment',
            # )

class CrmSampleReject(models.TransientModel):
    """Ask a reason for the purchase order cancellation."""
    _name = "approval.history.crm.wizard.reject"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__

    reason = fields.Text(string="Comment")
    attachment = fields.Binary(string="Attachments")

    def action_confirm(self):
        lead = self._context.get("active_id")
        if lead is None:
            return act_close
        lead = self.env["crm.lead"].browse(lead)

        state = lead.stage_id.name
        stage_draft = lead.stage_id.search([('code','=','draft')])
        stage_process = lead.stage_id.search([('code','=','process')])
        stage_research = lead.stage_id.search([('code','=','research')])
        stage_assigned = lead.stage_id.search([('code','=','assigned')])
        stage_done = lead.stage_id.search([('code','=','done')])
        user = self.env.user
        mstr = [(0,0,{
            'stage_id' : state,
            'comment' : self.reason,
            'user_id' : user.id,
            'attachment' : self.attachment
            })]

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&model=%s&view_type=form' % (lead.id, lead._name)

        lead.approval_history_ids = mstr

        if lead.state_type == stage_process.code:
            #send email when approve / send email to creator record
            email = lead.create_uid.login
            name = lead.create_uid.name
            partner_id = lead.create_uid.partner_id.id

            mail_param = self.env['ir.config_parameter'].get_param('crm.manager_reject_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            email_template.email_to = email
            email_values = {'url': base_url, 'name': name, 'reason': self.reason}
            email_template.sudo().with_context(email_values).send_mail(lead.id, force_send=True)

            #send notif to user
            url = ('<br></br><a href="%s">%s</a>') % (base_url, lead.name)
            name = ('Halo, %s.') % (name)
            body = name + ' CRM berikut sudah di reject dengan reason:  ' + self.reason + url
            self.send_notif(partner_id, body, 'user')

            lead.stage_id = stage_draft.id


    def send_notif(self, partner_id, body, type):
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
                    'channel_partner_ids': [(4, partner_id)]
                })
            channel_id.message_post(
                body=body,
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
            )


class RnDSample(models.TransientModel):
    _name = "approval.history.rnd.wizard"
    _description = __doc__

    reason = fields.Text(string="Comment")
    attachment = fields.Binary(string="Attachments")

    # NOTE : method ini sudah dioverride sama yg lain!
    def action_confirm(self):
        lead = self._context.get("active_id")
        if lead is None:
            return
        lead = self.env["design.process"].browse(lead)
        stage_draft = lead.stage_id.search([('code','=','draft')])
        # stage_sket = lead.stage_id.search([('code','=','sket')])
        stage_perincian = lead.stage_id.search([('code','=','design')])
        stage_sample = lead.stage_id.search([('code','=','sample')])
        stage_approve = lead.stage_id.search([('code','=','approve')])
        stage_assigned = lead.stage_id.search([('code','=','assigned')])
        stage_confirm = lead.stage_id.search([('code','=','process')])
        stage_done = lead.stage_id.search([('code','=','done')])

        if lead.state_type == stage_draft.code:
            lead.stage_id = stage_sample.id
            for line in lead.spec_design_ids:
                line.process_state = 'waiting'
            stage_name = "Draft"
        # elif lead.state_type == stage_sket.code:
        #     lead.stage_id = stage_perincian.id
        #     for line in lead.spec_design_ids:
        #         line.process_state = 'waiting'
        #     stage_name = "Color Sketch"
        elif lead.state_type == stage_perincian.code:
            if not lead.spec_design_ids:
                raise UserError(_("Please Select Item Product!!"))    
            lead.stage_id = stage_sample.id
            lead.action_outstanding_bom()
            stage_name = "Design Details"
        elif lead.state_type == stage_sample.code:
            lead.stage_id = stage_approve.id
            stage_name = "Sample Details"
        elif lead.state_type == stage_approve.code:
            lead.stage_id = stage_assigned.id
            for line in lead.spec_design_ids:
                line.process_state = 'process'
            stage_name = "Approve"
        elif lead.state_type == stage_assigned.code:
            lead.stage_id = stage_confirm.id
            for line in lead.spec_design_ids:
                lead.is_asigned = True
                lead.crm_id.is_asigned = False
                lead.crm_id.is_waiting = True
            stage_name = "Process"
        elif lead.state_type == stage_confirm.code:
            lead.stage_id = stage_done.id
            for line in lead.spec_design_ids:
                line.process_state = 'done'
            stage_name = "Done"

        user = self.env.user
        author = user.partner_id
        lead.approval_history_ids = [(0,0,{
            'stage_id' : stage_name,
            'comment' : self.reason,
            'user_id' : user.id,
            'attachment' : self.attachment
        })]
        notification_ids = [((0, 0, {
            'res_partner_id': user.partner_id.id,
            'notification_type': 'inbox'
        }))]
        message = "%s Has Been Process!" % lead.stage_id.name
        lead.message_post(author_id=author.id,
            body=message,
            message_type='notification',
            subtype_xmlid="mail.mt_comment",
            notification_ids=notification_ids,
            #partner_ids=[user.partner_id.id],
            partner_ids=[user.partner_id.id] if user.partner_id else []
        )


