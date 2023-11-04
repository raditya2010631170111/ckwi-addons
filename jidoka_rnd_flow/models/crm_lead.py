from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    design_detail_ids = fields.One2many('design.detail', 'crm_id', string='Design Detail')
    state_design_detail = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('to_review', 'To Review'),
        ('marketing_review', 'Marketing Review'),
        ('in_review', 'Assign Buyer'),
        ('confirm', 'Confirmed'),
        ('need_revised', 'Need Revised')
    ], string='State Design Detail',related="design_detail_ids.state")

    state_designdetail = fields.Char('state_designdetail', 
        compute='_compute_state_designdetail')
    is_show_button_revised = fields.Boolean(string='Show Button Revised', default=False, compute='_compute_state_designdetail')
    is_show_send = fields.Boolean(string='Show Button', default=False)
    def _compute_state_designdetail(self):
        # design_detail = self.design_detail_ids.search([('state','=','marketing_review'),('crm_id','=',self.id)]).mapped('state')
        for r in self:
            design_detail = r.design_detail_ids.filtered(lambda l: l.state in ['marketing_review', 'in_review'])
            if design_detail:
                r.state_designdetail = design_detail
                r.is_show_button_revised = True
            elif 'in_review' in design_detail.mapped('state'):
                r.state_designdetail = 'in_review'
                r.is_show_button_revised = False
            else:
                r.state_designdetail = 'marketing_review'
                r.is_show_button_revised = False

    
    def o_source(self) :
        revisi_record = self.search([('request_no', '=', self.request_no_rev)], limit=1)
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'crm.lead',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': revisi_record.id,
                'target': 'current',
            }
    

# self.design_detail_ids.search([('crm_id','=',self.id)]).mapped('state')


