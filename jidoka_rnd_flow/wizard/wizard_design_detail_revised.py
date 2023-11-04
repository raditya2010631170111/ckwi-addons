from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class WizardDesignDetailRevised(models.TransientModel):
    _name = 'wizard.design.detail.revised' 
    _description = 'Wizard Design Detail Revised'
    
    crm_id = fields.Many2one('crm.lead', string='CRM')
    detail_line_ids = fields.One2many('wizard.design.detail.revised.line', 'wizard_design_detail_id', string='Detail Line')
    parent_domain = fields.Char('Parent Domain')
    is_need_revised = fields.Boolean('Is Need Revised?',default=False)
    is_need_assign = fields.Boolean('Is Assign Buyer?',default=False)
    is_need_confirm = fields.Boolean('Is Confirm Buyer?',default=False)



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
    
    # @api.depends('depends')
    # def _compute_state(self):
    #     for r in self:
    #         if r.type_button == 'revisi':                
    #             r.state = ''
    
    
    


    # @api.onchange('crm_id')
    # def _onchange_crm_id(self):
    #     if self.crm_id.design_detail_ids:
    #         vals = [(5,0)]
    #         for rec in self.crm_id.design_detail_ids.filtered(lambda r:r.state == 'in_review'):
    #             vals.append((0,0,{'design_detail_id':rec.id,'name':rec.name}))
    #         self.detail_line_ids = vals


# self.crm_id.design_detail_ids
# len(self.crm_id.design_detail_ids)

# self.crm_id.design_detail_ids.search([('state','=','draft'),('crm_id','=',self.crm_id.id)])
# self.crm_id.design_detail_ids.search([('state','=','marketing_review'),('crm_id','=',self.crm_id.id)])

# self.crm_id.design_detail_ids.search([('state','=','need_revised'),('crm_id','=',self.crm_id.id)])

    
    def action_confirm(self):
        self.with_context(display_product=True)
       # import pdb;pdb.set_trace()
        # t_design_crm = len(self.crm_id.design_detail_ids.search([('crm_id','=',self.crm_id.id), ('state','in',('marketing_review', 'in_review'))]))
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

class WizardDesignDetailRevisedLine(models.TransientModel):
    _name = 'wizard.design.detail.revised.line'
    _description = 'Wizard Design Detail Revised Line'

    wizard_design_detail_id = fields.Many2one('wizard.design.detail.revised', string='Wizard Design Detail')
    design_detail_id = fields.Many2one('design.detail', string='Design Detail')
    # design_detail_id = fields.Many2one('design.detail', string='Design Detail')
    design_detail_date = fields.Date('Design Detail Created Date',related='design_detail_id.design_detail_date')
    state = fields.Selection(string='State',related='design_detail_id.state')
    type_button = fields.Selection([
        ('revisi', 'Revisi'),
        ('assign', 'Revisi'),
        ('confirm', 'Revisi')
    ], string='type_button')
    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('processing', 'Processing'),
    #     ('to_review', 'To Review'),
    #     ('marketing_review', 'Marketing Review'),
    #     ('in_review', 'Assign Buyer'),
    #     ('confirm', 'Confirmed'),
    #     ('need_revised', 'Need Revised')
    # ],string='State')
    
    # @api.depends('product_id')
    # def _compute_state(self):
    #     for r in self:
    #         design_detail = 
    
    
    feedback_date = fields.Date('Feedback Date',default=fields.Date.context_today,required=False)
    feedback_notes = fields.Text('Feedback Notes',required=False)
    product_id = fields.Many2one('product.product', related='design_detail_id.product_id',readonly=False, store=True)
    name = fields.Char('Reference')
   

    # @api.onchange('design_detail_id')
    # def _onchange_design_detail_id(self):
    #     if self.design_detail_id:
    #         self.name = self.design_detail_id.name
    # @api.onchange('product_id')
    # def ganti_domain(self):
    #     for rec in self:
    #         crm_lead = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
    #         product_ids = crm_lead.design_detail_ids.mapped('product_id')
    #         data_one_many = self.wizard_design_detail_id.detail_line_ids.mapped('product_id')
    #         for data in crm_lead.design_detail_ids:
    #             print (data.product_id.name)
    #             if self.product_id.id == data.product_id.id:
    #                 self.design_detail_date = data.design_detail_date
    #                 self.name = data.name
    #                 self.state = data.state
    #                 self.feedback_notes= data.feedback_notes
    #         product_ids = product_ids - data_one_many
    #         return {
    #             'domain':
    #         {
    #             'product_id': [('id', 'in', product_ids.ids)]
    #         },}

    # @api.model
    # def default_get(self, field_list):
    #     res = super(WizardDesignDetailRevisedLine, self).default_get(field_list)
    #     if self.wizard_design_detail_id.is_need_revised:
    #         res['domain'] = {'design_detail_id': [('crm_id', '=',self.wizard_design_detail_id.crm_id),('state','in',('marketing_review','in_review'))]}
    #     elif self.wizard_design_detail_id.is_need_assign:
    #         res['domain'] = {'design_detail_id': [('crm_id', '=',self.wizard_design_detail_id.crm_id),('state','in',('marketing_review'))]}
    #     elif self.wizard_design_detail_id.is_need_confirm:
    #         res['domain'] = {'design_detail_id': [('crm_id', '=',self.wizard_design_detail_id.crm_id),('state','in',('in_review'))]}
    #     return res
    
    
    
    @api.onchange('design_detail_id')
    def _onchange_design_detail_id(self):
        if self.design_detail_id:
            self.design_detail_date = self.design_detail_id.design_detail_date
            self.name = self.design_detail_id.name
            self.state = self.design_detail_id.state
            self.feedback_notes= self.design_detail_id.feedback_notes
            if self.wizard_design_detail_id.is_need_revised:
                return {
                'domain':
            {
                'design_detail_id': [('crm_id', '=',self.wizard_design_detail_id.crm_id),('state','=',('marketing_review','in_review'))]
            },}
            elif self.wizard_design_detail_id.is_need_assign:
                return {
                'domain':
            {
                'design_detail_id': [('crm_id', '=',self.wizard_design_detail_id.crm_id),('state','=',('marketing_review'))]
            },}
            elif self.wizard_design_detail_id.is_need_confirm:
                return {
                    'domain':
                {
                    'design_detail_id': [('crm_id', '=',self.wizard_design_detail_id.crm_id),('state','in',('in_review'))]
                },}
           # self.design_detail_id=self.design_detail_id.design_detail_id
            # self.product_id = False
        else:
            self.design_detail_date = False
            self.name = False
            self.state = False
            self.feedback_notes= False
           # self.design_detail_id=False
            # self.product_id = False

    # def name_get_product_id (self):
    #     result = []
    #     for record in self:
    #         product_id  = record.product_id 
    #         feedback_notes = record.feedback_notes
    #         if feedback_notes:
    #             product_id  += ' - ' + feedback_notes
    #         result.append((record.id, product_id ))
    #     return result
