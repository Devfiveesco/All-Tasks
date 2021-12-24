# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import date

def _numOfDays(date1, date2):
    return (date2-date1).days

class HrLeave(models.Model):
    _inherit = 'hr.leave'
    
    state = fields.Selection(selection_add=[('reject', 'Rejected')])
    allawnce_day = fields.Float(string="Days Due")
    leave_approvals = fields.One2many('leave.validation.status',
                                      'holiday_status',
                                      string='Leave Validators',
                                      track_visibility='always',
                                      help="Leave approvals")
    multi_level_validation = fields.Boolean(
        string='Multiple Level Approval',
        related='holiday_status_id.multi_level_validation',
        help="If checked then multi-level approval is necessary")

    # Calculated fields
    date_hired = fields.Date()
    today_date = fields.Date('Admission Date', default=date.today())
    between_date = fields.Float()
    months = fields.Float()
    years = fields.Float()

    @api.onchange('employee_id')
    def get_allawonce_days(self):
        for rec in self:
            contract = self.env['hr.contract.history'].search([('employee_id','=',rec.employee_id.id)])
            if not contract:
                pass
                raise ValidationError(_('This employee has no holidays.'))
            if contract:
               for c in contract:
                    year = 0.0
                    rec.date_hired = c.date_hired
                    rec.between_date = _numOfDays(rec.date_hired, rec.today_date)
                    rec.months = rec.between_date / 12
                    rec.years = rec.months / 12
                    year = rec.years
                    if year < 5:
                        rec.allawnce_day = 21
                    if year >= 5 and year <=10:
                        rec.allawnce_day = 23
                    if year >= 11 and year <=15:
                        rec.allawnce_day = 25
                    if year >= 16 and year <=20:
                        rec.allawnce_day = 28
                    if year >= 21 and year <=25:
                        rec.allawnce_day = 31
                    if year >= 26 and year <=30:
                        rec.allawnce_day = 34


    def action_reject(self):
        for rec in self:
            rec.state = 'reject'


    def action_view_employee(self):
        for rec in self:
            maint = self.env['hr.employee'].search([('department_id','=',rec.department_id.id)])
            action = self.env.ref('hr.open_view_employee_list_my').read()[0]
            if len(maint) > 1:
                action['domain'] = [('id', 'in', maint.ids)]
            # action['views'] = [(self.env.ref('hr.view_employee_form').id, 'form')]
            # action['domain'] = [('id', 'in', maint.ids)]
            # action = {'type': 'ir.actions.act_window_close'}
            return action

    def action_approve(self):
        """ Check if any pending tasks is added if so reassign the pending
        task else call approval """
        # if leave_validation_type == 'both':
        # this method is the first approval approval
        # if leave_validation_type != 'both': t
        # his method calls action_validate() below
        if any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_(
                'Leave request must be confirmed ("To Approve")'
                ' in order to approve it.'))

        ohrmspro_vacation_project = self.sudo().env['ir.module.module'].search(
            [('name', '=', 'ohrmspro_vacation_project')],
            limit=1).state

        if ohrmspro_vacation_project == 'installed':
            return self.env['hr.leave'].check_pending_task(self)
        else:
            return self.approval_check()

    def approval_check(self):
        """ Check all leave validators approved the leave request if approved
         change the current request stage to Approved"""

        current_employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

        active_id = self.env.context.get('active_id') if self.env.context.get(
            'active_id') else self.id

        user = self.env['hr.leave'].search([('id', '=', active_id)], limit=1)
        for user_obj in user.leave_approvals.mapped(
                'validating_users').filtered(lambda l: l.id == self.env.uid):
            validation_obj = user.leave_approvals.search(
                [('holiday_status', '=', user.id),
                 ('validating_users', '=', self.env.uid)])
            validation_obj.validation_status = True
        approval_flag = True
        for user_obj in user.leave_approvals:
            if not user_obj.validation_status:
                approval_flag = False
        if approval_flag:
            user.filtered(
                lambda hol: hol.validation_type == 'both').sudo().write(
                {'state': 'validate1',
                 'first_approver_id': current_employee.id})
            user.filtered(
                lambda hol:
                not hol.validation_type == 'both').sudo().action_validate()
            if not user.env.context.get('leave_fast_create'):
                user.activity_update()
            return True
        else:
            return False

    def action_refuse(self):
        """ Refuse the leave request if the current user is in
        validators list """
        current_employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

        approval_access = False
        for user in self.leave_approvals:
            if user.validating_users.id == self.env.uid:
                approval_access = True
        if approval_access:
            for holiday in self:
                if holiday.state not in ['confirm', 'validate', 'validate1']:
                    raise UserError(_(
                        'Leave request must be confirmed '
                        'or validated in order to refuse it.'))

                if holiday.state == 'validate1':
                    holiday.sudo().write(
                        {'state': 'refuse',
                         'first_approver_id': current_employee.id})
                else:
                    holiday.sudo().write(
                        {'state': 'refuse',
                         'second_approver_id': current_employee.id})
                # Delete the meeting
                if holiday.meeting_id:
                    holiday.meeting_id.unlink()
                # If a category that created several holidays,
                # cancel all related
                holiday.linked_request_ids.action_refuse()
            self._remove_resource_leave()
            self.activity_update()
            validation_obj = self.leave_approvals.search(
                [('holiday_status', '=', self.id),
                 ('validating_users', '=', self.env.uid)])
            validation_obj.validation_status = False
            return True
        else:
            for holiday in self:
                if holiday.state not in ['confirm', 'validate', 'validate1']:
                    raise UserError(_(
                        'Leave request must be confirmed '
                        'or validated in order to refuse it.'))

                if holiday.state == 'validate1':
                    holiday.write({'state': 'refuse',
                                   'first_approver_id': current_employee.id})
                else:
                    holiday.write({'state': 'refuse',
                                   'second_approver_id': current_employee.id})
                # Delete the meeting
                if holiday.meeting_id:
                    holiday.meeting_id.unlink()
                # If a category that created several holidays,
                # cancel all related
                holiday.linked_request_ids.action_refuse()
            self._remove_resource_leave()
            self.activity_update()
            return True

    def action_draft(self):
        """ Reset all validation status to false when leave request
        set to draft stage"""
        for user in self.leave_approvals:
            user.validation_status = False
        return super(HrLeave, self).action_draft()

    @api.onchange('holiday_status_id')
    def add_validators(self):
        """ Update the tree view and add new validators
        when leave type is changed in leave request form """
        li = []
        self.leave_approvals = [(5, 0, 0)]
        li2 = []
        for user in self.leave_approvals:
            li2.append(user.validating_users.id)
        for user in self.holiday_status_id.leave_validators.filtered(
                lambda l: l.holiday_validators.id not in li2):
            li.append((0, 0, {
                'validating_users': user.holiday_validators.id,
            }))
        self.leave_approvals = li

    def _get_approval_requests(self):
        """ Action for Approvals menu item to show approval
        requests assigned to current user """

        current_uid = self.env.uid
        hr_holidays = self.env['hr.leave'].search([('state', '=', 'confirm')])
        li = []
        if not hr_holidays:
            pass
        for req in hr_holidays:
            for user in req.leave_approvals.filtered(
                    lambda l: l.validating_users.id == current_uid):
                li.append(req.id)
        value = {
            'domain': str([('id', 'in', li)]),
            'view_mode': 'tree,form',
            'res_model': 'hr.leave',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'name': _('Approvals'),
            'res_id': self.id,
            'target': 'current',
            'create': False,
            'edit': False,
        }
        return value


