from odoo import api, fields, models


class VtcClient(models.Model):
    _name = 'vtc.client'
    _description = 'Client'
    _inherit = ['mail.thread']

    name = fields.Char('Nom', required=True)
    phone = fields.Char('Téléphone', required=True)
    email = fields.Char('Email')
    image = fields.Image('Photo', max_width=256, max_height=256)
    favorite_address = fields.Char('Adresse favorite')
    ride_ids = fields.One2many('vtc.ride', 'client_id', 'Courses')
    ride_count = fields.Integer(compute='_compute_stats', string='Nb courses')
    total_spent = fields.Float(compute='_compute_stats', string='Total dépensé')

    _sql_constraints = [
        ('phone_unique', 'unique(phone)', 'Ce numéro est déjà utilisé.'),
    ]

    @api.depends('ride_ids.state', 'ride_ids.price')
    def _compute_stats(self):
        for c in self:
            done = c.ride_ids.filtered(lambda r: r.state == 'done')
            c.ride_count = len(done)
            c.total_spent = sum(done.mapped('price'))
