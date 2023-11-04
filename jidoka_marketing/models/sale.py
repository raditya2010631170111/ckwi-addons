# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
import logging
_logger = logging.getLogger(__name__)


        
# STATE_IS_SC = [
#         ('cr_to_approve','Contract Review To Approve'),
#         ('cr','Contract Reviews'),
#         ('mo_to_approve', 'MO Waiting Approval'),
#         ('mo', 'Manufacture Order'),
#         ('sr_to_approve', 'SC Waiting Approval'),
#         ('sr', 'Sale Confirmation'),
#         ('sent', 'Quotation Sent'),
#         ('sale', 'Done'),
#         ('done', 'Locked'),
#         ('cancel', 'Cancelled')
# ]
STATE_IS_SO = [
        ('draft', 'Draft'),
        ('quotation_to_approve', 'Quotation To Approve'), 
        ('quotation', 'Quotation'),
        # ('cr_to_approve','Contract Review To Approve'),
        ('cr_draft', 'Contract Review Draft'),
]

# STATE_IS_REVISI = [
#         ('draft_rev', 'Sale Confirmation Draft'),
#         ('sr_rev', 'Sale Confirmation'),
# ]



class JidokaSale(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'

    buyer_po = fields.Char('Buyer PO')
    parent_id = fields.Many2one("sale.order","Parent", copy=False)
    is_parent = fields.Selection([
        ('is_mo', 'MO'),
        ('is_sc', 'SC'),
        ], string='Status Parent')


    is_type = fields.Selection([
        ('is_so', 'Is SO'),
        ('is_sc', 'Is SC'),
        ('is_revisi', 'is revisi')
        ], string='Type Order', copy=True)
    
    country_id = fields.Many2one('res.country', string='Country',related='partner_id.country_id',store=True,readonly=False)
    
    destination_id = fields.Many2one('res.country', string='Destination')
    is_cr = fields.Boolean('Is Contract Review',default=False)

    count_mo_search = fields.Integer("MO", compute="get_count_mo")
    
    

    date_meeting = fields.Date("Date Meeting")
    payment = fields.Char('Payment', default="T/T")
    no_cr = fields.Char("No. CR", default="New", readonly=True, copy=False)
    destination = fields.Char('Destination')
    # city_of_deliver = fields.Many2one("res.country.state","Deliver City", related="partner_shipping_id.state_id")
    # country_of_deliver = fields.Many2one("res.country","Deliver Country", related="city_of_deliver.country_id")

    city_of_deliver = fields.Many2one("res.country.state","Deliver State")
    city_deliver = fields.Char('Deliver City')
    country_of_deliver = fields.Many2one("res.country","Deliver Country")
    
    @api.onchange('country_of_deliver')
    def _onchange_country_of_deliver(self):
        self.city_of_deliver = False

    
    department_id = fields.Many2one('hr.department', string='Department')
    no_mo = fields.Char("No. MO", readonly=True, copy=False)
    request_no = fields.Char("No. Spec Design",readonly=True, copy=False)
    crm_id = fields.Many2one("crm.lead","Oportunity", readonly=True)
    partner_id = fields.Many2one(
        'res.partner', string='Buyer', readonly=True,
        states={'draft': [('readonly', False)],'cr_to_approve': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address', readonly=True, required=True,
        states={'draft': [('readonly', False)],'cr_to_approve': [('readonly', False)],'sent': [('readonly', False)], 'sale': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)

    # pricelist_id = fields.Many2one(
    # 'product.pricelist', string='Currency', check_company=True,  # Unrequired company
    # required=True, readonly=True, states={'draft': [('readonly', False)],'cr_to_approve': [('readonly', False)], 'sent': [('readonly', False)]},

    pricelist_id = fields.Many2one(
    'product.pricelist', string='Currency', check_company=True,  # Unrequired company
    required=True, readonly=[('state', '!=', 'draft')],
    domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
    help="If you change the pricelist, only newly added lines will be affected.")
    
    partner_invoice_id = fields.Many2one(
        'res.partner', string='Invoice Address',
        readonly=True, required=True,
        states={'draft': [('readonly', False)],'cr_to_approve': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    
    # date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)],'cr_to_approve': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")

    # date_order = fields.Datetime(string='Order Date', required=True, index=True, readonly=[('state', '!=', 'draft')], copy=False, default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    date_order = fields.Datetime(string='Order Date', required=True, index=True, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")

    # state_is_sc = fields.Selection(selection=STATE_IS_SC, required=True, copy=False, readonly=True, default='cr_to_approve', tracking=True, string='State' )
    
    state_is_so = fields.Selection(selection=STATE_IS_SO,  readonly=True, tracking=True, string='State', default='draft' )
    # state_is_revisi = fields.Selection(selection=STATE_IS_REVISI,  readonly=True, tracking=True, string='State', default='draft_rev' )

    state = fields.Selection([
        ('draft','Contract Review Draft'),
        ('cr_to_approve','Contract Review To Approve'),
        ('cr','Contract Reviews'),
        ('mo_to_approve', 'MO Waiting Approval'),
        ('mo', 'Manufacture Order'),
        ('sr_to_approve', 'SC Waiting Approval'),
        ('sr', 'Sale Confirmation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Done'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('rev', 'Revised'),
        # ('draft_rev', 'Sale Confirmation Draft'),
        # ('sr_rev', 'Sale Confirmation'),
        ], string='Status', readonly=True, tracking=True, default='draft')

        # string='Status', readonly=True, tracking=True, default='cr_to_approve')
    
    is_revisi = fields.Boolean('is_revisi')
    request_date = fields.Date('request_date', store=True)
    # request_date = fields.Date('request_date', compute='_compute_request_date', store=True)
    
    # @api.depends('order_line.request_date')
    # def _compute_request_date(self):
    #     for order in self:
    #         request_dates = order.order_line.mapped('request_date')
    #         non_empty_dates = [date for date in request_dates if date]
    #         order.request_date = min(non_empty_dates) if non_empty_dates else False

    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('quotation_to_approve', 'Quotation To Approve'), 
    #     ('quotation', 'Quotation'),
    #     ('cr_to_approve','Contract Review To Approve'),
    #     ('cr','Contract Reviews'),
    #     ('mo_to_approve', 'MO Waiting Approval'),
    #     ('mo', 'Manufacture Order'),
    #     ('sr_to_approve', 'SC Waiting Approval'),
    #     ('sr', 'Sale Confirmation'),
    #     ('sent', 'Quotation Sent'),
    #     ('sale', 'Done'),
    #     ('done', 'Locked'),
    #     ('cancel', 'Cancelled'),
    #     ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')

    # def action_confirm(self):
    #     if self._get_forbidden_state_confirm() & set(self.mapped('state')):
    #         raise UserError(_(
    #             'It is not allowed to confirm an order in the following states: %s'
    #         ) % (', '.join(self._get_forbidden_state_confirm())))

    #     for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
    #         order.message_subscribe([order.partner_id.id])
    #     self.write(self._prepare_confirmation_values())

    #     context = self._context.copy()
    #     context.pop('default_name', None)

    #     if self.is_revisi:
    #         self.with_context(context)._action_confirm_revisi()
    #     else:
    #         self.with_context(context)._action_confirm()

    #     if self.env.user.has_group('sale.group_auto_done_setting'):
    #         self.action_done()
    #     return True

    # def _action_confirm_revisi(self):
    #     for order in self:
    #         pickings_to_cancel = order.picking_ids.filtered(lambda picking: picking.state == 'done')
    #         for picking in pickings_to_cancel:
    #             move_to_cancel = picking.move_lines.filtered(lambda move: move.state == 'done')
    #             move_to_cancel._do_unreserve()
    #             move_to_cancel.write({'state': 'cancel'})
    #             picking.write({'state': 'cancel'})

    #         order.procurement_group_id = False
    #         order.order_line._action_launch_stock_rule()
    #     return True
    


    def revisi(self):
        # Memindahkan status ke 'rev'
        self.write({
            'state': 'rev',
            'is_revisi': False
        })

        old_request_no = self.name or 'New'

        if old_request_no.endswith('.Rev'):
            if old_request_no.split('.Rev-')[-1].isdigit():
                rev_number = int(old_request_no.split('.Rev-')[-1])
                new_rev_number = rev_number + 1
                new_request_no = f"{old_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"
            else:
                new_request_no = f"{old_request_no}.Rev-01"
        else:
            new_request_no = f"{old_request_no}.Rev-01"

        rev_numbers = [
            int(x.split('.Rev-')[-1])
            for x in self.search([('name', 'like', f'{old_request_no.rsplit(".Rev-", 1)[0]}%.Rev-')]).mapped('name')
        ]

        if rev_numbers:
            new_rev_number = max(rev_numbers) + 1
            new_request_no = f"{old_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"

        while self.env['sale.order'].search_count([('name', '=', new_request_no)]) > 0:
            rev_number = int(new_request_no.split('.Rev-')[-1])
            new_rev_number = rev_number + 1
            new_request_no = f"{new_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"

        new_order = self.copy(default={
                'name': True,
                'no_ckwi': self.name,
                'state': 'rev',
                'is_revisi' : True,
                'request_date' : self.order_line[0].request_date,
                'order_line': [(0, 0, {
                    # 'order_id': new_order.id,
                    'name_item' : ol.name_item,
                    'product_template_id': ol.product_template_id.id,
                    'product_id': ol.product_id.id,
                    'material_finishing': ol.material_finishing,
                    'material_finish_id': ol.material_finish_id.id,
                    'finish_id': ol.finish_id.id,
                    'sku': ol.sku,
                    'cont_load': ol.cont_load,
                    'product_uom_qty': ol.product_uom_qty,
                    'product_uom': ol.product_uom.id,
                    'sku_id': ol.sku_id.id,
                    'name': ol.name,
                    'william_fob_price': ol.william_fob_price,
                    'william_set_price': ol.william_set_price,
                    'packing_size_p': ol.packing_size_p,
                    'packing_size_l': ol.packing_size_l,
                    'packing_size_t': ol.packing_size_t,
                    'qty_carton': ol.qty_carton,
                    'cu_ft': ol.cu_ft,
                    'request_date': ol.request_date,
                    'inch_40': ol.inch_40,
                    'inch_40_hq': ol.inch_40_hq,
                    'fabric_colour_id': ol.fabric_colour_id.id

                }) for ol in self.order_line]
            })


        new_order.write({'state': 'sr'})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': new_order.id,
            'target': 'current',
        }



    def sr(self):
        self.write({'state' : 'sr_rev'}) 

    
    @api.model
    def create(self, vals):
        # cr_date = vals['create_date']
        cr_date = datetime.now()
        mounth_cr = cr_date.strftime("%m")
        yeard_cr = cr_date.strftime("%y")
        # name = []
        so_no = []
        nama_so_no = []
        type_bdg = []
        state = []
        state_so = []

        # TIDAK DIPAKAI SEMENTARA
        if vals.get('name', 'New') == 'New':
            type_bdg = vals.get('document_type', False)
        if type_bdg == 'marketing_quotation':
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.order')
            name = vals['name']
            vals['name'] = '%s'%(name)
            vals['state_is_so'] = 'draft'
            vals['state'] = None
        elif type_bdg == 'contract_review':
            vals['name'] = self.env['ir.sequence'].next_by_code('no.cr')
            name = vals['name']
            vals['name'] = "CKWI-%s/%s/CR/%s" %(name,mounth_cr,yeard_cr)
            # vals['state'] = 'cr_to_approve'
            vals['state'] = 'draft'
            vals['state_is_so'] = None
        
        
        # if not vals.get('state_is_so') == 'draft' and not vals.get('name', 'New') == 'New' :
        #     vals['name'] = self.env['ir.sequence'].next_by_code('sale.order')
        #     name = vals['name']
        #     vals['name'] = '%s'%(name)
        
        # elif not vals.get('state') == 'cr_to_approve' and vals.get('name', 'New') == 'New' :
        #     vals['name'] = self.env['ir.sequence'].next_by_code('no.cr')
        #     name = vals['name']
        #     vals['name'] = "CKWI-%s/%s/CR/%s" %(name,mounth_cr,yeard_cr)
            
        # if self.state == 'cr_to_approve':
        #     vals['name'] = self.env['ir.sequence'].next_by_code('no.cr')
        #     name = vals['name']
        #     vals['name'] = "CKWI-%s/%s/CR/%s" %(name,mounth_cr,yeard_cr)
        
        
        
        # _logger.info('======vals================')
        # _logger.info(vals)
        return super(JidokaSale, self).create(vals)
    
    def copy(self, default=None):
        default = default or {}
        cr_date = datetime.now()
        mounth_cr = cr_date.strftime("%m")
        yeard_cr = cr_date.strftime("%y")
        if self.document_type == 'marketing_quotation':
            # default['name'] = _("%s (copy)", self.name)
            default['name'] = self.env['ir.sequence'].next_by_code('sale.order')
            name = default['name']
            default['name'] = '%s'%(name)
        # elif self.document_type == 'contract_review':
        elif self.document_type == 'contract_review':
            # default['name'] = _("%s (copy)", self.name)
            default['name'] = self.env['ir.sequence'].next_by_code('no.cr')
            name = default['name']
            default['name'] = "CKWI-%s/%s/CR/%s" %(name,mounth_cr,yeard_cr)
        elif self.document_type == 'sale_confirmation':
            # default['name'] = _("%s (copy)", self.name)
            default['name'] = self.env['ir.sequence'].next_by_code('no.cr')
            # name = default['name']
            # default['name'] = "CKWI-%s/%s/CR/%s" % (name, mounth_cr, yeard_cr)
            
            old_request_no = self.name or 'New'
            
            if old_request_no.endswith('.Rev'):
                if old_request_no.split('.Rev-')[-1].isdigit():
                    rev_number = int(old_request_no.split('.Rev-')[-1])
                    new_rev_number = rev_number + 1
                    new_request_no = f"{old_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"
                else:
                    new_request_no = f"{old_request_no}.Rev-01"
            else:
                new_request_no = f"{old_request_no}.Rev-01"
            
            rev_numbers = [
                int(x.split('.Rev-')[-1])
                for x in self.search([('name', 'like', f'{old_request_no.rsplit(".Rev-", 1)[0]}%.Rev-')]).mapped('name')
            ]
            
            if rev_numbers:
                new_rev_number = max(rev_numbers) + 1
                new_request_no = f"{old_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"
            
            while self.env['sale.order'].search_count([('name', '=', new_request_no)]) > 0:
                rev_number = int(new_request_no.split('.Rev-')[-1])
                new_rev_number = rev_number + 1
                new_request_no = f"{new_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"
            
            default['name'] = new_request_no

            # Update the sequence
            # new_sequence = self.env['ir.sequence'].next_by_code('your.new.sequence.code')
            # default['name'] = new_sequence

        else:
            raise ValidationError(_("This document can not duplicate")) 
        so = super(JidokaSale, self).copy(default)
        # for ol in self.order_line:
        #     # Copy o2m and assign new project
        #     ol.copy(default={'order_id': so.id})
        # so.copy(default)
        _logger.info('======SO================')
        _logger.info(so)
        return so

    def action_quotation(self):
        for x in self:
            # x.state = 'quotation_to_approve'
            x.state_is_so = 'quotation_to_approve'

    def action_approve_quotation(self):
        for x in self:
            # x.state = 'quotation'
            x.state_is_so = 'quotation'

    def requotation(self):
        for record in self:
            new_quotation = record.copy(default=({'state':'quotation',}))

    def action_contact_reviews(self):
        for rec in self:
            for ls in rec.order_line.sorted(key=lambda l: l.request_date):
                    if not ls.request_date:
                        raise UserError(_('Please Check Ship Date On Product %s' %(ls.product_id.name)))
        
            wjk = self.browse(self.env.context.get('active_ids'))
            if wjk:
                st = wjk.ids
            else:
                st = self.ids
            self.requotation()
            self.ensure_one()
            return {
                'name' : _("Contract Reviews"),
                'view_type' : 'form',
                'res_model' : 'add.cr.rv.wizard',
                'view_mode' : 'form',
                'type':'ir.actions.act_window',
                'target': 'new',
                'context': {
                        'default_sale_ids': st,
                        'default_partner_id': self.partner_id.id,
                        },
            }
        
        
    def action_contact_reviews_r0(self):
        # import pdb;pdb.set_trace()
        aktifs = []  
        for self in self:        
            aktif = self.browse(self.env.context.get('active_ids'))
            if aktif:
                aktifs = aktif.ids
            return {
                'name' : _("Contract Reviews"),
                'view_type' : 'form',
                'res_model' : 'add.cr.rv.wizard',
                'view_mode' : 'form',
                'type':'ir.actions.act_window',
                'target': 'new',
                'context': {
                        'default_sale_ids': aktifs,
                        'default_partner_id': self.partner_id.id,
                        },
            }
        
    def action_contact_reviews_r1(self):
        # import pdb;pdb.set_trace()
        # partner = self.partner_id
        # self.requotation()
        # aktif = self.browse(self.env.context.get('active_ids'))
        line_vals = []
        for rec in self:
            # _logger.info('======aktif================')
            # _logger.info(aktif)
            
            for ol in rec.order_line:  
                line_vals.append((0,0,{
                    'product_template_id': ol.product_template_id.id,
                    'product_id': ol.product_id.id,
                    # 'material_finishing': ol.material_finishing,
                    'material_finish_id': ol.material_finish_id.id,
                    'finish_id': ol.finish_id.id,
                    'sku': ol.sku,
                    'request_date': ol.request_date,
                    'cust_ref':ol.cust_ref,
                    'cont_load': ol.cont_load,
                    'product_uom_qty':ol.product_uom_qty,
                    'product_uom':ol.product_uom.id,
                    'name': ol.name,
                    'product_packaging': ol.product_packaging.id,
                    'fabric_colour_id': ol.fabric_colour_id.id,
                    # 'sku_id': ol.sku_id.id,
                    # 'no_mo': no_mo,
                    'william_fob_price': ol.william_fob_price,
                    'william_set_price': ol.william_set_price,
                    'packing_size_p': ol.packing_size_p,
                    'packing_size_l': ol.packing_size_l,
                    'packing_size_t': ol.packing_size_t,
                    'qty_carton': ol.qty_carton,
                    'cu_ft': ol.cu_ft,
                    'inch_40': ol.inch_40,
                    'inch_40_hq': ol.inch_40_hq,
                    'price_total':ol.price_total,
                    'price_subtotal': ol.price_subtotal,
                    'price_tax':ol.price_tax,
                    'price_unit':ol.price_unit,
                    'state_is_so': False
                    }))
                    
                    
            
            cr_date = rec.create_date
            mounth_cr = cr_date.strftime("%m")
            yeard_cr = cr_date.strftime("%y")
            name = []
            so_no = []
            nama_so_no = []
            
        name = self.env['ir.sequence'].next_by_code('no.cr') or _('New')
        _logger.info('======name================')
        _logger.info(name)
            
        so_no =  "CKWI-%s/%s/CR/%s" %(name,mounth_cr,yeard_cr)
            
        if rec.name != so_no:
            nama_so_no = so_no
            # else:
            #     nama_so_no
                    
        order_vals = {
            'name': nama_so_no,
            'date_order': cr_date,
            'partner_id': rec.partner_id.id,
            'order_line': line_vals,
            # 'amount_untaxed': r.amount_untaxed,
            # 'amount_tax': r.amount_tax,
            # 'amount_total':r.amount_total,
            'document_type': 'contract_review',
            # 'state': 'cr_to_approve', #default sebelumnya
            'state_is_so': 'cr_draft',
            'is_type': 'is_sc',
            'is_cr': True  
            }
            
        _logger.info('======order_vals================')
        _logger.info(order_vals)

        view = self.env.ref('sale.view_order_form')
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
                           

    @api.onchange("opportunity_id")
    def change_shipp(self):
        partner_shipping = self.opportunity_id.partner_shipping_id.id
        if partner_shipping:
            self.partner_shipping_id = partner_shipping

    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     cr_date = datetime.now()
    #     mounth_cr = cr_date.strftime("%m")
    #     yeard_cr = cr_date.strftime("%y")
    #     name = []
    #     so_no = []
    #     # nama_so_no = []
    #     name = self.env['ir.sequence'].next_by_code('no.cr') or _('New')
    #     so_no =  "CKWI-%s/%s/CR/%s" %(name,mounth_cr,yeard_cr)
    #     self.name = so_no
        
    
    # @api.model
    # def _create_no_cr(self):
    # def create(self,vals):
    #     #  for self in self:
    #     # res = super(JidokaSale, self).default_get(fields)
    #     # if vals.get('state') == 'draft':
    #     #     cr_date = datetime.now()
    #     #     mounth_cr = cr_date.strftime("%m")
    #     #     yeard_cr = cr_date.strftime("%y")
    #     #     name = []
    #     #     so_no = []
    #     #     # nama_so_no = []
    #     #     name = self.env['ir.sequence'].next_by_code('no.cr') or _('New')
    #     #     so_no =  "CKWI-%s/%s/CR/%s" %(name,mounth_cr,yeard_cr)
    #     #     # self.name = so_no
    #     #     vals['name'] = so_no
    #     if vals.get('name', _('New')) == _('New'):
    #         if vals.get('state') == 'cr_to_approve':
    #             code = 'no.cr'
    #         else:
    #             code = 'sale.order'
    #         # TODO code berikut tidak dipakai, nomor dg sequence tersendiri
    #         # if vals.get('journal_id'):
    #         #     journal = self.env['account.journal'].sudo().browse(
    #         #         int(vals.get('journal_id')))
    #         #     if journal and journal.seq_code_voucher:
    #         #         check_sequence = self.env['ir.sequence'].sudo().search(
    #         #             [('code', '=', journal.seq_code_voucher)])
    #         #         if check_sequence:
    #         #             code = journal.seq_code_voucher
    #         #     elif journal and journal.code:
    #         #         code_journal = 'seq.voucher.'+journal.code
    #         #         check_sequence = self.env['ir.sequence'].sudo().search(
    #         #             [('code', '=', code_journal)])
    #         #         if check_sequence:
    #         #             code = code_journal
    #         vals['name'] = self.env['ir.sequence'].sudo().next_by_code(
    #             code) or _('New')
    #     result = super(JidokaSale, self).create(vals)
    #     return result

        
        
    
        # create
    
            
            
 

    def action_sale_confirm(self):
        for docs in self:
            docs.state = 'sr_to_approve'
            docs.is_type = 'is_sc'
            docs.document_type = 'sale_confirmation'

            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&model=%s&view_type=form' % (docs.id, docs._name)

            group_mgr = self.env['ir.config_parameter'].get_param('so.group_approve_manager_marketing')
            users = self.env.ref(group_mgr).users

            # send email when user validate / send email to approver
            mail_param = self.env['ir.config_parameter'].get_param('so.validate_sc_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            for user in users:
                partner_id = user.partner_id.id
                email = user.login
                email_template.email_to = email
                email_values = {'url': base_url, 'name': user.name}
                email_template.sudo().with_context(email_values).send_mail(docs.id, force_send=True)

                # send notif to approver
                url = ('<br></br><a href="%s">%s</a>') % (base_url, docs.name)
                name = ('Halo, %s.') % (user.name)
                body = name + ' Ada Sale Confirmation yang harus di approve ' + url
                self.send_notif(partner_id, body, 'manager')


    def action_draft_cr(self):
        # for rec in self:
        #     # Membuat sequencenya di sini
        #     seq_no = self.env['ir.sequence'].with_context(ir_sequence_date=fields.Date.today()).next_by_code('MO')
            
            
            
        #     # Mengupdate field "no_mo" pada setiap order_line
        #     for line in rec.order_line.filtered(lambda l: l.no_mo == 'New'):
        #         line.no_mo = seq_no
                

            # rec.state = 'cr_to_approve'
        
        obj_mo = []
        for so in self:
            so.state = 'cr_to_approve'
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
                    

    def action_approve_cr(self):
        # aktif = self.browse(self.env.context.get('active_ids'))
        # if aktif:
        #     p = aktif.ids
        return {
            'name': _("Approve With Comment"),
            'view_type': 'form',
            'res_model': 'approval.history.so.wizard',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{
                'default_partner_id': self.partner_id.id,
                'default_sale_order_id':self.id,
                }
        }
        
    def action_approve_mo(self):
        return {
            'name': _("Approve With Comment"),
            'view_type': 'form',
            'res_model': 'approval.history.mo.wizard',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        #     'context':{
        #         'default_partner_id': self.partner_id.id,}
        }

    def action_approve_sr(self):
        return {
            'name': _("Approve With Comment"),
            'view_type': 'form',
            # 'res_model': 'approval.history.so.wizard',
            'res_model': 'approval.history.sc.wizard',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{
                'default_document_type': 'sale_confirmation',
                #     'default_is_parent': 'is_mo',}
                }
        }


    def action_reject_cr(self):
        return {
            'name': _("Reject With Comment"),
            'view_type': 'form',
            'res_model': 'approval.history.so.wizard.reject',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_reject_mo(self):
        return {
            'name': _("Reject With Comment"),
            'view_type': 'form',
            'res_model': 'approval.history.mo.wizard.reject',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_reject_sr(self):
        return {
            'name': _("Reject With Comment"),
            'view_type': 'form',
            # 'res_model': 'approval.history.so.wizard.reject',
            'res_model': 'approval.history.sc.wizard.reject',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


    def action_manufactur_order(self):
        # import pdb;pdb.set_trace()
        for docs in self:
            docs.state = 'mo_to_approve'
            mo = docs.search([('parent_id', '=', docs.id)])
            # _logger.info('======MO================')
            # _logger.info(mo)
            
            if mo:
                mo.state = 'mo_to_approve'
            cr = docs.parent_id
            # _logger.info('======CR================')
            # _logger.info(cr)
            
            if cr:
                cr.state = 'mo_to_approve'
                
            obj_mo = []
            # _logger.info('======obj_mo================')
            # _logger.info(obj_mo)
            
            for ls in docs.order_line:
                # _logger.info('======docs.order_line================')
                # _logger.info(docs.order_line)
                
                
                if ls.no_mo == "New":
                    raise UserError(_('Cant Add New Product %s on MO!' %(ls.product_id.display_name)))
                # no_mo = ls.no_mo
                # _logger.info('======no_mo================')
                # _logger.info(no_mo)
                
                order_id = ls.order_id.id
                # _logger.info('======order_id================')
                # _logger.info(order_id)
                
                mo = [ l['no_mo'] for l in obj_mo]
                # _logger.info('======mo================')
                # _logger.info(mo)
                
                if no_mo not in mo:
                    obj_mo.append({
                            'no_mo' : no_mo,
                            'request_date' : ls.request_date
                        })
                    
                    
            for mo in obj_mo:
                order_line = docs.order_line.filtered(lambda l: l.no_mo == mo['no_mo'])
                # _logger.info('======order_line================')
                # _logger.info(order_line)
                
                sub_mo = docs.copy({
                        "parent_id" : docs.id,
                        "state" : docs.state,
                        "no_cr" : docs.no_cr,
                        "name" : mo['no_mo'],
                        "no_mo": mo['no_mo'],
                        'order_line' : order_line
                    })
                # _logger.info('======sub_mo================')
                # _logger.info(sub_mo)

            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            # _logger.info('======base_url================')
            # _logger.info(base_url)
                
            base_url += '/web#id=%d&model=%s&view_type=form' % (docs.id, docs._name)
            # _logger.info('======base_url+================')
            # _logger.info(base_url)

            group_mgr = self.env['ir.config_parameter'].get_param('so.group_approve_manager_marketing')
            users = self.env.ref(group_mgr).users

            # send email when user validate / send email to approver
            mail_param = self.env['ir.config_parameter'].get_param('so.validate_mo_template')
            mail_temp = self.env.ref(mail_param)
            email_template = mail_temp
            for user in users:
                partner_id = user.partner_id.id
                email = user.login
                email_template.email_to = email
                email_values = {'url': base_url, 'name': user.name}
                email_template.sudo().with_context(email_values).send_mail(docs.id, force_send=True)

                # send notif to approver
                url = ('<br></br><a href="%s">%s</a>') % (base_url, docs.name)
                name = ('Halo, %s.') % (user.name)
                body = name + ' Ada Manufacture Order yang harus di approve ' + url
                self.send_notif(partner_id, body, 'manager')

    def action_manufactur_order_tes(self):
        # import pdb;pdb.set_trace ()
        self.ensure_one()
        if not self.order_line:
            raise ValidationError("Please add a product")
        for ol in self.order_line:
            if ol.no_mo == 'New':
                raise ValidationError(_("No MO (New) in Order line can not add")) 
            
        obj_mo = []
        for ol in self.order_line.sorted(key=lambda l: l.no_mo):
            no_mo = ol.no_mo
            mo_date = ol.request_date.strftime("%y-%m")
            date = ol.request_date.strftime("%y-%m-%d")
            
            # if no_mo == 'New':
            #     raise ValidationError(_("Order line can not add")) 
            
            if no_mo not in [mo['no_mo'] for mo in obj_mo]:
                obj_mo.append({
                    'no_mo': no_mo,
                    'request_date': mo_date,
                    'date': date
                })
        
        # create ne MO (SO) per obj_mo
        for mo in obj_mo:
            line_vals = []
            for ol in self.order_line.filtered(lambda l: l.no_mo == mo['no_mo']):
                # if mo['no_mo'] == 'New':
                #     raise ValidationError(_("Order line can not add")) 
                
                line_vals.append((0,0,{
                    'product_template_id': ol.product_template_id.id,
                    'product_id': ol.product_id.id,
                    # 'material_finishing': ol.material_finishing,
                    'material_finish_id': ol.material_finish_id.id,
                    'finish_id': ol.finish_id.id,
                    'sku': ol.sku,
                    'request_date': ol.request_date,
                    'no_mo': mo['no_mo'],
                    'cust_ref': ol.cust_ref,
                    'no_po_cust' : ol.no_po_cust,
                    'cont_load': ol.cont_load,
                    'product_uom_qty':ol.product_uom_qty,
                    'product_uom':ol.product_uom.id,
                    # 'sku_id': l.sku_id.id,
                    'product_packaging':ol.product_packaging.id,
                    'name': ol.name,
                    'fabric_colour_id':ol.fabric_colour_id.id,
                    'william_fob_price': ol.william_fob_price,
                    'william_set_price': ol.william_set_price,
                    'packing_size_p': ol.packing_size_p,
                    'packing_size_l': ol.packing_size_l,
                    'packing_size_t': ol.packing_size_t,
                    'qty_carton': ol.qty_carton,
                    'cu_ft': ol.cu_ft,
                    'inch_40': ol.inch_40,
                    'inch_40_hq': ol.inch_40_hq,
                    'price_total':ol.price_total,
                    'price_subtotal': ol.price_subtotal,
                    'price_tax':ol.price_tax,
                    'price_unit':ol.price_unit,
                    'state_is_so':False
                }))
                
            # create line vals
            order_vals = {
                'parent_id': self.id,
                'name' : mo['no_mo'],
                'no_mo': mo['no_mo'],
                'partner_id': self.partner_id.id,
                'partner_invoice_id': self.partner_invoice_id.id,
                'partner_shipping_id': self.partner_shipping_id.id,
                'country_of_deliver':self.country_of_deliver.id,
                # 'city_of_deliver':self.city_of_deliver.id,
                'city_deliver':self.city_deliver,
                'department_id': self.department_id.id,
                'destination_id':self.destination_id.id,
                'date_order':self.date_order,
                'pricelist_id':self.pricelist_id.id,
                'term_id':self.term_id.id,
                'payment_term_id':self.payment_term_id.id,
                'document_type': 'manufacture_order',
                'notes_sale_id':self.notes_sale_id.id,
                'certification_id':self.certification_id.id,
                'is_type': 'is_sc',
                'no_cr': self.no_cr,
                'is_parent': 'is_mo',
                'state': 'mo',
                'is_cr':False,
                'order_line': line_vals,
                'state_is_so':False,
                'no_ckwi' : self.name,
                'origin' : self.origin,
                'buyer_po' : self.buyer_po,
                # 'amount_untaxed':self.amount_untaxed,
                # 'amount_tax':self.amount_tax,
                # 'amount_total':self.amount_total,
            }
            new_so = self.env['sale.order'].create(order_vals)
            
        # if self:
        #     return self.write({'state': 'mo_to_approve'})
        if self.state == 'cr':
            self.write({'state': 'mo_to_approve'})
            self.write({'document_type': 'manufacture_order'})
            self.write({'is_type': 'is_sc'})
            
            # self.state = 'mo_to_approve'
        # return True

        # res = super(JidokaSale, self).write({'state': 'mo_to_approve'})
        # return res
        
        # NOTIF EMAIL
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        # _logger.info('======base_url================')
        # _logger.info(base_url)
                
        base_url += '/web#id=%d&model=%s&view_type=form' % (self.id, self._name)
        # _logger.info('======base_url+================')
        # _logger.info(base_url)
        
        group_mgr = self.env['ir.config_parameter'].get_param('so.group_approve_manager_marketing')
        users = self.env.ref(group_mgr).users

        # send email when user validate / send email to approver
        mail_param = self.env['ir.config_parameter'].get_param('so.validate_mo_template')
        mail_temp = self.env.ref(mail_param)
        email_template = mail_temp
        
        for user in users:
            partner_id = user.partner_id.id
            email = user.login
            email_template.email_to = email
            email_values = {'url': base_url, 'name': user.name}
            _logger.info("========email_values========")
            _logger.info(email_values)
            email_template.sudo().with_context(email_values).send_mail(self.id, force_send=True)

            # send notif to approver
            url = ('<br></br><a href="%s">%s</a>') % (base_url, self.name)
            name = ('Halo, %s.') % (user.name)
            body = name + ' Ada Manufacture Order yang harus di approve ' + url
            # self.send_notif(partner_id, body, 'manager')
            self.send_notif(partner_id, body, 'manager')
    

    def action_sale_mo(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale MO',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'res_id':self.id,
            'domain': [('parent_id', '=', self.id)],
            'context':{
                'default_document_type': 'manufacture_order',}
        }

    def get_count_mo(self):
        mo = self.search_count([('parent_id','=', self.id)])
        self.count_mo_search = mo

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
            bot = self.env['res.partner'].search([('name', '=', 'Marketing Bot')]).id
            user = self.env.user.id
            print('user', user)
            partner_id = self.env.user.address_id.id
            channel_odoo_bot_users = 'Marketing Approval'
            channel_obj = self.env['mail.channel']
            channel_id = channel_obj.search([('name', 'like', channel_odoo_bot_users)])
            # _logger.info("===========BOT===========")
            # _logger.info(bot)
            # _logger.info("===========CHANNEL ID===========")
            # _logger.info(channel_id)
            # _logger.info("===========CHANNEL ID===========")
            # _logger.info("===========partner_id===========")
            # _logger.info(partner_id)
            # _logger.info("===========partner_id===========")
            if not channel_id:
                channel_id = channel_obj.create({
                    'name': channel_odoo_bot_users,
                    'email_send': False,
                    'channel_type': 'channel',
                    'public': 'public',
                    'channel_partner_ids': [(4, partner_id), (4, bot)]
                    # 'channel_partner_ids': [(4, partner_id)]
                })
            channel_id.message_post(
                body=body,
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
            )


class JidokaSaleLine(models.Model):
    _inherit = 'sale.order.line'
    _description = 'Sale Order Line'

    request_date = fields.Date("Ship Date", copy=False,required=True)
    is_revisi = fields.Boolean('is_revisi', related='order_id.is_revisi')

    @api.onchange('is_revisi')
    def onchange_is_revisi(self):
        if self.is_revisi:
            self.request_date = self.order_id.request_date
        else:
            self.request_date = False

    state_is_so = fields.Selection(
            related='order_id.state_is_so', string='Order Status', readonly=True,  store=True)

    state = fields.Selection(
            related='order_id.state', string='Order Status', readonly=True, store=True, default=None)

    def get_list_line(self):
        wjk = self
        res = []
        for line in wjk:
            res.append({
                "product_id": line.product_id.name,
                "finish_id" : line.finish_id.name,
                "name" : line.name,
                # "sku_id" : line.sku_id.name,
                "sku" : line.sku,
                "no_po" : line.no_po,
                "product_uom_qty": line.product_uom_qty,
                "product_uom" : line.product_uom.name,
                "price_unit": line.price_unit,
                "price_subtotal": line.price_subtotal,
                "product_packaging": line.product_packaging.name
                })
        return res

    def get_order_list(self):
        order = self.search([],limit=1)
        return order





class JidokaPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Sale Order'

    exim_code = fields.Char('Exim Code')
    number_sequence = fields.Integer("Number CR", readonly=True, default=1)
    number_mo = fields.Integer("Number MO", readonly=True, default=1)
    number_sample = fields.Integer("Number Sample Request", readonly=True, default=1)
    # terms_id = fields.Many2one('account.payment.term', string='Term')

