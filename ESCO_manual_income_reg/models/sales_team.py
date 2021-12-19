from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CrmTeam(models.Model) :
	_inherit = 'crm.team'


	analytic_account_id = fields.Many2one('account.analytic.account','Analytic Account')

	