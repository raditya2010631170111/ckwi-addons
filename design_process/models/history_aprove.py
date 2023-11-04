

from odoo import models, api, fields,_




class historyApproval(models.Model):
    _name = "approval.history"
    _rec_name = "create_date"
    _description = "Role history"

    crm_id = fields.Many2one("crm.lead","CRM")
    design_id = fields.Many2one("design.process","Design")
    stage_id = fields.Char("State")
    user_id = fields.Many2one("res.users","User")
    comment = fields.Char("Comment")
    attachment = fields.Binary("Attachments")
    request_no = fields.Char(string='No. Spec Design')