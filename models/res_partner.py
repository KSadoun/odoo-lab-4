from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    related_patient_id = fields.Many2one(
        'hms.patient',
        string='Related Patient'
    )

    vat = fields.Char(required=True)

    @api.constrains('related_patient_id', 'email')
    def _check_patient_email(self):
        for partner in self:
            if not partner.related_patient_id:
                continue

            patient_email = partner.related_patient_id.email

            customers = self.search([
                ('id', '!=', partner.id),
                ('email', '=', patient_email)
            ])

            if customers:
                raise ValidationError(
                    _("This patient email is already assigned to another customer.")
                )

    def unlink(self):
        for partner in self:
            if partner.related_patient_id:
                raise ValidationError(
                    _("You cannot delete a customer linked to a patient.")
                )

        return super().unlink()