# self.design_detail_ids.state
    # state_design_detail = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('processing', 'Processing'),
    #     ('to_review', 'To Review'),
    #     ('marketing_review', 'Marketing Review'),
    #     ('in_review', 'Assign Buyer'),
    #     ('confirm', 'Confirmed'),
    #     ('need_revised', 'Need Revised')
    # ], string='State',default='draft', related="design_detail_ids.state")
    # trevised = fields.Char('revised')
    
    def create_revisi(self):
        # import pdb;pdb.set_trace()
        view = self.env.ref('jidoka_rnd_flow.wizard_design_detail_revised_view_form')
        # domain = [('crm_id','=',self.id),('state','in',('marketing_review','in_review'))]
        return {
            'name': _('Design Detail Revised'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.design.detail.revised',
            'views': [(view.id, 'form')],
            # 'domain' : domain,
            'view_id': view.id,
            'target': 'new',
            'context':{
                'default_crm_id':self.id,
                'default_parent_domain':'marketing_review', 
                # 'default_parent_domain':'marketing_review',
                'default_is_need_revised':True,
                # 'default_type_button':'revisi',
                # 'default_detail_line_ids': self.ids
            }
        }
 
    
    # def create_revisi1(self, default=None):
    #     self.is_arch = True
    #     old_request_no = self.request_no or 'New'
    #     req_no = self.request_no_rev 
    #     req_no= self.request_no.split('.Rev-')[0] if self.request_no else None


        
    #     if old_request_no.endswith('.Rev'):
    #         # cek apakah nomor revisi sudah terdapat pada nomor permintaan lama
    #         if old_request_no.split('.Rev-')[-1].isdigit():
    #             # jika sudah terdapat nomor revisi pada nomor permintaan lama, ambil nomor revisi dan tambahkan 1
    #             rev_number = int(old_request_no.split('.Rev-')[-1])
    #             new_rev_number = rev_number + 1
    #             # buat nomor permintaan baru dengan nomor revisi yang sudah ditambahkan 1
    #             new_request_no = f"{old_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"
    #         else:
    #             # jika belum terdapat nomor revisi pada nomor permintaan lama, tambahkan nomor revisi 01
    #             new_request_no = f"{old_request_no}.Rev-01"
    #     else:
    #         # jika tidak terdapat ".Rev-" pada nomor permintaan lama, tambahkan ".Rev-01"
    #         new_request_no = f"{old_request_no}.Rev-01"
        
    #     # split nomor revisi dan cek apakah ada lebih dari 1 nomor revisi, jika ada, gunakan nomor revisi yang terbesar
    #     rev_numbers = [int(x.split('.Rev-')[-1]) for x in self.search([('request_no', 'like', f'{old_request_no.rsplit(".Rev-", 1)[0]}%.Rev-')]).mapped('request_no')]
    #     if rev_numbers:
    #         new_rev_number = max(rev_numbers) + 1
    #         new_request_no = f"{old_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"
        
    #     # periksa apakah nomor permintaan baru sudah ada di database
    #     while self.search_count([('request_no', '=', new_request_no)]) > 0:
    #         # jika sudah ada, tambahkan 1 pada nomor revisi dan buat nomor permintaan baru
    #         rev_number = int(new_request_no.split('.Rev-')[-1])
    #         new_rev_number = rev_number + 1
    #         new_request_no = f"{new_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"
            
    #     # duplikasi record dan ubah nomor permintaan menjadi nomor permintaan yang baru
    #     new_record = super(CrmLead, self).copy(default)
    #     new_record.write({'request_no': new_request_no,
    #                       'request_no_rev' :req_no,
    #                       'is_arch': False,
    #                       'is_r_mar' : False,
    #                       'spec_design_ids':self.spec_design_ids.ids,
    #                     #  'approval_history_ids': self.approval_history_ids.ids,
    #                       })
        
    #     # kembalikan aksi untuk membuka record baru dengan nomor permintaan yang sudah diubah
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'crm.lead',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_id': new_record.id,
    #         'target': 'current',
    #     }

    def create_revisi1(self, default=None):
        view_id = self.env.ref('jidoka_rnd_flow.create_revisi1_view_form').id
        return {
            'name': _('Revisi From Marketing'),
            'view_mode': 'form',
            'res_model': 'create.revisi1.wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


#         # import pdb;pdb.set_trace()
#         view = self.env.ref('jidoka_rnd_flow.wizard_design_detail_revised_view_form1')
#         # domain = [('crm_id','=',self.id),('state','in',('marketing_review','in_review'))]
#         return {
#             'name': _('Design Detail Revised'),
#             'type': 'ir.actions.act_window',
#             'view_mode': 'form',
#             'res_model': 'wizard.design.detail.revised',
#             'views': [(view.id, 'form')],
#             # 'domain' : domain,
#             'view_id': view.id,
#             'target': 'new',
#             'context':{
#                 'default_crm_id':self.id,
#                 # 'default_parent_domain':'draft', 
#                 'default_parent_domain':'marketing_review',
#                 'default_is_need_revised':True,
#                 # 'default_type_button':'revisi',
#                 # 'default_detail_line_ids': self.ids
#             }
#         }
# # default_detail_line_ids': [(0,0,{
#             'type_button': 'revisi'
#                 })for x in self.design_detail_ids]
# self.env['crm.lead']

    def create_assign_buyer(self):
        #import pdb;pdb.set_trace()
        # self.design_detail_ids.filtered(lambda l: l.state in ['marketing_review', 'in_review'])
        # self.design_detail_ids.filtered(lambda l: l.state in ['marketing_review'])
        view = self.env.ref('jidoka_rnd_flow.wizard_design_detail_assign_view_form')
        # domain = [('crm_id','=',self.id),('state','=',('marketing_review'))]
        return {
            'name': _('Buyer Review'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            # 'domain': domain,
            'res_model': 'wizard.design.detail.assign',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context':{
                'default_crm_id':self.id,
                'default_parent_domain':'marketing_review',
                # 'default_is_need_assign':True,
            }
        }

    # def views_sample_request(self):
    #         sample_request_vals = {
    #             'lead_id': self.id,
    #             'request_no': self.request_no,
    #             'user_team_id': self.user_team_id.id,
    #             'rnd_team_id':self.rnd_team_id.id,
    #             'department_rnd_id': self.department_rnd_id.id,
    #             'material_ids': [(6, 0, self.detail_material_ids.ids)],
    #             'detail_finish_ids': [(6, 0, self.detail_finish_ids.ids)],
    #             'user_id': self.user_id.id,
    #             'department_id': self.department_id.id,   
    #             'pricelist_id' : self.pricelist_id.id,
    #             # 'user_rnd_id':self.user_rnd_id.id,
    #             'partner_id': self.partner_shipping_id.id,
    #             'date_deadline': self.date_deadline,
    #             'purpose': 'Sample Request from CRM',
    #             'state': 'draft',
    #         }
    #         view = self.env.ref('jidoka_crm_sample_request.crm_sample_request_view_form')
           
    #         return {
    #             'name': _('Sample Request'),
    #             'type': 'ir.actions.act_window',
    #             'view_mode': 'tree',
    #             'domain': [('request_no', '=', sample_request.request_no)],
    #             # 'domain': [],
    #             'res_model': 'crm.sample.request',
    #             'views': [(False, 'tree'), (False, 'form')],
    #             'view_id': False,
    #             'target': 'current',
    #             'context': {'create': False},
    #             'search_view_id': False,
    #             'search_view_embed': False,
    #             'view_type': 'form',
    #             'view_id': False,
    #             'search_menu_id': False,
    #             'actions': [
    #                 {'type': 'ir.actions.act_window',
    #                 'name': 'Open Sample Request',
    #                 'res_model': 'crm.sample.request',
    #                 'view_type': 'form',
    #                 'view_mode': 'form',
    #                 'view_id': False,
    #                 'target': 'current',
    #                 'context': {}},
    #             ],
    #             'columns': {
    #                 'field_name': {
    #                     'string': 'Column Name',
    #                     'type': 'char',
    #                     'clickable': True,
    #                     'action': 'form',
    #                 },
    #             },
    #         }

    def send_data(self):
            # import pdb;pdb.set_trace()
            self.is_show_send = False

            sample_request_vals = {
                'lead_id': self.id,
                'request_no': self.request_no,
                'user_team_id': self.user_team_id.id,
                'rnd_team_id':self.rnd_team_id.id,
                'department_rnd_id': self.department_rnd_id.id,
                'material_ids': [(6, 0, self.detail_material_ids.ids)],
                'detail_finish_ids': [(6, 0, self.detail_finish_ids.ids)],
                'user_id': self.user_id.id,
                'department_id': self.department_id.id,   
                'pricelist_id' : self.pricelist_id.id,
                # 'user_rnd_id':self.user_rnd_id.id,
                'partner_id': self.partner_shipping_id.id,
                'date_deadline': self.date_deadline,
                'purpose': 'Sample Request from CRM',
                'state': 'draft',
            }
            sample_request = self.env['crm.sample.request'].create(sample_request_vals)

            # Get latest confirmed design detail line
            latest_detail_line = self.design_detail_ids.filtered(lambda x: x.state == 'confirm').sorted(key=lambda r: r.create_date)[-1]
            line_detail_vals = []
            if latest_detail_line:
                line_detail_vals.append((0, 0, {
                    'product_id': latest_detail_line.product_id.id,
                    'design_detail_date': latest_detail_line.design_detail_date,
                    'name': latest_detail_line.name,
                    'state': latest_detail_line.state,
                    # 'process_state':line.process_state,
                }))

            if line_detail_vals:
                sample_request.write({'line_detail_ids': line_detail_vals})

            line_vals = []
            for line in self.spec_design_ids:
                if any(detail[2]['product_id'] == line.item_id.id for detail in line_detail_vals):
                    line_vals.append((0, 0, {
                        'product_id': line.item_id.id,
                        'qty': line.quantity,
                        'uom_id': line.uom_id.id,
                        'attachment': line.attachment,
                        'description': line.description,
                    }))

            if not line_vals:
                raise UserError(_('There are no confirmed products'))
                
            sample_request.write({'line_ids': line_vals})

            view = self.env.ref('jidoka_crm_sample_request.crm_sample_request_view_form')
                    
            return {
                'name': _('Sample Request'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'domain': [('request_no', '=', sample_request.request_no)],
                # 'domain': [],
                'res_model': 'crm.sample.request',
                'views': [(False, 'tree'), (False, 'form')],
                'view_id': False,
                'target': 'current',
                'context': {'create': False},
                'search_view_id': False,
                'search_view_embed': False,
                'view_type': 'form',
                'view_id': False,
                'search_menu_id': False,
                'actions': [
                    {'type': 'ir.actions.act_window',
                    'name': 'Open Sample Request',
                    'res_model': 'crm.sample.request',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': False,
                    'target': 'current',
                    'context': {}},
                ],
                'columns': {
                    'field_name': {
                        'string': 'Column Name',
                        'type': 'char',
                        'clickable': True,
                        'action': 'form',
                    },
                },
            }

             # return {
            #     'name': _('Sample Request'),
            #     'type': 'ir.actions.act_window',
            #     'view_mode': 'tree',
            #     'res_id': sample_request.id,
            #     'res_model': 'crm.sample.request',
            #     'views': [(view.id, 'tree')],
            #     'view_id': view.id,
            #     'target': 'current',
            # }

            

    def confirm_buyer(self):
        view = self.env.ref('jidoka_rnd_flow.wizard_design_detail_confirm_view_form')
        self.is_show_send = True
        # domain=[('crm_id', '=',parent.crm_id),('state','=',('in_review'))]"
        return {
            'name': _('Confirm Buyer'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            # 'domain': domain,
            'res_model': 'wizard.design.detail.confirm',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context':{
                'default_crm_id':self.id,
                'default_parent_domain':'in_review',
                # 'default_is_need_confirm':True,
            }
        }
    
class CreateRevisi1Wizard(models.TransientModel):
    _name = 'create.revisi1.wizard'
    
    notes = fields.Text(string='Notes')
    
    def create_revisi1(self,default=None):
        crm_lead = self.env['crm.lead'].browse(self._context.get('active_id'))
        crm_lead.is_arch = True
        old_request_no = crm_lead.request_no or 'New'
        req_no = crm_lead.request_no_rev
        req_no= crm_lead.request_no.split('.Rev-')[0] if crm_lead.request_no else None

        if old_request_no.endswith('.Rev'):
            if old_request_no.split('.Rev-')[-1].isdigit():
                rev_number = int(old_request_no.split('.Rev-')[-1])
                new_rev_number = rev_number + 1
                new_request_no = f"{old_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"
            else:
                new_request_no = f"{old_request_no}.Rev-01"
        else:
            new_request_no = f"{old_request_no}.Rev-01"

        rev_numbers = [int(x.split('.Rev-')[-1]) for x in crm_lead.search([('request_no', 'like', f'{old_request_no.rsplit(".Rev-", 1)[0]}%.Rev-')]).mapped('request_no')]
        if rev_numbers:
            new_rev_number = max(rev_numbers) + 1
            new_request_no = f"{old_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"

        while crm_lead.search_count([('request_no', '=', new_request_no)]) > 0:
            rev_number = int(new_request_no.split('.Rev-')[-1])
            new_rev_number = rev_number + 1
            new_request_no = f"{new_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"

        new_record = crm_lead.copy(default)
        new_record.write({'request_no': new_request_no,
                          'request_no_rev' :req_no,
                          'is_arch': False,
                          'is_r_mar' : False,
                        #   'spec_design_ids':crm_lead.spec_design_ids.ids,
                          'description': self.notes,
                          })
        line_spec = []
        for spec_design in crm_lead.spec_design_ids:
            line_spec.append((0, 0, {
                'item_id': spec_design.item_id.id,
                'uom_id': spec_design.uom_id.id,
                'quantity': spec_design.quantity,
                'note': spec_design.note,
                'description': spec_design.description,
                'attachment': spec_design.attachment,

            }))

        new_record.write({'spec_design_ids': line_spec})

        l_history = []
        for history in crm_lead.approval_history_ids:
            l_history.append((0, 0, {
                'stage_id': history.stage_id,
                'user_id': history.user_id.id,
                'comment': history.comment,
                'attachment': history.attachment,
                'create_date': history.create_date,
                'request_no': history.request_no,

            }))

        new_record.write({'approval_history_ids': l_history})

        crm_lead.is_r_mar = False


        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': new_record.id,
            'target': 'current',
        }