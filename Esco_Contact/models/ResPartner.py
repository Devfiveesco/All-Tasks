
from odoo import fields, models, api


class ContactInheritForm(models.Model):
    _inherit = 'res.partner'

    reg_status = fields.Selection([('draft','NA'),('waiting','Under Checking'),('approve','Approved'),
                              ('reject','Rejected')],default='draft', string="Reg Status")

    def action_waiting(self):
        for rec in self:
            self.reg_status = 'waiting'

    def action_approve(self):
        for rec in self:
            self.reg_status = 'approve'

    def action_reject(self):
        for rec in self:
            self.reg_status = 'reject'

    def action_set_to_draft(self):
        for rec in self:
            self.reg_status = 'draft'

