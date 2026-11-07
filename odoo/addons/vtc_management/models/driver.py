from odoo import api, fields, models


class VtcDriver(models.Model):
    _name = 'vtc.driver'
    _description = 'Chauffeur'
    _inherit = ['mail.thread']

    name = fields.Char('Nom', required=True, tracking=True)
    phone = fields.Char('Téléphone')
    email = fields.Char('Email')
    image = fields.Image('Photo', max_width=256, max_height=256)
    license_number = fields.Char('N° permis')
    license_expiry = fields.Date('Expiration permis')
    vehicle_ids = fields.One2many('vtc.vehicle', 'driver_id', 'Véhicules')
    state = fields.Selection([
        ('online', 'En ligne'),
        ('offline', 'Hors ligne'),
        ('suspended', 'Suspendu'),
    ], default='offline', string='Statut', tracking=True)
    commission_rate = fields.Float('Commission plateforme (%)', default=20.0)
    ride_ids = fields.One2many('vtc.ride', 'driver_id', 'Courses')
    ride_count = fields.Integer(compute='_compute_stats', string='Nb courses')
    total_revenue = fields.Float(compute='_compute_stats', string='CA total')
    driver_earnings = fields.Float(compute='_compute_stats', string='Gains chauffeur')
    rating = fields.Float(compute='_compute_stats', string='Note moyenne', digits=(2, 1))

    @api.depends('ride_ids.state', 'ride_ids.price', 'ride_ids.rating', 'commission_rate')
    def _compute_stats(self):
        for d in self:
            done = d.ride_ids.filtered(lambda r: r.state == 'done')
            rated = done.filtered(lambda r: r.rating)
            d.ride_count = len(done)
            d.total_revenue = sum(done.mapped('price'))
            d.driver_earnings = d.total_revenue * (1 - d.commission_rate / 100)
            d.rating = sum(int(r.rating) for r in rated) / len(rated) if rated else 0.0

    def action_go_online(self):
        self.write({'state': 'online'})

    def action_go_offline(self):
        self.write({'state': 'offline'})
