from odoo import models, fields


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s' % (rec.scrap_location_id.name)))
            return result

class ScrapLocation(models.Model):
    _inherit = 'stock.location'

    scrap_id = fields.Many2one('stock.scrap',string="Scrap Location")


