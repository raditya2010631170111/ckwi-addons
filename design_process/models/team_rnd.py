from odoo import api, fields, models, _
import logging
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class TeamsRnd(models.Model):
    _name = 'team.rnd'
    _description = 'Team RnD'
    _inherit = ['mail.thread']


    name = fields.Char("Teams Name")
    email = fields.Char("Teams Email")
    team_leader_id = fields.Many2one("res.users", "Teams Leader")
    company_id = fields.Many2one("res.company","Company", default=lambda self: self.env.user.company_id.id)
    member_line = fields.One2many("res.users","team_rnd_id","Member RnD")



class TeamsUserRnd(models.Model):
    _inherit = 'res.users'
    _description = 'Team User RnD'


    team_rnd_id = fields.Many2one('team.rnd',"RND")