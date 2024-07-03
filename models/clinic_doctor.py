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
    upcoming_appointments = fields.One2many(
    comodel_name="clinic.appointment",
    compute="_compute_upcoming_appointments",
    string="Upcoming Appointments"
    )

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
        
    @api.depends('appointment_id')
    def _compute_upcoming_appointments(self):
        for record in self:
            upcoming_appointments = self.env['clinic.appointment'].search([
                ('doctor_id', '=', record.id),
                ('appointment', '>=', fields.Datetime.now()),
                ('status', 'in', ['confirmed', 'pending'])
            ])
            record.upcoming_appointments = upcoming_appointments