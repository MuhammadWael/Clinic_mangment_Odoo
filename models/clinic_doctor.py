from odoo import models,fields,api

class ClinicDoctor(models.Model):
    _inherit = "res.users"

    appointment_id = fields.One2many("clinic.appointment","doctor_id",string="Appointments")
    specialty = fields.Text(string="Specialty", required=True)
    availability = fields.Selection(
        compute="_compute_avalability",
        selection=[
            ('available','Available'),
            ('unavailable','Unavailable')
        ]) 

    @api.depends('appointment_id')
    def _compute_avalability(self):
        for record in self:
            unavailable = self.env['clinic.appointment'].search([
                ('doctor_id', '=', record.id),
                ('status', 'in', ['confirmed', 'pending'])
            ])
            if unavailable:
                record.availability = 'unavailable'
            else:
                record.availability = 'available'
