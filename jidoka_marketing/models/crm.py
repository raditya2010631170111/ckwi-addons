# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class JidokaCRM(models.Model):
    _inherit = 'crm.lead'
    _description = 'Spec Design'

    spec_design_ids = fields.One2many('spec.design','crm_id','Spec Design')
    material_ids = fields.One2many('spec.design.line','crm_id','Material', readonly=True)
    hardware_ids = fields.One2many('hardware.design.line','crm_id','Material')
    special_ids = fields.One2many('spec.intruction','crm_id','Instruction', readonly=True)
    item = fields.Many2one("product.product",'Item. Spec Design')
    is_set = fields.Boolean("Is Set", default=False)
    request_no = fields.Char("No. Spec Design",readonly=True, required=True, copy=False, default='New')
    request_no_rev = fields.Char(string='No. Revisi')
    department_id = fields.Many2one('hr.department', string='Department')
    detail_material_ids = fields.Many2many('design.material','design_ref_rel_matrial','design_ref_rel_id','material_ref_rel_id','Material')
    detail_finish_ids = fields.Many2many('design.finish','design_ref_rel_finish','crm_ref_id','finish_ref_id','Finish')
    crm_id = fields.Many2one("crm.lead","Revisi")
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Customer', required=True,)
    sample_no = fields.Char("Sample")
    partner_id = fields.Many2one(
        'res.partner', string='Buyor', index=True, tracking=10,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")
    company_currency = fields.Many2one("res.currency", string='Currency', related='pricelist_id.currency_id', readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', "Currency")
    partner_team = fields.Many2one('res.partner', string='Teams')

    @api.onchange("is_set")
    def change_item(self):
        if not self.is_set:
            self.item= False

    # @api.model_create_multi
    @api.model_create_multi
    def create(self, vals_list):
        lead = self._context.get("active_id")
        # if lead is None:
        #     return act_close
        lead = self.env["crm.lead"].browse(lead)
        
        for vals in vals_list:
            if vals.get('website'):
                vals['website'] = self.env['res.partner']._clean_website(vals['website'])
        leads = super(JidokaCRM, self).create(vals_list)

        for lead, values in zip(leads, vals_list):
            if any(field in ['active', 'stage_id'] for field in values):
                lead._handle_won_lost(values)
                
        if lead.request_no == 'New':
                no_seq = self.env['ir.sequence'].next_by_code('new.request') or 'New'
                month = fields.Date.today().strftime("%m")
                years = fields.Date.today().strftime("%y")
                lead.request_no = str(no_seq) +'/'+ month +'/'+ 'SP'+ '/' + years
                lead.origin_req =  str(lead.request_no)

        return leads

    @api.onchange('partner_id')
    def get_change_id(self):
        addr = self.partner_id.address_get(['delivery', 'invoice'])
        if self.partner_id:
            self.partner_shipping_id = addr['delivery']
        else:
            self.partner_shipping_id = False


    def o_source(self) :
        revisi_record = self.search([('request_no', '=', self.request_no_rev), ('name','=', self.name), ('spec_design_ids', '=' ,self.spec_design_ids.ids)], limit=1)
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'crm.lead',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': revisi_record.id,
                'target': 'current',
            }
    


#     docker-compose exec odoo odoo \
# -d ckwi \
# --db_password odoo \
# --db_host db \
# --no-xmlrpc \
# --stop-after-init \
# --update jidoka_marketing