from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class ContractReview(models.TransientModel):

    _name = "approval.history.so.wizard"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__

    reason = fields.Text(string="Comment")
    attachment = fields.Binary(string="Attachments")
    
    partner_id = fields.Many2one('res.partner', string='Buyer')
    shipping_date = fields.Date(string='Contract Reviews Date', required=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order',store=True)

    # @api.model
    # def create(self, vals):
    #     lead = self._context.get("active_ids")
    #     if lead is None:
    #         return act_close
    #     lead = self.env["sale.order"].browse(lead)
    #     if lead.is_cr == 'True':
    #         cr_date = datetime.now()
    #         mounth_cr = cr_date.strftime("%m")
    #         yeard_cr = cr_date.strftime("%y")
    #         name = []
    #         so_no = []
    #         # nama_so_no = []
    #         if not vals.get('name') or vals['name'] == _('New'):
    #             vals['name'] = self.env['ir.sequence'].next_by_code('no.cr') or _('New')
    #             name = vals['name']
    #             so_no =  "CKWI-%s/%s/CR/%s" %(name,mounth_cr,yeard_cr)
    #             vals['name'] = so_no
                
                
    #         return super().create(vals)
    
    def action_confirm(self, vals):
        # import pdb;pdb.set_trace()
        lead = self._context.get("active_ids")
        if lead is None:
            return act_close
        lead = self.env["sale.order"].browse(lead)
        # _logger.info('======lead================')
        # _logger.info(lead)  
        
        aktifin = self.browse(self.env.context.get('active_ids'))
        # _logger.info('======aktifin================')
        # _logger.info(aktifin) 
          
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&model=%s&view_type=form' % (lead.id, lead._name)

        
        
        if lead.state == 'cr_to_approve':
            obj_mo = []
            for so in self.sale_order_id:
                for ol in so.order_line.sorted(key=lambda l: l.request_date):
                    # if ol.request_date == False:
                    #     raise UserError(_('Please Check Ship Date On Product %s' %(ls.product_id.name)))
                    mo_date = ol.request_date.strftime("%y-%m")
                    date = ol.request_date.strftime("%y-%m-%d")
                    mounth_mo = ol.request_date.strftime("%m")
                    yeard_mo = ol.request_date.strftime("%y")
                    
                    request_date = [l ['request_date'] for l in obj_mo]
                    _logger.info('======request_date1================')
                    _logger.info(request_date)
                    
                    if mo_date not in request_date:
                        obj_mo.append({
                            'request_date': mo_date,
                            'date': date,
                            'seq_mo':self.env['ir.sequence'].with_context(ir_sequence_date=ol.request_date).next_by_code('MO')
                            
                        })
                        _logger.info('======obj_mo================')
                        _logger.info(obj_mo)
                    # order_line = so.order_line.filtered(lambda l: l.request_date)
                    # _logger.info('======order_line================')
                    # _logger.info(order_line)   
                
            for mo in obj_mo:
                order_line = so.order_line.filtered(lambda l: l.request_date)
                _logger.info('======order_line================')
                _logger.info(order_line)   
                for obj in order_line:
                    if obj.no_mo == 'New':
                        if mo['date'] == obj.request_date.strftime("%y-%m-%d"):
                            seq_no = mo['seq_mo']
                        else:
                            seq_no = self.env['ir.sequence'].with_context(ir_sequence_date=obj.request_date).next_by_code('MO')
                            mo['seq_mo'] = seq_no
                        
                        mo['date'] = obj.request_date.strftime("%y-%m-%d")
                        obj.no_mo = seq_no
            
             
                        
                    
                
            
            lead.state = 'cr'
            lead.date_order = self.shipping_date
            
            # send email to user

            email = lead.create_uid.login
            name = lead.create_uid.name
            partner_id = lead.create_uid.partner_id.id

            mail_param = self.env['ir.config_parameter'].get_param('so.cr_manager_approve_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            email_template.email_to = email
            email_values = {'url': base_url, 'name': name, 'reason': self.reason}
            email_template.sudo().with_context(email_values).send_mail(lead.id, force_send=True)

            # send notif to user
            url = ('<br></br><a href="%s">%s</a>') % (base_url, lead.name)
            name = ('Halo, %s.') % (name)
            if self.reason:
                reason = self.reason
            else:
                reason = ''
            body = name + ' Contract Review berikut sudah di approve dengan comment: ' + reason + url
            self.send_notif(partner_id, body, 'user')
            
        elif lead.state == 'mo_to_approve':
            lead.state = 'mo'
            mo = lead.search([('parent_id', '=', lead.id)])
            if mo:
                mo.state = 'mo'
            cr = lead.parent_id
            if cr:
                cr.state = 'mo'

            #send email to user
            email = lead.create_uid.login
            name = lead.create_uid.name
            partner_id = lead.create_uid.partner_id.id

            mail_param = self.env['ir.config_parameter'].get_param('so.mo_manager_approve_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            email_template.email_to = email
            email_values = {'url': base_url, 'name': name, 'reason': self.reason}
            email_template.sudo().with_context(email_values).send_mail(lead.id, force_send=True)

            # send notif to user
            url = ('<br></br><a href="%s">%s</a>') % (base_url, lead.name)
            name = ('Halo, %s.') % (name)
            if self.reason:
                reason = self.reason
            else:
                reason = ''
            body = name + ' Manufacture Order berikut sudah di approve dengan comment: ' + reason + url
            self.send_notif(partner_id, body, 'user')



        elif lead.state == 'sr_to_approve':
            lead.state = 'sr'

            # send email to user
            email = lead.create_uid.login
            name = lead.create_uid.name
            partner_id = lead.create_uid.partner_id.id

            mail_param = self.env['ir.config_parameter'].get_param('so.sc_manager_approve_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            email_template.email_to = email
            email_values = {'url': base_url, 'name': name, 'reason': self.reason}
            email_template.sudo().with_context(email_values).send_mail(lead.id, force_send=True)

            # send notif to user
            url = ('<br></br><a href="%s">%s</a>') % (base_url, lead.name)
            name = ('Halo, %s.') % (name)
            if self.reason:
                reason = self.reason
            else:
                reason = ''
            body = name + ' Sale Confirmation berikut sudah di approve dengan comment: ' + reason + url
            self.send_notif(partner_id, body, 'user')

        # for r in self:
    # SHIPDATE TIDAK BOLEH KOSONG
    def action_confirm_tes(self):
        
        # import pdb;pdb.set_trace()
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&model=%s&view_type=form' % (self.id, self._name)
        
        for so in self.sale_order_id:
            # so.write({'state': 'cr'})
            # so.write({'document_type': 'contract_review'})
            so.state = 'cr'
            so.document_type = 'contract_review'
            so.date_order = self.shipping_date
            
            obj_mo = []
            for ls in so.order_line.sorted(key=lambda l: l.request_date):
                if not ls.request_date:
                    raise UserError(_('Please Check Ship Date On Product %s' %(ls.product_id.name)))
                mo_date = ls.request_date.strftime("%y-%m")
                date = ls.request_date.strftime("%y-%m-%d")
                mounth_mo = ls.request_date.strftime("%m")
                yeard_mo = ls.request_date.strftime("%y")
                request_date = [ l['request_date'] for l in obj_mo]
                if mo_date not in request_date:
                    obj_mo.append({
                            'request_date' : mo_date,
                            'date' : date,
                            'seq_mo' : self.env['ir.sequence'].with_context(ir_sequence_date=ls.request_date).next_by_code('MO'),
                            'mounth_mo': mounth_mo,
                            'yeard_mo': yeard_mo
                        })
            
            for mo in obj_mo:
                order_line = so.order_line.filtered(lambda l: l.request_date.strftime("%y-%m") == mo['request_date']).sorted(key=lambda l: l.request_date)
                _logger.info('======order_line================')
                _logger.info(order_line)  
                # order_line = so.order_line.filtered(lambda l: l.no_mo == mo['seq_mo'])
                for obj in order_line:
                    if obj.no_mo == 'New':
                        #check the same date
                        if mo['date'] == obj.request_date.strftime("%y-%m-%d"):
                            seq_no = mo['seq_mo']
                        else:
                            seq_no = self.env['ir.sequence'].with_context(ir_sequence_date=obj.request_date).next_by_code('MO')
                            mo['seq_mo'] = seq_no

                        # print('ini', mo['date'], obj.request_date.strftime("%y-%m-%d"),  seq_no)

                        mo['date'] = obj.request_date.strftime("%y-%m-%d")
                        obj.no_mo = seq_no
                
                
            # so.state = 'cr'
            
            # send email to user

            email = so.create_uid.login
            name = so.create_uid.name
            partner_id = so.create_uid.partner_id.id

            mail_param = self.env['ir.config_parameter'].get_param('so.cr_manager_approve_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            email_template.email_to = email
            email_values = {'url': base_url, 'name': name, 'reason': self.reason}
            email_template.sudo().with_context(email_values).send_mail(so.id, force_send=True)

            # send notif to user
            url = ('<br></br><a href="%s">%s</a>') % (base_url, so.name)
            name = ('Halo, %s.') % (name)
            if self.reason:
                reason = self.reason
            else:
                reason = ''
            body = name + ' Contract Review berikut sudah di approve dengan comment: ' + reason + url
            self.send_notif(partner_id, body, 'user')
            

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

    
class ContractReviewReject(models.TransientModel):
    
    _name = "approval.history.so.wizard.reject"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__

    reason = fields.Text(string="Comment")
    attachment = fields.Binary(string="Attachments")

    def action_confirm(self):
        lead = self._context.get("active_id")
        if lead is None:
            return act_close
        lead = self.env["sale.order"].browse(lead)

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&model=%s&view_type=form' % (lead.id, lead._name)

        if lead.state == 'cr_to_approve':
            lead.state = 'draft'

            # send email to user
            email = lead.create_uid.login
            name = lead.create_uid.name
            partner_id = lead.create_uid.partner_id.id

            mail_param = self.env['ir.config_parameter'].get_param('so.cr_manager_reject_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            email_template.email_to = email
            email_values = {'url': base_url, 'name': name, 'reason': self.reason}
            email_template.sudo().with_context(email_values).send_mail(lead.id, force_send=True)

            # send notif to user
            url = ('<br></br><a href="%s">%s</a>') % (base_url, lead.name)
            name = ('Halo, %s.') % (name)
            body = name + ' Contract Review berikut sudah direject dengan reason: ' + self.reason + url
            self.send_notif(partner_id, body, 'user')

        elif lead.state == 'mo_to_approve':
            lead.state = 'cr'
            mo = lead.search([('parent_id', '=', lead.id)])
            print('mo', mo)
            if mo:
                mo.state = 'cr'
            cr = lead.parent_id
            print('cr', cr)
            if cr:
                cr.state = 'cr'

            #send email to user
            email = lead.create_uid.login
            name = lead.create_uid.name
            partner_id = lead.create_uid.partner_id.id

            mail_param = self.env['ir.config_parameter'].get_param('so.mo_manager_reject_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            email_template.email_to = email
            email_values = {'url': base_url, 'name': name, 'reason': self.reason}
            email_template.sudo().with_context(email_values).send_mail(lead.id, force_send=True)

            # send notif to user
            url = ('<br></br><a href="%s">%s</a>') % (base_url, lead.name)
            name = ('Halo, %s.') % (name)
            body = name + ' Manufacture Order berikut sudah direject dengan reason: ' + self.reason + url
            self.send_notif(partner_id, body, 'user')


        elif lead.state == 'sr_to_approve':
            lead.state = 'mo'

            # send email to user
            email = lead.create_uid.login
            name = lead.create_uid.name
            partner_id = lead.create_uid.partner_id.id

            mail_param = self.env['ir.config_parameter'].get_param('so.sc_manager_reject_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            email_template.email_to = email
            email_values = {'url': base_url, 'name': name, 'reason': self.reason}
            email_template.sudo().with_context(email_values).send_mail(lead.id, force_send=True)

            # send notif to user
            url = ('<br></br><a href="%s">%s</a>') % (base_url, lead.name)
            name = ('Halo, %s.') % (name)
            body = name + ' Sale Confirmation berikut sudah direject dengan reason: ' + self.reason + url
            self.send_notif(partner_id, body, 'user')



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
            
class ManufacturingOrder(models.TransientModel):
    _name = 'approval.history.mo.wizard'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__

    reason = fields.Text(string="Comment")
    attachment = fields.Binary(string="Attachments")
    
    def action_confirm(self):
        # import pdb;pdb.set_trace()
        lead = self._context.get("active_id")
        if lead is None:
            return act_close
        lead = self.env["sale.order"].browse(lead)
          
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&model=%s&view_type=form' % (lead.id, lead._name)
        
        if lead.state == 'mo_to_approve':
            lead.state = 'mo'
            lead.is_parent = 'is_mo'
            mo = lead.search([('parent_id', '=', lead.id)])
            if mo:
                mo.state = 'mo'
            cr = lead.parent_id
            if cr:
                cr.state = 'mo'

            #send email to user
            email = lead.create_uid.login
            name = lead.create_uid.name
            partner_id = lead.create_uid.partner_id.id

            mail_param = self.env['ir.config_parameter'].get_param('so.mo_manager_approve_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            email_template.email_to = email
            email_values = {'url': base_url, 'name': name, 'reason': self.reason}
            email_template.sudo().with_context(email_values).send_mail(lead.id, force_send=True)

            # send notif to user
            url = ('<br></br><a href="%s">%s</a>') % (base_url, lead.name)
            name = ('Halo, %s.') % (name)
            if self.reason:
                reason = self.reason
            else:
                reason = ''
            body = name + ' Manufacture Order berikut sudah di approve dengan comment: ' + reason + url
            self.send_notif(partner_id, body, 'user')
    
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
 
class ManufacturingOrderReject(models.TransientModel):
    _name = 'approval.history.mo.wizard.reject'
    _description = __doc__

    reason = fields.Text(string="Comment")
    attachment = fields.Binary(string="Attachments")
    
    def action_confirm(self):
        lead = self._context.get("active_id")
        if lead is None:
            return act_close
        lead = self.env["sale.order"].browse(lead)

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&model=%s&view_type=form' % (lead.id, lead._name)
        
        if lead.state == 'mo_to_approve':
            lead.state = 'cr'
            mo = lead.search([('parent_id', '=', lead.id)])
            print('mo', mo)
            if mo:
                mo.state = 'cr'
            cr = lead.parent_id
            print('cr', cr)
            if cr:
                cr.state = 'cr'

            #send email to user
            email = lead.create_uid.login
            name = lead.create_uid.name
            partner_id = lead.create_uid.partner_id.id

            mail_param = self.env['ir.config_parameter'].get_param('so.mo_manager_reject_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            email_template.email_to = email
            email_values = {'url': base_url, 'name': name, 'reason': self.reason}
            email_template.sudo().with_context(email_values).send_mail(lead.id, force_send=True)

            # send notif to user
            url = ('<br></br><a href="%s">%s</a>') % (base_url, lead.name)
            name = ('Halo, %s.') % (name)
            body = name + ' Manufacture Order berikut sudah direject dengan reason: ' + self.reason + url
            self.send_notif(partner_id, body, 'user')



class SaleConfirmation(models.TransientModel):
    _name = 'approval.history.sc.wizard'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__

    reason = fields.Text(string="Comment")
    attachment = fields.Binary(string="Attachments")
    
    def action_confirm(self):
        lead = self._context.get("active_id")
        if lead is None:
            return act_close
        lead = self.env["sale.order"].browse(lead)
          
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&model=%s&view_type=form' % (lead.id, lead._name)
    
        if lead.state == 'sr_to_approve':
            lead.state = 'sr'
            lead.is_type = 'is_sc'
            lead.is_parent = 'is_mo'
            lead.document_type = 'sale_confirmation'

            # send email to user
            email = lead.create_uid.login
            name = lead.create_uid.name
            partner_id = lead.create_uid.partner_id.id

            mail_param = self.env['ir.config_parameter'].get_param('so.sc_manager_approve_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            email_template.email_to = email
            email_values = {'url': base_url, 'name': name, 'reason': self.reason}
            email_template.sudo().with_context(email_values).send_mail(lead.id, force_send=True)

            # send notif to user
            url = ('<br></br><a href="%s">%s</a>') % (base_url, lead.name)
            name = ('Halo, %s.') % (name)
            if self.reason:
                reason = self.reason
            else:
                reason = ''
            body = name + ' Sale Confirmation berikut sudah di approve dengan comment: ' + reason + url
            self.send_notif(partner_id, body, 'user')
    
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
    

class SaleConfirmationReject(models.TransientModel):
    _name = 'approval.history.sc.wizard.reject'
    _description = __doc__

    reason = fields.Text(string="Comment")
    attachment = fields.Binary(string="Attachments")
    
    def action_confirm(self):
        lead = self._context.get("active_id")
        if lead is None:
            return act_close
        lead = self.env["sale.order"].browse(lead)

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&model=%s&view_type=form' % (lead.id, lead._name)
        
        if lead.state == 'sr_to_approve':
            lead.state = 'mo'

            # send email to user
            email = lead.create_uid.login
            name = lead.create_uid.name
            partner_id = lead.create_uid.partner_id.id
            shipping_id = lead

            mail_param = self.env['ir.config_parameter'].get_param('so.sc_manager_reject_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            email_template.email_to = email
            email_values = {'url': base_url, 'name': name, 'reason': self.reason}
            email_template.sudo().with_context(email_values).send_mail(lead.id, force_send=True)

            # send notif to user
            url = ('<br></br><a href="%s">%s</a>') % (base_url, lead.name)
            name = ('Halo, %s.') % (name)
            body = name + ' Sale Confirmation berikut sudah direject dengan reason: ' + self.reason + url
            self.send_notif(partner_id, body, 'user')


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

    



    

    
    
    
    
       
            