class HrLeaveTypes(models.Model):
    """ Extend model to add multilevel approval """
    _inherit = 'hr.leave.type'

    multi_level_validation = fields.Boolean(
        string='Multiple Level Approval',
        help="If checked then multi-level approval is necessary")
    leave_validation_type = fields.Selection(
        selection_add=[('multi', 'Multi Level Approval')])
    leave_validators = fields.One2many('hr.holidays.validators',
                                       'hr_holiday_status',
                                       string='Leave Validators',
                                       help="Leave validators")

    @api.onchange('leave_validation_type')
    def enable_multi_level_validation(self):
        """ Enabling the boolean field of multilevel validation"""
        self.multi_level_validation = True if (
                self.leave_validation_type == 'multi') else False


class HrLeaveValidators(models.Model):
    """ Model for leave validators in Leave Types configuration """
    _name = 'hr.holidays.validators'

    hr_holiday_status = fields.Many2one('hr.leave.type')

    holiday_validators = fields.Many2one('res.users',
                                         string='Leave Validators',
                                         help="Leave validators",
                                         domain="[('share','=',False)]")


class LeaveValidationStatus(models.Model):
    """ Model for leave validators and their status for each leave request """
    _name = 'leave.validation.status'

    holiday_status = fields.Many2one('hr.leave')

    validating_users = fields.Many2one('res.users', string='Leave Validators',
                                       help="Leave validators",
                                       domain="[('share','=',False)]")

    validation_status = fields.Boolean(string='Approve Status', readonly=True,
                                       default=False,
                                       track_visibility='always', help="Status")
    leave_comments = fields.Text(string='Comments', help="Comments")

    @api.onchange('validating_users')
    def prevent_change(self):
        """ Prevent Changing leave validators from leave request form """
        raise UserError(_(
            "Changing leave validators is not permitted. You can only change "
            "it from Leave Types Configuration"))
