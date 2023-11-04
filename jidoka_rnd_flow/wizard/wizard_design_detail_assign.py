from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class WizardDesignDetailAssign(models.TransientModel):
    _name = 'wizard.design.detail.assign'
    _description = 'Wizard Design Detail Assign'
    
    crm_id = fields.Many2one('crm.lead', string='CRM')
    detail_line_ids = fields.One2many('wizard.design.detail.assign.line', 'wizard_design_detail_id', string='Detail Line')
    parent_domain = fields.Char('Parent Domain')
    is_need_revised = fields.Boolean('Is Need Revised?',default=False)

    type_button = fields.Selection([
    ('revisi', 'Revisi'),
    ('assign', 'Assign Buyer'),
    ('confirm', 'Confirm Buyer')], string='type_button')

    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('to_review', 'To Review'),
        ('marketing_review', 'Marketing Review'),
        ('in_review', 'Assign Buyer'),
        ('confirm', 'Confirmed'),
        ('need_revised', 'Need Revised')
    ],string='State',
        compute='_compute_state' )
    


    def action_confirm(self):
        # t_design_crm = len(self.crm_id.design_detail_ids.search([('crm_id','=',self.crm_id.id),('state','=','marketing_review')]))
        # t_detail = len(self.detail_line_ids)

        # if t_detail >= t_design_crm:
        #     raise ValidationError ("Double Data")
        
        if self.detail_line_ids:
            for rec in self.detail_line_ids:
                # dl = 
                if self.parent_domain == 'marketing_review':
                    val = {
                        'name':rec.name
                    }
                    if self.is_need_revised:
                        val['feedback_date'] = rec.feedback_date
                        val['feedback_notes'] = rec.feedback_notes
                        val['state'] = 'need_revised'
                    else:
                        val['state'] = 'in_review'
                    rec.design_detail_id.write(val)
                elif self.parent_domain == 'in_review':
                    rec.design_detail_id.write({'state':'confirm'})

class WizardDesignDetailAssignLine(models.TransientModel):
    _name = 'wizard.design.detail.assign.line'
    _description = 'Wizard Design Detail Assign Line'

    wizard_design_detail_id = fields.Many2one('wizard.design.detail.assign', string='Wizard Design Detail')
    design_detail_id = fields.Many2one('design.detail', string='Design Detail')
    # design_detail_id = fields.Many2one('design.detail', string='Design Detail')
    design_detail_date = fields.Date('Design Detail Created Date',related='design_detail_id.design_detail_date')
    state = fields.Selection(string='State',related='design_detail_id.state')
    type_button = fields.Selection([
        ('revisi', 'Revisi'),
        ('assign', 'Revisi'),
        ('confirm', 'Revisi')
    ], string='type_button')

    
    
    feedback_date = fields.Date('Feedback Date',default=fields.Date.context_today,required=False)
    feedback_notes = fields.Text('Feedback Notes',required=False)
    product_id = fields.Many2one('product.product', related='design_detail_id.product_id',readonly=False, store=True)
    name = fields.Char('Reference')
   
    @api.onchange('design_detail_id')
    def _onchange_design_detail_id(self):
        if self.design_detail_id:
            self.design_detail_date = self.design_detail_id.design_detail_date
            self.name = self.design_detail_id.name
            self.state = self.design_detail_id.state
            self.feedback_notes= self.design_detail_id.feedback_notes
           # self.design_detail_id=self.design_detail_id.design_detail_id
            # self.product_id = False
        else:
            self.design_detail_date = False
            self.name = False
            self.state = False
            self.feedback_notes= False
           # self.design_detail_id=False
            # self.product_id = False

