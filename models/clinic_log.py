from odoo import models,fields

class ClinicLog(models.Model):
    _name = "clinic.log"

    patient_id = fields.Many2one("res.partner",string="Patient")
    doctor_id = fields.Many2one("res.users",string="Doctor")
    appointment_id = fields.Many2one("clinic.appointment",string="Appointment")  
    appointment_id_to_be_shown = fields.Char(string="Appointment ID")  
    entry_datetime = fields.Datetime(string="Enter Date&Time",required=True)
    notes = fields.Text(string="Notes")
    status = fields.Selection(string="Status",
    selection=[
        ('available','Available'),
        ('pending','Pending'),
        ('canceled', 'Canceled'),
        ('confirmed', 'Confirmed')
    ],
    required="True")