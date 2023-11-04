import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)
class JidokaCRMLead(models.Model):
    _inherit = 'crm.lead'
    _rec_name = 'name'
    _description = 'Spec Design'



    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('research', 'Research'),
        ('assigned', 'Assigned'),
        ('done', 'Done')],
        string='State Approve',default='draft', tracking=True, copy=False)

    state_type = fields.Char("State Type", related="stage_id.code")
    revisi_date = fields.Datetime("Revisi Date")
    is_revisi = fields.Boolean("Is Revisi", default=False, copy=False)
    is_asigned = fields.Boolean("Is Assigned", default=False)
    is_waiting = fields.Boolean("Is Waiting", default=False)
    reason = fields.Text("Reason Revisi", default="hide")
    is_r_mar = fields.Boolean("Is Revisi Marketing", default=False)
    is_arch = fields.Boolean('arch', default=False)
    count_design_research = fields.Integer("Count", compute="count_design")
    count_rev = fields.Integer('Rev')
    origin_req = fields.Char('Origin Request')
    approval_history_ids = fields.One2many("approval.history","crm_id","Approval History")

    user_rnd_id = fields.Many2one("res.partner", string='Partner RnD')
    user_team_id = fields.Many2one("res.users", string='RnD Person')
    rnd_team_id = fields.Many2one("team.rnd","RnD Teams")
    department_rnd_id = fields.Many2one("hr.department","Department")
    code = fields.Char(string='code', related='stage_id.code', store=True)
    
    signature_pic = fields.Binary('Signature PIC')
    signature_mar_mangr = fields.Binary('Signature Marketing Manager')
    signature_rnd = fields.Binary('Signature RnD Manager')
    signed_pic = fields.Char('PIC', help='Name of the person that signed the SO.', copy=False)
    signed_mar_mangr = fields.Char('Marketing Manager', help='Name of the person that signed the SO.', copy=False)
    signed_rnd = fields.Char('RnD', help='Name of the person that signed the SO.', copy=False)
    signed_on = fields.Datetime('Signed Date', help='Date of the signature.', copy=False)

    probability = fields.Float(
        'Probability', group_operator="avg", copy=False,
        compute='_compute_probabilities', readonly=False, store=True, default=0)

    count_crm_sample_request = fields.Integer("Count", compute="count_sample_request")

    @api.depends(lambda self: ['tag_ids', 'stage_id', 'team_id'] + self._pls_get_safe_fields())
    def _compute_probabilities(self):
        lead_probabilities = self._pls_get_naive_bayes_probabilities()
        for lead in self:
            if lead.id in lead_probabilities:
                was_automated = lead.active and lead.is_automated_probability
                lead.automated_probability = lead_probabilities[lead.id]
                if was_automated:
                    lead.probability = lead.automated_probability

    @api.onchange("user_team_id")
    def get_teams_rnd(self):
        user = self.user_team_id
        if user:
            self.user_rnd_id = user.partner_id.id
            self.department_rnd_id = user.department_id.id
            self.rnd_team_id = user.team_rnd_id.id
    
    # design_process_id = fields.Many2one("design.process","Design Process")
    
    # design_detail_ids = fields.One2many('design.detail', 'design_process_id', string='Design Detail')

    def create_design_detail(self):
        for rec in self:
            vals = [(5,0)]
            for spec in rec.spec_design_ids:
                vals.append((0,0,{
                    'spec_design_id': spec.id,
                    # 'design_process_id': rec.id
                }))
            rec.design_detail_ids = vals


    def count_design(self):
        count_design = self.env['design.process'].search_count([('crm_id','=', self.id)])
        self.count_design_research = count_design

    def count_sample_request(self):
        sample_request = self.env['crm.sample.request'].search_count([('lead_id','=', self.id)])
        self.count_crm_sample_request = sample_request
        
        

    def get_to_design(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'R & D',
            'view_mode': 'kanban,form',
            'res_model': 'design.process',
            'domain': [('crm_id', '=', self.id)],
            'context': {'default_crm_id': self.id},
        }
    def get_to_crm_sample_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'CRM Sample Request',
            'view_mode': 'tree,form',
            'res_model': 'crm.sample.request',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }



    def action_validate_design(self):
        for x in self:
            if not x.user_rnd_id:
                raise UserError(_("RnD Teams not found"))
            design = self.env['design.process']
            crm = {
                'partner_id': x.partner_id.id,
                'deadline': x.date_deadline,
                'crm_id': x.id,
                'request_no': x.request_no,
                'partner_team' :x.partner_team.id,
                'department_id': x.department_id.id,
                'department_rnd_id': x.department_rnd_id.id,
                'user_id': x.user_id.id,
                'user_rnd_id': x.user_rnd_id.id,
                'user_team_id': x.user_team_id.id,
                'type_rnd': 'is_design',
                # 'rnd_team_id': x.rnd_team_id.id,
                'item' : x.item.id,
                'is_set' : x.is_set,
                'detail_material_ids': x.detail_material_ids.ids,
                'detail_finish_ids': x.detail_finish_ids.ids,
                'spec_design_ids' : x.spec_design_ids.ids,
                'design_detail_ids' : x.design_detail_ids.ids,
                'material_ids' : x.material_ids.ids,
                'special_ids' : x.special_ids.ids,
                'hardware_ids' : x.hardware_ids.ids,

            }
            design.create(crm)
            
            user_id = self.env.user.id
            user = self.env.user.name
            partner_id = self.partner_id.id
            # message = ("Oportunity %s from %s has been assigned") % (self.name, user)
            message = "Opportunity %s from %s has been assigned" % (self.name, user)
            # _logger.info("====================MESSAGE====================")
            # _logger.info(message)
            # _logger.info("========================================")

            notification_ids = [((0, 0, {
                       'res_partner_id': self.user_rnd_id.id,
                    #    'res_partner_id': x.user_rnd_id.id,
                       'notification_type': 'inbox'
                       }))]
            # _logger.info("====================notification_ids====================")
            # _logger.info(notification_ids)
            # _logger.info("========================================")
            
            # ==========================SEMENTARA TIDAK DIPAKAI DULU==========================
            # self.with_user(user_id).message_post(author_id=user_id,
            #                    body=(message),
            #                    message_type='notification',
            #                    subtype_xmlid="mail.mt_comment",
            #                    notification_ids=notification_ids,
            #                    partner_ids=[x.user_rnd_id.id],
            #                    notify_by_email=False,
            #                )
            # # self.sudo().message_post(author_id=user_id,
            # #                    body=(message),
            # #                    message_type='notification',
            # #                    subtype_xmlid="mail.mt_comment",
            # #                    notification_ids=notification_ids,
            # #                    partner_ids=[x.user_rnd_id.id],
            # #                    notify_by_email=False,
            # #                )
            
            # ====================================================

            x.is_asigned = True
            x.is_waiting = False
            return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Data Has been Processed, please check RnD',
                        'type': 'rainbow_man',
                    }
                }




    def action_set_to_draft(self):
        stage_draft = self.stage_id.search([('code','=','draft')])
        user = self.env.user
        mstr = [(0,0,{
            'stage_id' : "Set To Draft",
            'user_id' : user.id,
            })]
        self.approval_history_ids = mstr
        self.stage_id = stage_draft.id
        for line in self.spec_design_ids:
            line.process_state = 'draft'


    def action_to_manager(self):
        # if not self.spec_design_ids or len (self.spec_design_ids)==0:
        #     raise ValidationError ("Specific Design cannot be Empty")
        #if not self.signature_pic or not self.signature_mar_mangr or not self.signature_rnd or not self.signed_pic or not self.signed_mar_mangr or not self.signed_rnd or not self.signed_on:
            #raise ValidationError ("Please add page signature")
        return {
            'name' : _("Approve Manager With Comment"),
            'view_type' : 'form',
            'res_model' : 'approval.history.crm.wizard',
            'view_mode' : 'form',
            'type':'ir.actions.act_window',
            'target': 'new',
        }


    def action_approve_manager(self):
        #if not self.signature_pic or not self.signature_mar_mangr or not self.signature_rnd or not self.signed_pic or not self.signed_mar_mangr or not self.signed_rnd or not self.signed_on:
            #raise ValidationError ("Please add page signature")
        return {
                'name' : _("Approve Manager With Comment"),
                'view_type' : 'form',
                'res_model' : 'approval.history.crm.wizard',
                'view_mode' : 'form',
                'type':'ir.actions.act_window',
                'target': 'new',
            }

    def action_reject_manager(self):
        return {
                'name' : _("Reject Manager With Reason"),
                'view_type' : 'form',
                'res_model' : 'approval.history.crm.wizard.reject',
                'view_mode' : 'form',
                'type':'ir.actions.act_window',
                'target': 'new',
            }

    
    def action_create_design(self):
        if not self.spec_design_ids or len (self.spec_design_ids)==0:
            raise ValidationError ("Specific Design cannot be Empty")
        
        #if not self.signature_pic or not self.signature_mar_mangr or not self.signature_rnd or not self.signed_pic or not self.signed_mar_mangr or not self.signed_rnd or not self.signed_on:
            #raise ValidationError ("Please add page signature")
        
        self.is_r_mar = True


        return {
                'name' : _("Assigned RnD With Comment"),
                'view_type' : 'form',
                'res_model' : 'approval.history.crm.wizard',
                'view_mode' : 'form',
                'type':'ir.actions.act_window',
                'target': 'new',
            }
       
    def action_assigned_buyer(self):
        # if not self.spec_design_ids or len (self.spec_design_ids)==0:
        #     raise ValidationError ("Specific Design cannot be Empty")
        return {
                'name' : _("Assigned Buyer With Comment"),
                'view_type' : 'form',
                'res_model' : 'approval.history.crm.wizard',
                'view_mode' : 'form',
                'type':'ir.actions.act_window',
                'target': 'new',
            } 
