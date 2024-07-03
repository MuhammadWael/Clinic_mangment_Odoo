from odoo import models,fields,api
from odoo.exceptions import ValidationError,UserError

class ClinicTreatment(models.Model):
    _name = "clinic.treatment"

    treatment_id = fields.Char(string='Treatment ID', readonly=True, copy=False, index=True)
    patient_id = fields.Many2one("res.partner",string="Patient")
    doctor_id = fields.Many2one("res.users",string="Doctor")
    appointment_id = fields.Many2one("clinic.appointment",string="Appointment")
    prescription_id = fields.One2many("clinic.prescription","treatment_id",string="Prescription")
    treatment_details = fields.One2many('clinic.treatment.details', 'treatment_id', string='Treatment Details')
    notes = fields.Text(string="Add notes")

    @api.model
    def create(self,vals):
        vals['treatment_id'] = self.env['ir.sequence'].next_by_code('clinic.treatment')
        return super().create(vals)
    
    @api.onchange('appointment_id')
    def _onchange_appointment(self):
        for record in self:
            if record.appointment_id:
                record.patient_id = self.env['clinic.appointment'].browse(record.appointment_id.id).patient_id.id
                record.doctor_id = self.env['clinic.appointment'].browse(record.appointment_id.id).doctor_id.id       
    
class ClinicTreatmentDetails(models.Model):
    _name = "clinic.treatment.details"


    diagnoses = fields.Char(string='Diagnoses')
    prescriped_medication = fields.Char(string='Prescriped Medication')
    proceduers = fields.Char(string='proceduers')
    treatment_id = fields.Many2one('clinic.treatment', string='Treatment', required=True)
