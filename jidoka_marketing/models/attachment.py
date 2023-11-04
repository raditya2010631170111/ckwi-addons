from odoo import models, fields, api, _
from datetime import date

import logging
_logger = logging.getLogger(__name__)






class design_image(models.Model):
    _name = 'design.image'
    _description = 'Design Image'



    name = fields.Text("Name")
    attachment = fields.Binary("Attachments")
    spec_id = fields.Many2one("spec.design","Spec. Design")


class verifikasi_design(models.Model):
    _name = 'verifikasi.design'
    _description = 'Verifikasi Design'



    name = fields.Text("Name")
    attachment = fields.Binary("Attachments")
    spec_id = fields.Many2one("spec.design","Spec. Design")



class sket_warna(models.Model):
    _name = 'sket.warna'
    _description = 'Sket Warna'
    _inherit = ['mail.thread']
    # _inherit = ['mail.thread', 'mail.activity.mixin']    



    name = fields.Text("Name", tracking=3)
    attachment = fields.Binary("Attachments", tracking=3)
    spec_id = fields.Many2one("spec.design","Spec. Design", tracking=3)
    # datetime = fields.Datetime('datetime', default=fields.Datetime.now,)
    date = fields.Date("date",default=date.today())
    user_id = fields.Many2one("res.users", "User", tracking=3)
    user_name = fields.Char()

    @api.model
    def create(self, vals):
        if 'user_name' not in vals and 'user_id' in vals:
            user = self.env['res.users'].browse(vals['user_id'])
            vals['user_name'] = user.name
        return super(sket_warna, self).create(vals)
        
    # def write(self, vals):
    #     res = super(sket_warna, self).write(vals)
    #     attachments = []
    #     name_attach = []
    #     # type_file = None
    #     type_file = []
    #     png = "image/png"
    #     pdf = "application/pdf"
    #     # png = mimetypes.types_map.get('.png', 'image/png')
    #     # pdf = mimetypes.types_map.get('.pdf', 'application/pdf')
    #     if self.attachment:
    #         attachments.append(self.attachment)
    #         name_attach.append("Attachment")
    #         type_file.append("%s" %(png))
    #         # type_file = "image/png"
    #     if self.attachment1:
    #         attachments.append(self.attachment1)
    #         name_attach.append("Attachment 1")
    #         type_file.append("%s" %(png))
    #         # type_file = "image/png"
    #     if self.attachment2:
    #         attachments.append(self.attachment2)
    #         name_attach.append("Attachment 2")
    #         type_file.append("%s" %(png))
    #         # type_file = "image/png"
    #     if self.attachment3:
    #         attachments.append(self.attachment3)
    #         name_attach.append("Attachment 3")
    #         type_file.append("%s" %(png))
    #         # type_file = "image/png"
    #     if self.attachment4:
    #         attachments.append(self.attachment4)
    #         name_attach.append("Attachment 4")
    #         type_file.append("%s" %(pdf))
    #         # type_file = "application/pdf"
    #     if self.attachment5:
    #         attachments.append(self.attachment5)
    #         name_attach.append("Attachment 5")
    #         type_file.append("%s" %(pdf))
    #         # type_file = "application/pdf"
    #     if self.attachment6:
    #         attachments.append(self.attachment6)
    #         name_attach.append("Attachment 6")
    #         type_file.append("%s" %(pdf))
    #         # type_file = "application/pdf"
    #     if self.attachment7:
    #         attachments.append(self.attachment7)
    #         name_attach.append("Attachment 7")
    #         type_file.append("%s" %(pdf))
    #         # type_file = "application/pdf"
            
    #     _logger.info("=============================attachments=============================")
    #     _logger.info(attachments)
    #     _logger.info("==========================================================")
        
    #     if attachments:
    #         attachment_ids = []
    #         for attachment in attachments:
    #             attachment_id = []
                
    #             attachment_data = {
    #                 # 'name': 'Attachment',
    #                 'name': name_attach,
    #                 # 'datas': attachment,
    #                 # 'datas_fname': 'attachment.png',
    #                 'res_model': self._name,
    #                 'res_id': self.id,
    #                 # 'mimetype': 'application/pdf'
    #                 # 'mimetype': "image/png",
    #                 'mimetype': type_file,
    #                 'type': 'binary',
    #                 'datas': attachment,
    #             }
    #             # attachment_id = self.env['ir.attachment'].create(attachment_data)
    #             # if attachment_id:
    #             if not attachment_id:
    #                 attachment_id = self.env['ir.attachment'].create(attachment_data)
    #             else:
    #                 attachment_id = self.env['ir.attachment'].write(attachment_data)
    #             attachment_ids.append(attachment_id.id)
                
    #             _logger.info("=============================attachment_ids=============================")
    #             _logger.info(attachment_ids)
    #             _logger.info("==========================================================")
            
    #         self.message_post(body='Attachments added', attachment_ids=attachment_ids)
    #     return res  
    
    def write(self, vals):
        res = super(sket_warna, self).write(vals)
        attachments = []
        name_attach = []
        type_file = []
        png = "image/png"
        pdf = "application/pdf"

        if vals.get('attachment'):
            attachments.append((self.attachment, "Attachment", png))
        if vals.get('attachment1'):
            attachments.append((self.attachment1, "Attachment 1", png))
        if vals.get('attachment2'):
            attachments.append((self.attachment2, "Attachment 2", png))
        if vals.get('attachment3'):
            attachments.append((self.attachment3, "Attachment 3", png))
        if vals.get('attachment4'):
            attachments.append((self.attachment4, "Attachment 4", pdf))
        if vals.get('attachment5'):
            attachments.append((self.attachment5, "Attachment 5", pdf))
        if vals.get('attachment6'):
            attachments.append((self.attachment6, "Attachment 6", pdf))
        if vals.get('attachment7'):
            attachments.append((self.attachment7, "Attachment 7", pdf))

        _logger.info("=============================attachments=============================")
        _logger.info(attachments)
        _logger.info("==========================================================")

        attachment_ids = []
        for attachment, name, file_type in attachments:
            if attachment:
                attachment_data = {
                    'name': name,
                    'res_model': self._name,
                    'res_id': self.id,
                    'mimetype': file_type,
                    'type': 'binary',
                    'datas': attachment,
                }
                attachment_id = self.env['ir.attachment'].create(attachment_data)
                attachment_ids.append(attachment_id.id)
                
        
        if 'user_id' in vals:
            user = self.env['res.users'].browse(vals['user_id'])
            vals['user_name'] = user.name

        # if attachment_ids:
        #     user_name = self.user_name or self.env.user.name
        #     image_name =  attachment_ids.name
        #     self.message_post(body='Attachments Update %s<br/> by %s<br/> Image change %s' % (self.date, user_name,image_name), attachment_ids=attachment_ids)
        if attachment_ids:
            user_name = self.user_name or self.env.user.name
            image_names = self.env['ir.attachment'].browse(attachment_ids).mapped('name')
            image_names_str = ", ".join(image_names)
            self.message_post(
                body='Attachments Update %s<br/> by %s<br/> Modified Image: %s' % (self.date, user_name, image_names_str),
                attachment_ids=attachment_ids
            )
        
        return res
    
    # attach = self.env['ir.attachment'].search([('res_model','=','sket.warna'),('res_id','=',self.id)])
class explode_diagram(models.Model):
    _name = 'explode.diagram'
    _description = 'Explode Diagram'



    name = fields.Text("Name")
    attachment = fields.Binary("Attachments")
    spec_id = fields.Many2one("spec.design","Spec. Design")


class sket_detail(models.Model):
    _name = 'sket.detail'
    _description = 'Sket Detail'



    name = fields.Text("Name")
    attachment = fields.Binary("Attachments")
    spec_id = fields.Many2one("spec.design","Spec. Design")



class verifikasi_sample(models.Model):
    _name = 'verifikasi.sample'
    _description = 'Verifikasi Sample'



    name = fields.Text("Name")
    attachment = fields.Binary("Attachments")
    spec_id = fields.Many2one("spec.design","Spec. Design")