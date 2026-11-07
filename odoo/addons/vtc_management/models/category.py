from odoo import fields, models


class VtcCategory(models.Model):
    _name = 'vtc.category'
    _description = 'Catégorie de service'

    name = fields.Char('Nom', required=True)
    base_fare = fields.Float('Prise en charge (TND)', default=1.0)
    price_per_km = fields.Float('Prix / km', default=0.8)
    price_per_min = fields.Float('Prix / minute', default=0.1)
    min_fare = fields.Float('Tarif minimum', default=3.0)
    seats = fields.Integer('Places', default=4)
    active = fields.Boolean(default=True)
