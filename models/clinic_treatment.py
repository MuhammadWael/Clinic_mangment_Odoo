from odoo import models,fields,api
from odoo.exceptions import ValidationError,UserError

class ClinicTreatment(models.Model):
    _name = "clinic.treatment"

    patient_id = fields.Many2one("res.partner",string="Patient")
    doctor_id = fields.Many2one("res.users",string="Doctor")
    appointment_id = fields.Many2one("clinic.appointment",string="Appointment")
    prescription_id = fields.One2many("clinic.prescription","treatment_id")
    details = fields.Selection(required=True,
                               selection=[
        ('diagnosis','Diagnosis'),
        ('prescribed_medications','Prescribed Medications'),
        ('procedures','Procedures')
    ])

    notes = fields.Text(string="Add notes")

    @api.onchange('appointment_id')
    def _onchange_appointment(self):
        for record in self:
            if record.appointment_id:
                record.patient_id = self.env['clinic.appointment'].browse(record.appointment_id.id).patient_id.id
                record.doctor_id = self.env['clinic.appointment'].browse(record.appointment_id.id).doctor_id.id       