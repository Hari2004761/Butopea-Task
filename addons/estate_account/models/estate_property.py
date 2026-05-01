from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    invoice_ids = fields.One2many('account.move', 'property_id', string='Invoices')
    invoice_count = fields.Integer(compute='_compute_invoice_count')

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for prop in self:
            prop.invoice_count = len(prop.invoice_ids)

    def action_sold(self):
        for prop in self:
            if prop.state == 'sold':
                raise UserError(_('"%s" is already sold.') % prop.name)
            if prop.invoice_ids:
                raise UserError(_('"%s" already has invoices linked to it.') % prop.name)

        res = super().action_sold()
        for prop in self:
            if not prop.buyer_id:
                raise UserError(_('Cannot invoice: no buyer set on "%s".') % prop.name)

            journal = self.env['account.journal'].search(
                [('type', '=', 'sale'), ('company_id', '=', self.env.company.id)],
                limit=1,
            )
            if not journal:
                raise UserError(_('No sales journal found for company "%s".') % self.env.company.name)

            self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': prop.buyer_id.id,
                'journal_id': journal.id,
                'property_id': prop.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'name': _('6%% commission on sale of %s') % prop.name,
                        'quantity': 1,
                        'price_unit': prop.selling_price * 0.06,
                    }),
                    (0, 0, {
                        'name': _('Administrative fees'),
                        'quantity': 1,
                        'price_unit': 100.00,
                    }),
                ],
            })
        return res

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoices'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
            'context': {'default_move_type': 'out_invoice'},
        }
