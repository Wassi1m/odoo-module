from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class VtcRide(models.Model):
    _name = 'vtc.ride'
    _description = 'Course'
    _inherit = ['mail.thread']
    _order = 'request_date desc'

    name = fields.Char('Référence', default='Nouveau', readonly=True, copy=False)
    client_id = fields.Many2one('vtc.client', 'Client', required=True, tracking=True)
    category_id = fields.Many2one('vtc.category', 'Catégorie', required=True)
    driver_id = fields.Many2one('vtc.driver', 'Chauffeur', tracking=True,
                                domain="[('state', '=', 'online')]")
    vehicle_id = fields.Many2one('vtc.vehicle', 'Véhicule',
                                 domain="[('driver_id', '=', driver_id), ('category_id', '=', category_id)]")
    pickup = fields.Char('Départ', required=True)
    destination = fields.Char('Destination', required=True)
    distance_km = fields.Float('Distance (km)')
    duration_min = fields.Float('Durée (min)')
    request_date = fields.Datetime('Demandée le', default=fields.Datetime.now)
    start_date = fields.Datetime('Début', readonly=True)
    end_date = fields.Datetime('Fin', readonly=True)
    price = fields.Float('Prix (TND)', compute='_compute_price', store=True)
    payment_method = fields.Selection([
        ('cash', 'Espèces'), ('card', 'Carte'), ('wallet', 'Portefeuille'),
    ], default='cash', string='Paiement')
    rating = fields.Selection([(str(i), str(i)) for i in range(1, 6)], 'Note client')
    state = fields.Selection([
        ('requested', 'Demandée'),
        ('accepted', 'Acceptée'),
        ('in_progress', 'En cours'),
        ('done', 'Terminée'),
        ('cancelled', 'Annulée'),
    ], default='requested', string='Statut', tracking=True, group_expand='_expand_states')

    @api.model
    def _expand_states(self, states, domain, order=None):
        return [key for key, _l in self._fields['state'].selection]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('vtc.ride') or 'Nouveau'
        return super().create(vals_list)

    @api.depends('category_id', 'distance_km', 'duration_min')
    def _compute_price(self):
        for r in self:
            c = r.category_id
            if not c:
                r.price = 0.0
                continue
            p = c.base_fare + r.distance_km * c.price_per_km + r.duration_min * c.price_per_min
            r.price = max(p, c.min_fare)

    @api.constrains('distance_km', 'duration_min')
    def _check_positive(self):
        for r in self:
            if r.distance_km < 0 or r.duration_min < 0:
                raise ValidationError(_('Distance et durée doivent être positives.'))

    @api.onchange('driver_id')
    def _onchange_driver(self):
        v = self.driver_id.vehicle_ids.filtered(
            lambda x: x.state == 'available' and x.category_id == self.category_id)
        self.vehicle_id = v[:1]

    # --- Workflow ---
    def action_accept(self):
        for r in self:
            if not r.driver_id or not r.vehicle_id:
                raise UserError(_('Choisissez un chauffeur et un véhicule.'))
            if r.vehicle_id.state != 'available':
                raise UserError(_("Le véhicule n'est pas disponible."))
            r.state = 'accepted'

    def action_start(self):
        for r in self:
            r.write({'state': 'in_progress', 'start_date': fields.Datetime.now()})
            r.vehicle_id.state = 'on_ride'

    def action_finish(self):
        for r in self:
            r.write({'state': 'done', 'end_date': fields.Datetime.now()})
            r.vehicle_id.state = 'available'

    def action_cancel(self):
        for r in self:
            if r.state == 'done':
                raise UserError(_("Impossible d'annuler une course terminée."))
            if r.vehicle_id.state == 'on_ride':
                r.vehicle_id.state = 'available'
            r.state = 'cancelled'
