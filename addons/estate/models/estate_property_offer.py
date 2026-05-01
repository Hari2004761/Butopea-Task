from odoo import api, fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offer'
    _order = 'price desc'

    price = fields.Float(required=True)
    status = fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
        copy=False,
    )
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    property_type_id = fields.Many2one(
        related='property_id.property_type_id',
        store=True,
    )
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(
        compute='_compute_date_deadline',
        inverse='_inverse_date_deadline',
        store=True,
    )

    _sql_constraints = [
        ('check_offer_price', 'CHECK(price > 0)', 'The offer price must be strictly positive.'),
    ]

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.date_deadline = fields.Date.add(date, days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.validity = (offer.date_deadline - date).days

    def action_accept(self):
        for offer in self:
            if offer.property_id.state == 'canceled':
                raise UserError('Canceled properties cannot accept offers.')
            # Refuse all sibling offers first
            (offer.property_id.offer_ids - offer).write({'status': 'refused'})
            offer.property_id.selling_price = offer.price
            offer.property_id.buyer_id = offer.partner_id
            offer.property_id.state = 'offer_accepted'
            offer.status = 'accepted'
        return True

    def action_refuse(self):
        for offer in self:
            if offer.status == 'accepted':
                offer.property_id.selling_price = 0.0
                offer.property_id.buyer_id = False
                offer.property_id.state = 'offer_received'
            offer.status = 'refused'
        return True

    @api.model
    def create(self, vals):
        property_rec = self.env['estate.property'].browse(vals.get('property_id'))
        if vals.get('price', 0) < property_rec.best_price:
            raise UserError(
                f'The offer must be higher than {property_rec.best_price:.2f}.'
            )
        if property_rec.state == 'new':
            property_rec.state = 'offer_received'
        return super().create(vals)
