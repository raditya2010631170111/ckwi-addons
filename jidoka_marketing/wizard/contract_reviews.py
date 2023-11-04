from odoo import fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ContractReviews(models.TransientModel):
    _name = "cr.rv.wizard"
    _description = __doc__

    partner_id = fields.Many2one("res.partner",string="Buyer", required=True)
    sale_id = fields.Many2one("sale.order",string="Contract Reviews", required=True)
    note = fields.Text("Note")

    def get_contact_reviews(self):
        for x in self:
            sj = self.env['sale.order'].search([('name','=', x.sale_id.name)])
            order_line = []
            for line in sj.order_line:
                order_line.append({
                    'product_id': line.product_id.name,
                    'name': line.name,
                    # 'sku_id': line.sku_id.name,
                    'sku': line.sku,
                    'no_mo': line.no_mo,
                    'no_po': line.no_po,
                    'no_po_cust' : line.no_po_cust,
                    'cust_ref': line.cust_ref,
                    'cont_load': line.cont_load,
                    'product_uom_qty': line.product_uom_qty,
                    'request_date': line.request_date,
                    })
            return order_line

    def action_contract_ref(self):
        return self.env.ref('jidoka_marketing.doc_contract_reviews_id').report_action(self, config=False)






class AddContractReviews(models.TransientModel):
    _name = "add.cr.rv.wizard"
    _description = __doc__

    partner_id = fields.Many2one("res.partner", string="Buyer", required=True)
    shipping_date = fields.Date(string="Contract Reviews", required=True)
    sale_ids = fields.Many2many("sale.order","sale_order_contract_reviews_ref","sale_order_id","contract_reviews",string="Contract Reviews", required=True)
    


    

    def action_contract_ref(self):
        # import pdb;pdb.set_trace()
        partner = self.partner_id

        for add in self.sale_ids:
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&model=%s&view_type=form' % (add.id, add._name)

            if add.partner_id.id != partner.id:
                raise UserError(_("You cannot use more than one Buyer for contract reviews %s", add.partner_id.name))
                
                
            # for r in add:
            #     r.state = 'cr_to_approve'
            #     r.document_type = 'contract_review'
                

            add.state = 'cr_to_approve'
            add.document_type = 'contract_review'
            # add.is_type = 'is_sc'
            # add.write({'state': 'cr_to_approve'})
            # add.write({'state': 'cr_to_approve'})

            group_mgr = self.env['ir.config_parameter'].get_param('so.group_approve_manager_marketing')
            users = self.env.ref(group_mgr).users

            #send email when user validate / send email to approver
            mail_param = self.env['ir.config_parameter'].get_param('so.validate_cr_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            for user in users:
                partner_id = user.partner_id.id
                #send email to approver
                email = user.login
                email_template.email_to = email
                email_values = {'url': base_url, 'name': user.name}
                email_template.sudo().with_context(email_values).send_mail(add.id, force_send=True)

                # send notif to approver
                url = ('<br></br><a href="%s">%s</a>') % (base_url, add.name)
                name = ('Halo, %s.') % (user.name)
                body = name + ' Ada Contract Review yang harus di approve ' + url
                self.send_notif(partner_id, body, 'manager')

            no_seq = add.partner_id.number_sequence
            cr_date = self.shipping_date
            mounth_cr = cr_date.strftime("%m")
            yeard_cr = cr_date.strftime("%y")
            if add.no_cr == 'New':
                seq = str("{:05n}".format(no_seq))
                add.no_cr =  "CKWI-" + seq[2:] +'/'+ str(mounth_cr) +'/'+ "CR" + '/'+str(yeard_cr)
                add.name =  add.no_cr

            # no_seq = add.partner_id.number_mo
            obj_mo = []
            for ls in add.order_line.sorted(key=lambda l: l.request_date):
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
                order_line = add.order_line.filtered(lambda l: l.request_date.strftime("%y-%m") == mo['request_date']).sorted(key=lambda l: l.request_date)
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

        so = self.sale_ids
        # # so.partner_id.number_sequence += 1
            
            
            
    def action_contract_ref_r0(self):
#         import pdb;pdb.set_trace()
        # partner = self.partner_id
        self.ensure_one()
        
        line_vals = []
        partner = self.partner_id
        # so_no = 'New'
        for r in self.sale_ids:
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&model=%s&view_type=form' % (r.id, r._name)

            if r.partner_id.id != partner.id:
                raise UserError(_("You cannot use more than one Buyer for contract reviews %s", r.partner_id.name))
            
            obj_mo = []
            for ls in r.order_line.sorted(key=lambda l: l.request_date):
                if not ls.request_date:
                    raise UserError(_('Please Check Ship Date On Product %s' %(ls.product_id.name)))
                
                if obj_mo:
                    if ls.request_date not in [mo['request_date'] for mo in obj_mo]:
                        obj_mo.append({
                            'request_date' : ls.request_date,
                            'seq_mo' : self.env['ir.sequence'].with_context(ir_sequence_date=ls.request_date).next_by_code('MO'),
                        })
                else:
                    obj_mo.append({
                        'request_date' : ls.request_date,
                        'seq_mo' : self.env['ir.sequence'].with_context(ir_sequence_date=ls.request_date).next_by_code('MO'),
                    })
                    
        for r in self.sale_ids:    
            for l in r.order_line:
                no_mo = 'New'
                for mo in obj_mo:
                    if mo['request_date'] == l.request_date:
                        no_mo = mo['seq_mo']
                        # break
                line_vals.append((0,0,{
                    'product_template_id': l.product_template_id.id,
                    'product_id': l.product_id.id,
                    # 'material_finishing': l.material_finishing,
                    'material_finish_id': l.material_finish_id.id,
                    # 'sku_id': l.sku_id.id,
                    'sku': l.sku,
                    'request_date': l.request_date,
                    'no_mo': no_mo,
                    'cont_load': l.cont_load,
                    'product_uom_qty':l.product_uom_qty,
                    'product_uom':l.product_uom.id,
                    'name': l.name,
                    'william_fob_price': l.william_fob_price,
                    'william_set_price': l.william_set_price,
                    'packing_size_p': l.packing_size_p,
                    'packing_size_l': l.packing_size_l,
                    'packing_size_t': l.packing_size_t,
                    'qty_carton': l.qty_carton,
                    'cu_ft': l.cu_ft,
                    'inch_40': l.inch_40,
                    'inch_40_hq': l.inch_40_hq,
                    'finish_id': l.finish_id.id,
                    'price_total':l.price_total,
                    'price_subtotal': l.price_subtotal,
                    'price_tax':l.price_tax,
                    'price_unit':l.price_unit
                    
                }))
                
                
        cr_date = self.shipping_date
        mounth_cr = cr_date.strftime("%m")
        yeard_cr = cr_date.strftime("%y")
        
        name = [] 
        so_no = []
        contract_review = []
        
        name = self.env['ir.sequence'].next_by_code('no.cr') or _('New')
        so_no =  "CKWI-%s/%s/CR/%s" %(name,mounth_cr,yeard_cr)
        
        # for r in self.sale_ids:
        #     contract_review = r.contract_review
        
        for r in self.sale_ids:
            if r.name != so_no:
                nama_so_no = so_no
                
        _logger.info('======so_no================')
        _logger.info(so_no)
            
        order_vals = {
            'name': nama_so_no,
            'no_cr': nama_so_no,
            'date_order': cr_date,
            'partner_id': self.partner_id.id,
            'document_type': 'contract_review',
            'order_line': line_vals,
            'amount_untaxed': r.amount_untaxed,
            'amount_tax': r.amount_tax,
            'amount_total':r.amount_total,
            'state': 'cr_to_approve',
            'is_type': 'is_so',
            'parent_id': self.id
            
        }
        view = self.env.ref('sale.view_order_form')
            # 'res_id' : object.id
        so = self.env['sale.order'].create(order_vals)
        
        return {
            'res_model': 'sale.order',
            'res_id': so.id,
            # 'target': 'new',
            'target': 'current',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id' : view.id,
        }
            
        
            

    def send_notif(self, partner_id, body, type):
        bot = self.env['res.partner'].search([('name', '=', 'Marketing Bot')]).id

        if type == 'user':
            channel = self.env['mail.channel'].channel_get([partner_id])
            channel_id = self.env['mail.channel'].browse(channel["id"])
            channel_id.message_post( body=(body), message_type='comment', subtype_xmlid='mail.mt_comment',
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
            channel_id.message_post( body=body, message_type='comment', subtype_xmlid='mail.mt_comment',
            )
        
# class MultiContractReviews(models.TransientModel):
#     _name = 'multi.cr.rv.wizard'
#     _description = 'Multi Cr Rv Wizard'
    
#     partner_id = fields.Many2one("res.partner", string="Buyer", required=True)
#     shipping_date = fields.Date(string="Shipping date", required=True)
#     sale_ids = fields.Many2many("sale.order","sale_order_multi_contract_reviews_ref","sale_order_id","contract_reviews",string="Contract Reviews", required=True)
#     sale_order_line_ids = fields.Many2many("sale.order.line","sale_order_line_multi_contract_reviews_ref","sale_order_line_id","contract_reviews",string="Multi Contract Reviews", required=True)
    

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'
    
    
    material_finishing = fields.Char('Material Finishing')    
    material_finish_id = fields.Many2many('design.material', string='Material')
