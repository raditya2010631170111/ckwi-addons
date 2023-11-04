from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ModelTechnicalName(models.TransientModel):
    _inherit = "approval.history.rnd.wizard"
    
    # override???
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
            lead.create_design_detail()
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
            lead.validate_design()
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
        # notif ke user yg login???
        author = user.partner_id
        lead.message_post(author_id=author.id,
            body=message,
            message_type='notification',
            subtype_xmlid="mail.mt_comment",
            notification_ids=notification_ids,
            partner_ids=[user.partner_id.id],
        )
