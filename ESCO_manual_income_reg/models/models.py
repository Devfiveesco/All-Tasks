# -*- coding: utf-8 -*-

import base64

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class DeliveryCompanies(models.Model):
    _name = 'delivery.companies'

    partner_id = fields.Many2one('res.partner' , string='Company Name')
    no_of_orders = fields.Integer('Number of Orders')
    total_amount = fields.Float('Total Amount')
    income_reg_id = fields.Many2one('income.reg', string='Income Registration')




class IncomeReg(models.Model) :
    _name = 'income.reg'
    _rec_name = 'branch_id'

    branch_id = fields.Many2one('crm.team' , 'Branch Name', required=True)
    date = fields.Date('Date' , required=True)
    total_net_income = fields.Float('Total Net Income' , required=True)
    total_expense = fields.Float('Total Expense' , required=True)
    total_in_usd = fields.Float('Total In USD',required=True)
    delivery_companies_ids = fields.One2many('delivery.companies','income_reg_id', string='Delivery Companies')
    state = fields.Selection( [('draft','Draft') , ('posted','Posted')] ,default='draft')


    def post(self):
        for rec in self:
            self.create_invoice()
            rec.state = 'posted'

    def create_invoice(self):
        inv_obj = self.env['account.move'].search([])
        sales_delivery_product = self.env['product.product'].search([('name','=','Sales - Delivery')],limit=1)
        line = self.delivery_companies_ids
        for l in line:
            vals = {
                'partner_id': l.partner_id.id,
                'move_type': 'out_invoice',
                # 'invoice_origin': self.name,
                'invoice_date': self.date,
                'invoice_line_ids': [(0, 0, {
                    'name': "Sales - Delivery",
                    'product_id': sales_delivery_product.id,
                    'price_unit': l.total_amount})],
            }
            invoice = inv_obj.create(vals)
            return invoice