from odoo import models,fields

class ClinicLog(models.Model):
    _name = "clinic.log"

    patient_id = fields.Many2one("res.partner",string="Patient")
    doctor_id = fields.Many2one("res.users",string="Doctor")
    appointment_id = fields.Many2one("clinic.appointment",string="Appointment")  
    entry_datetime = fields.Datetime(string="Enter Date&Time",required=True)
    notes = fields.Text(string="Notes")