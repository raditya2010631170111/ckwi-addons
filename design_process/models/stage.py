



from odoo import models, fields, api, _
from odoo.exceptions import UserError



class design_process_stage(models.Model):
    _name = 'design.process.stage'
    _rec_name = 'name'
    _order = "sequence,id"
    _description = 'Design Stage'

    sequence = fields.Integer('Sequence')
    name = fields.Char('Name')
    code = fields.Char('Code')
    active = fields.Boolean(default=True)





class CrmStage(models.Model):
    _inherit = 'crm.stage'
    _description = 'Crm Stage'



    code = fields.Char("Code")
