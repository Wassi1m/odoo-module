from odoo import api, fields, models


class VtcVehicle(models.Model):
    _name = 'vtc.vehicle'
    _description = 'Véhicule'
    _inherit = ['mail.thread']
    _rec_name = 'display_label'

    plate = fields.Char('Immatriculation', required=True, tracking=True)
    brand = fields.Char('Marque', required=True)
    model = fields.Char('Modèle', required=True)
    year = fields.Integer('Année')
    color = fields.Char('Couleur')
    image = fields.Image('Photo', max_width=512, max_height=512)
    category_id = fields.Many2one('vtc.category', 'Catégorie', required=True)
    driver_id = fields.Many2one('vtc.driver', 'Chauffeur', tracking=True)
    state = fields.Selection([
        ('available', 'Disponible'),
        ('on_ride', 'En course'),
        ('maintenance', 'Maintenance'),
    ], default='available', string='Statut', tracking=True)
    ride_ids = fields.One2many('vtc.ride', 'vehicle_id', 'Courses')
    ride_count = fields.Integer(compute='_compute_ride_count')
    display_label = fields.Char(compute='_compute_display_label', store=True)

    _sql_constraints = [
        ('plate_unique', 'unique(plate)', "L'immatriculation doit être unique."),
    ]

    @api.depends('brand', 'model', 'plate')
    def _compute_display_label(self):
        for v in self:
            v.display_label = f"{v.brand or ''} {v.model or ''} [{v.plate or ''}]"

    def _compute_ride_count(self):
        for v in self:
            v.ride_count = len(v.ride_ids)
