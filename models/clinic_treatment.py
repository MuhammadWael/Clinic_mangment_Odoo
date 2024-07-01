from odoo import models,fields,api
from odoo.exceptions import ValidationError,UserError

class ClinicAppointment(models.Model):
    _name = "clinic.treatment"

    patient_id = fields.Many2one("res.partner",string="Patient")
    doctor_id = fields.Many2one("res.users",string="Doctor")
    appointment_id = fields.Many2one("clinc.appointment",string="Appointment")
    appointment_type = fields.Selection([
        ('diagnosis','Diagnosis'),
        ('prescribed_medications','Prescribed Medications'),
        ('procedures','Procedures')
    ])

    notes = fields.Text(string="Add notes")
