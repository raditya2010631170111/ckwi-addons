from odoo import fields, models, api, _
from odoo.exceptions import UserError

class SampleRequestApprove(models.TransientModel):

    """Ask a reason for the purchase order cancellation."""

    _name = "approval.history.sample.wizard"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__

    reason = fields.Text(string="Comment")

    def action_confirm(self):
        lead = self._context.get("active_id")
        if lead is None:
            return act_close
        lead = self.env["crm.sample.request"].browse(lead)

        lead.ensure_one()
        lead.write({
            'state': 'approved'
        })
        # create DP

        # lead._create_design_process()
        
        # create MO
        
        # lead._create_mo()
        # link MO to DP

        # base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        # base_url += '/web#id=%d&model=%s&view_type=form' % (lead.id, lead._name)

        # email = lead.create_uid.login
        # name = lead.create_uid.name
        # partner_id = lead.create_uid.partner_id.id

        # if self.reason:
        #     reason = self.reason
        # else:
        #     reason = ''

        # mail_param = self.env['ir.config_parameter'].get_param('crm_sample.sample_request_manager_approve_template')
        # mail_temp = self.env.ref(mail_param)
        # email_template = mail_temp
        # email_template.email_to = email
        # email_values = {'url': base_url, 'name': name, 'reason': self.reason}
        # email_template.sudo().with_context(email_values).send_mail(lead.id, force_send=True)

        # send notif to user
        # url = ('<br></br><a href="%s">%s</a>') % (base_url, lead.name)
        # name = ('Halo, %s.') % (name)
        # body = name + ' Sample Request berikut sudah di approve dengan comment: ' + reason + url
        # self.send_notif(partner_id, body, 'user')


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


class SampleRequestReject(models.TransientModel):

    """Ask a reason for the purchase order cancellation."""

    _name = "approval.history.sample.wizard.reject"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__

    reason = fields.Text(string="Comment")

    def action_confirm(self):
        lead = self._context.get("active_id")
        if lead is None:
            return act_close
        lead = self.env["crm.sample.request"].browse(lead)

        lead.ensure_one()
        lead.write({
            'state': 'rejected'
        })

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&model=%s&view_type=form' % (lead.id, lead._name)

        email = lead.create_uid.login
        name = lead.create_uid.name
        partner_id = lead.create_uid.partner_id.id

        mail_param = self.env['ir.config_parameter'].get_param('crm_sample.sample_request_manager_reject_template')
        mail_temp = self.env.ref(mail_param)
        email_template = mail_temp
        email_template.email_to = email
        email_values = {'url': base_url, 'name': name, 'reason': self.reason}
        email_template.sudo().with_context(email_values).send_mail(lead.id, force_send=True)

        # send notif to user
        url = ('<br></br><a href="%s">%s</a>') % (base_url, lead.name)
        name = ('Halo, %s.') % (name)
        body = name + ' Contract Review berikut sudah di reject dengan reason: ' + self.reason + url
        self.send_notif(partner_id, body, 'user')

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