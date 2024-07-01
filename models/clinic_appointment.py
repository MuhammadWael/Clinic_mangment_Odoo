from odoo import models,fields,api
from odoo.exceptions import ValidationError,UserError

class ClinicAppointment(models.Model):
    _name = "clinic.appointment"

    patient_id = fields.Many2one("res.partner",string="Patient")
    doctor_id = fields.Many2one("res.users",string="Doctor")
    appointment = fields.Datetime(string="Appointment")
    appointment_type = fields.Selection([
        ('consultation','Consultation'),
        ('checkup','Checkup'),
        ('emergency','Emergency')
    ])
    status = fields.Selection([
        ('pending','Pending'),
        ('canceled', 'Canceled'),
        ('confirmed', 'Confirmed')
    ])
    notes = fields.Text(string="Add notes")

    @api.constrains
    def _check_conflict(self):
        for record in self:
            if record.status != 'canceled':
                overlapping_appointments = self.search([
                    ('doctor_id', '=', record.doctor_id.id),
                    ('appontment','=',record.appointment),
                    ('id', '!=', record.id),
                    ('status', '!=','canceled')
                ])
                if overlapping_appointments:
                    raise ValidationError("This appointment isn't available")