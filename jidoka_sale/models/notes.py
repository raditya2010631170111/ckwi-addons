from odoo import _, api, fields, models

#   <!-- ============JC-336============ -->

class ResNotesSale(models.Model):
    _name = 'res.notes.sale'
    # _rec_name = 'id'

    name = fields.Char(string="Note Name",  index=True,
        compute='_compute_name',store=True )
    
    @api.depends('customer_id','type_note')
    def _compute_name(self):
        type_note = []
        for r in self:
            
            if r.type_note == False:
                type_note = ''
            elif r.type_note == 'contract_review':
                type_note = 'Contract Review'
            elif r.type_note == 'manufacture_order':
                type_note = 'Manufacture Order'
            elif r.type_note == 'sale_confirmation':
                type_note = 'Sale Confirmation'
            else:
                type_note = ''
                
            if r.customer_id:
                customer_id = r.customer_id.display_name
            else:
                customer_id = ''
            r.name = '%s - %s'%(customer_id,type_note) 
    
    
    
    
    customer_id = fields.Many2one('res.partner', string='Customer')
    
    # type_note = fields.Selection([
    #     ('cr', 'Contract Review'),
    #     ('mo', 'Manufacture Order'),
    #     ('sc', 'Sale Confirmation'),
    # ], string='Type Note')
    
    type_note = fields.Selection([
        ('contract_review', 'Contract Review'),
        ('manufacture_order', 'Manufacture Order'),
        ('sale_confirmation', 'Sale Confirmation'),
    ], string='Type Note')
    
    information = fields.Html(
        string='Information',
    )
    info_teks = fields.Text('Information')
    
    

    def name_get(self):
        result = []
        for r in self:
            
            if r.type_note == False:
                type_note = ''
            elif r.type_note == 'contract_review':
                type_note = 'Contract Review'
            elif r.type_note == 'manufacture_order':
                type_note = 'Manufacture Order'
            elif r.type_note == 'sale_confirmation':
                type_note = 'Sale Confirmation'
            else:
                type_note = ''
                
            if r.customer_id:
                customer_id = r.customer_id.display_name
            else:
                customer_id = ''
            name = '%s - %s'%(customer_id,type_note) 
            result.append((r.id, name))
        return result
#   <!-- ============JC-336============ -->
