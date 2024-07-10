from odoo import models,fields,api
from datetime import timedelta,datetime

class ClinicDoctor(models.Model):
    _inherit = "res.users"

    specialty = fields.Selection(
        string="Specialty", 
        required=True,
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
    availability = fields.One2many("clinic.availability","doctor_id",string="Availability") 
    appointment_id = fields.One2many("clinic.appointment","doctor_id",string="Appointments")
    upcoming_appointments = fields.One2many(
    comodel_name="clinic.appointment",
    compute="_compute_upcoming_appointments",
    string="Upcoming Appointments"
    )

    
    @api.depends('appointment_id')
    def _compute_upcoming_appointments(self):
        for record in self:
            upcoming_appointments = self.env['clinic.appointment'].search([
                ('doctor_id', '=', record.id),
                ('appointment', '>=', fields.Datetime.now()),
                ('status', 'in', ['confirmed', 'pending'])
            ])
            record.upcoming_appointments = upcoming_appointments
    
    @api.onchange('availability')
    def _make_appointments(self):
        day_mapping = {
            'sat': 5,
            'sun': 6,
            'mon': 0,
            'tues': 1,
            'wed': 2,
            'thurs': 3,
            'fri': 4
        }
        for record in self:
            for availability in record.availability:
                current_date = datetime.now()
                end_date = current_date + timedelta(weeks=4)
                
                while current_date <= end_date:
                    if current_date.weekday() == day_mapping.get(availability.week_day.strip().lower()):
                        start_time = availability.start_time
                        end_time = availability.end_time
                        while start_time < end_time:
                            appointment_datetime = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=start_time)
                            self.env['clinic.appointment'].create({
                                'doctor_id': record._origin.id, #because onchange make new (temp) values and we need to use original ones 
                                'appointment': appointment_datetime,
                                'status': 'available'
                            })
                            start_time += 0.25
                    current_date += timedelta(days=1)
