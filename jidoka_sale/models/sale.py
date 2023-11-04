# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.misc import formatLang, get_lang
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import time


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'

    no_ckwi = fields.Char('Source Document')
    document_type = fields.Selection([
        ('marketing_quotation', 'Marketing Quotation'),
        ('contract_review','Contract Review'),
        ('manufacture_order','Manufacture Order'),
        ('sale_confirmation', 'Sale Confirmation')
        ], string='Document Type', compute='_get_document_type', store=True, default='marketing_quotation')
    # document_type = fields.Selection([
    #     ('marketing_quotation', 'Marketing Quotation'),
    #     ('contract_review','Contract Review'),
    #     ('manufacture_order','Manufacture Order'),
    #     ('sale_confirmation', 'Sale Confirmation')
    #     ], string='Document Type', compute='_get_document_type', store=True, default='marketing_quotation')
        #   <!-- ============JC-336============ -->
    notes_sale_id = fields.Many2one('res.notes.sale', string='Notes Sale')
    notes_sale = fields.Text('Tes Notes Sale')
        #   <!-- ============JC-336============ -->
    certification_id = fields.Many2one('res.certification', string='Certification')
    currency_id = fields.Many2one('res.currency', string='Currency', store=True)
    # certification = fields.Selection([
    #     ('fsc', 'FSC'),
    #     ('non fsc', 'Non FSC')
    # ], string='Certification')
    term_id = fields.Many2one(
        'account.payment.term', string='Terms', check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    # @api.depends('state')
    # def _get_document_type(self):
    #     for rec in self :
    #         if rec.state in ('draft', 'send', 'quotation','quotation_to_approve'):
    #             self.write({'document_type': 'marketing_quotation'})
    #         elif rec.state in ('cr','cr_to_approve'):
    #             self.write({'document_type': 'contract_review'})
    #         elif rec.state in ('mo', 'mo_to_approve'):
    #             self.write({'document_type': 'manufacture_order'})
    #         else :
    #             self.write({'document_type': 'sale_confirmation'})
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        - Sales Team
        """
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'fiscal_position_id': False,
            })
            return

        self = self.with_company(self.company_id)

        addr = self.partner_id.address_get(['delivery', 'invoice'])
        partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
            'term_id': self.partner_id.payment_term_jidoka_id and self.partner_id.payment_term_jidoka_id.id or False,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
        }
        user_id = partner_user.id
        if not self.env.context.get('not_self_saleperson'):
            user_id = user_id or self.env.context.get('default_user_id', self.env.uid)
        if user_id and self.user_id.id != user_id:
            values['user_id'] = user_id

        if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms') and self.env.company.invoice_terms:
            values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
        if not self.env.context.get('not_self_saleperson') or not self.team_id:
            values['team_id'] = self.env['crm.team'].with_context(
                default_team_id=self.partner_id.team_id.id
            )._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)], user_id=user_id)
        self.update(values)



    @api.depends('state_is_so', 'state')
    def _get_document_type(self):
        for rec in self :
            if rec.state_is_so in ('draft', 'send', 'quotation','quotation_to_approve'):
                self.write({'document_type': 'marketing_quotation'})
            elif rec.state in ('cr','cr_to_approve'):
                self.write({'document_type': 'contract_review'})
            elif rec.state in ('mo', 'mo_to_approve'):
                self.write({'document_type': 'manufacture_order'})
            else :
                self.write({'document_type': 'sale_confirmation'})

    
        
    # def _action_confirm(self):
    #     """ Implementation of additionnal mecanism of Sales Order confirmation.
    #         This method should be extended when the confirmation should generated
    #         other documents. In this method, the SO are in 'sale' state (not yet 'done').
    #     """
    #     # create an analytic account if at least an expense product
    #     for order in self:
    #         if any(expense_policy not in [False, 'no'] for expense_policy in order.order_line.mapped('product_id.expense_policy')):
    #             if not order.analytic_account_id:
    #                 order._create_analytic_account()

    #     return True
    
    # def action_confirm(self):
        
    #     self.document_type = 'sale_confirmation'
        
    #     if self._get_forbidden_state_confirm() & set(self.mapped('state')):
    #         raise UserError(_(
    #             'It is not allowed to confirm an order in the following states: %s'
    #         ) % (', '.join(self._get_forbidden_state_confirm())))

    #     for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
    #         order.message_subscribe([order.partner_id.id])
    #     self.write(self._prepare_confirmation_values())

    #     # Context key 'default_name' is sometimes propagated up to here.
    #     # We don't need it and it creates issues in the creation of linked records.
    #     context = self._context.copy()
    #     context.pop('default_name', None)

    #     self.with_context(context)._action_confirm()
    #     if self.env.user.has_group('sale.group_auto_done_setting'):
    #         self.action_done()
    #     return True
    
    def action_done(self):
        for order in self:
            tx = order.sudo().transaction_ids.get_last_transaction()
            if tx and tx.state == 'pending' and tx.acquirer_id.provider == 'transfer':
                tx._set_transaction_done()
                tx.write({'is_processed': True})
        return self.write({'state': 'done'})
    
    def get_list_line(self):
        wjk = self.order_line
        res = []
        for line in wjk:
            res.append({    
                "product_id": line.product_id.name,
                "product_id": line.product_id.name,
                "material_finish_id": line.material_finish_id.name,
                "finish_id" : line.finish_id.name,
                "sku" : line.sku,
                "name" : line.name,
                "request_date": line.request_date,
                # "sku_id" : line.sku_id.name,
                "no_po" : line.no_po,
                "cont_load" : line.cont_load,
                "cust_ref" : line.cust_ref,
                'no_po_cust' : line.no_po_cust,
                "product_uom_qty": line.product_uom_qty,
                "product_uom" : line.product_uom.name,
                "price_unit": line.price_unit,
                "price_subtotal": line.price_subtotal,
                # "product_packaging": line.product_packaging.name
                "product_packaging": line.product_packaging.name,
                # "material_finishing": line.material_finishing,
                "fabric_colour_id": line.fabric_colour_id.name,
                })
        return res

    def get_order_list(self):
        order_line = self.order_line
        order = order_line.search([],limit=1)
        return order

    def get_order_list_sc(self):
        self.ensure_one()
        order_line = self.order_line
        order = order_line.search([],limit=1)
        return order

   
    # def action_view_delivery(self):
    #     '''
    #     This function returns an action that displays existing delivery orders
    #     of given sales order ids. It can either be in a list or in a form
    #     view, if there is only one delivery order to show.
    #     '''
    #     if self.is_revisi:
    #         return self.action_view_delivery_revisi()
        
    #     action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")

    #     pickings = self.mapped('picking_ids')
    #     if len(pickings) > 1:
    #         action['domain'] = [('id', 'in', pickings.ids)]
    #     elif pickings:
    #         form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
    #         if 'views' in action:
    #             action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
    #         else:
    #             action['views'] = form_view
    #         action['res_id'] = pickings.id
    #     # Prepare the context.
    #     picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
    #     if picking_id:
    #         picking_id = picking_id[0]
    #     else:
    #         picking_id = pickings[0]
    #     action['context'] = dict(self._context, default_partner_id=self.partner_id.id, default_picking_type_id=picking_id.picking_type_id.id, default_origin=self.name, default_group_id=picking_id.group_id.id)
    #     return action

    # def action_view_delivery_revisi(self):
    #     '''
    #     This function returns an action that displays existing delivery orders
    #     of given sales order ids in their original state.
    #     '''
    #     action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        
    #     pickings = self.mapped('picking_ids')
    #     if len(pickings) > 1:
    #         action['domain'] = [('id', 'in', pickings.ids)]
    #     elif pickings:
    #         form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
    #         if 'views' in action:
    #             action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
    #         else:
    #             action['views'] = form_view
    #         action['res_id'] = pickings.id
    #     # Prepare the context.
    #     picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
    #     if picking_id:
    #         picking_id = picking_id[0]
    #     else:
    #         picking_id = pickings[0]
    #     action['context'] = dict(self._context, default_partner_id=self.partner_id.id, default_picking_type_id=picking_id.picking_type_id.id, default_origin=self.name, default_group_id=picking_id.group_id.id)
    #     return action


    

    # def action_draft(self):
    #     orders = self.filtered(lambda s: s.state in ['cancel', 'sent'])
    #     return orders.write({
    #         'state_is_so': 'draft',
    #         'signature': False,
    #         'signed_by': False,
    #         'signed_on': False,
    #     })
                
class JidokaSaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"



    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = {
            'ref': order.client_order_ref,
            'move_type': 'out_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,
            'fiscal_position_id': (order.fiscal_position_id or order.fiscal_position_id.get_fiscal_position(order.partner_id.id)).id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_reference': order.reference,
            'invoice_payment_term_id': order.payment_term_id.id,
            'partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
            'team_id': order.team_id.id,
            'campaign_id': order.campaign_id.id,
            'medium_id': order.medium_id.id,
            'source_id': order.source_id.id,
            'name' : order.origin,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,
                'tax_ids': [(6, 0, so_line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }

        return invoice_vals
    

    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    spec_design_id = fields.Many2one('spec.design', string='Spec Design')
    attachment = fields.Binary('Design Image',related='spec_design_id.attachment')
    assembly_size = fields.Char('Assembly Size')
    name = fields.Text('Description', 
        compute='_compute_name', readonly=False,store=True )
    
    material_finishing = fields.Char('Material Finishing')
    # material_finish_id = fields.Many2many('design.material', string='Material')
    material_finish_id = fields.Many2one('design.material', string='Material')
    wood = fields.Float('Wood')
    wood_price = fields.Float('Wood Price')
    labour = fields.Float('Labour')
    wood_15 = fields.Float('15%',compute='_compute_wood_15')
    paint = fields.Float('Paint',compute='_compute_paint')
    packing = fields.Float('Packing')
    hard = fields.Float('Hard',compute='_compute_hard')
    hd_35 = fields.Float('35%',compute='_compute_hd_35')
    spesial_hardware = fields.Float('SP HDR',compute='_compute_spesial_hardware')
    canvas = fields.Float('Cushion / Canvas')
    canvas_15 = fields.Float('15%',compute='_compute_canvas_15')
    load = fields.Float('Load',compute='_compute_load')
    total_cost = fields.Float('Total Cost',compute='_compute_total_cost')
    total_wood_price = fields.Float('Total Wood Price',compute='_compute_total_wood_price')
    total_margin_price = fields.Float('Total Margin Price',compute='_compute_total_margin_price')
    total_net_price = fields.Float('Total Net Price')
    total_set_price = fields.Float('Total Set Price')
    william_fob_price = fields.Float('Single Price')
    william_set_price = fields.Float('Set Price')
    packing_size_p = fields.Float('Packing Size P')
    packing_size_l = fields.Float('Packing Size L')
    packing_size_t = fields.Float('Packing Size T')
    qty_carton = fields.Float('Qty / CTN')
    cu_ft = fields.Float('CU FT')
    inch_40 = fields.Float("40' (PCS)")
    inch_40_hq = fields.Float("40' HQ (PCS)")
    fabric_colour_id = fields.Many2one('res.fabric.colour', string='Fabric Colour')    
    # no_po_cust = fields.Char("No PO Customer")
    cust_ref = fields.Char('Cust Reference')
    no_po_cust = fields.Char('Cust Ref', store=True)
    packaging_id = fields.Many2one('product.packaging', string='Packaging')
    moq = fields.Integer('MOQ')
    name_item = fields.Char('Name')

    # nopo = fields.Char('nopo', store=True,compute='_compute_no_po')

    # @api.depends('order_id.name')
    # def _compute_no_po(self):
    #     for line in self:
    #         if line.order_id.name:
    #             line.nopo = line.order_id.name
    #         else:
    #             line.nopo = False
    
    # @api.depends('product_id.name','material_finishing','fabric_colour_id.name','finish_id.name')
    @api.depends('material_finish_id','fabric_colour_id.name','finish_id.name','name_item')
    def _compute_name(self):
        material = self.material_finish_id.name
        for r in self:
            # product = r.product_id.name
            # sku = r.sku_id.name
            # sku = r.sku
            # cust_ref = r.cust_ref
            # product_qty = r.product_uom_qty
            # product_uom = r.product_uom.name
            fabric_colour = r.fabric_colour_id.name
            # material = r.material_finishing
            finish = r.finish_id.name
            name_item = r.name_item

            # if product == False:
            #     product = ''
            if fabric_colour == False:
                fabric_colour = ''
            if material == False:
                material = ''
            if finish == False:
                finish = ''
            if name_item == False:
                name_item = ''
            # if sku == False:
            #     sku = ''
            # if product_qty == False:
            #     product_qty = '-'
            # r.name = "%s %s %s %s %s" %(product,material, finish, sku, fabric_colour)
            # self.name = "%s \n%s %s \n%s" %(product,material, finish,fabric_colour)
            self.name = "%s \n%s %s \n%s" %(name_item,material, finish,fabric_colour)






    @api.onchange('william_fob_price','william_set_price')
    def onchange_price_unit(self):
        for line in self:
            line.price_unit = line.william_fob_price + line.william_set_price

    
    @api.depends('wood_price','labour')
    def _compute_wood_15(self):
        for rec in self:
            rec.wood_15 = round((rec.wood_price * 1.15) +(rec.labour * 1.15),2)
    
    @api.depends('wood')
    def _compute_paint(self):
        for rec in self:
            rec.paint = round((rec.wood * 90),2)

    @api.depends('wood')
    def _compute_hard(self):
        for rec in self:
            rec.hard = round((rec.wood * 75),2)

    @api.depends('paint','packing','hard')
    def _compute_hd_35(self):
        for rec in self:
            rec.hd_35 = round((rec.paint * 1.35) + ((rec.packing+rec.hard) * 1.35),2)

    # @api.depends('wood')
    def _compute_spesial_hardware(self):
        for rec in self:
            rec.spesial_hardware = round((90 * 1.5),2)

    @api.depends('spesial_hardware','canvas')
    def _compute_canvas_15(self):
        for rec in self:
            rec.canvas_15 = round((rec.spesial_hardware + rec.canvas) * 1.15 ,2)

    @api.depends('inch_40')
    def _compute_load(self):
        for rec in self:
            res = 0.00
            if rec.inch_40 > 0:
                res = round(550 / rec.inch_40,2)
            rec.load = res
    
    @api.depends('wood_15','hd_35','canvas_15','load')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.wood_15 + rec.hd_35 + rec.canvas_15 + rec.load

    @api.depends('total_net_price','canvas_15','wood')
    def _compute_total_wood_price(self):
        for rec in self:
            res = 0.00
            if rec.wood > 0:
                res = round((rec.total_net_price - rec.canvas_15) / rec.wood,2)
            rec.total_wood_price = res
    
    @api.depends('total_net_price','total_cost')
    def _compute_total_margin_price(self):
        for rec in self:
            res = 0.00
            if rec.total_net_price > 0:
                res = round(((rec.total_net_price - rec.total_cost) / rec.total_net_price) * 100,2)
            rec.total_margin_price = res
            
    


    # def get_list_line(self):
    #     wjk = self
    #     res = []
    #     for line in wjk:
    #         res.append({
    #             "product_id": line.product_id.name,
    #             "finish_id" : line.finish_id.name,
    #             "name" : line.name,
    #             "sku_id" : line.sku_id.name,
    #             "no_po" : line.no_po,
    #             "product_uom_qty": line.product_uom_qty,
    #             "product_uom" : line.product_uom.name,
    #             "price_unit": line.price_unit,
    #             "price_subtotal": line.price_subtotal,
    #             "product_packaging": line.product_packaging.name
    #             })
    #     return res

    # def get_order_list(self):
    #     order = self.search([],limit=1)
    #     return order
    