from odoo import fields, models, api
from datetime import date

class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    description_for_offer = fields.Html(string="Description")
    tag = fields.Selection([('emp','Emp'),('inv','Invoice'),
                            ('sales','Sales'),('inven','Inventory'),
                            ('pur','Purchase'),('py','Pyroll')])

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
     
    qu_date = fields.Date(
                       default=date.today())
    amount_to_text = fields.Char(compute="amount_text") 

    def amount_text(self):
        self.amount_to_text = self.currency_id.amount_to_text(self.amount_total)

