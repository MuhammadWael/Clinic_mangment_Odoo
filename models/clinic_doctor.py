from odoo import models,fields,api
from odoo.exceptions import UserError,ValidationError
from datetime import timedelta,datetime

class ClinicDoctor(models.Model):
    _inherit = "res.users"

    specialty = fields.Selection(
        string="Specialty", 
        selection=[
            ('general_practitioner', 'General Practitioner'),
            ('pediatrician', 'Pediatrician'),
            ('cardiologist', 'Cardiologist'),
            ('dermatologist', 'Dermatologist'),
            ('gynecologist', 'Gynecologist'),
            ('neurologist', 'Neurologist'),
            ('orthopedist', 'Orthopedist'),
            ('psychiatrist', 'Psychiatrist'),
            ('radiologist', 'Radiologist'),
            ('urologist', 'Urologist'),
        ])
    is_doctor = fields.Boolean(string="is Doctor?", default=False)
    availability = fields.One2many("clinic.availability","doctor_id",string="Availability") 
    appointment_id = fields.One2many("clinic.appointment","doctor_id",string="Appointments")
    upcoming_appointments = fields.One2many(
    comodel_name="clinic.appointment",
    compute="_compute_upcoming_appointments",
    string="Upcoming Appointments"
    )

    @api.model
    def create(self,vals):
        doctor = super().create(vals)
        if doctor.is_doctor and not doctor.specialty:
            raise UserError("Please select a specialty for the doctor")
        return doctor
    

    @api.depends('appointment_id')
    def _compute_upcoming_appointments(self):
        for record in self:
            upcoming_appointments = self.env['clinic.appointment'].search([
                ('doctor_id', '=', record.id),
                ('appointment', '>=', fields.Datetime.now()),
                ('status', 'in', ['confirmed', 'pending'])
            ])
            record.upcoming_appointments = upcoming_appointments
            