from odoo import models,fields,api
from odoo.exceptions import ValidationError,UserError

class ClinicPrescription(models.Model):
    _name = "clinic.prescription"

    prescription_id = fields.Char(string='Precription ID', readonly=True, copy=False, index=True)
    appointment_id = fields.Many2one("clinic.appointment",required=True)
    patient_id = fields.Many2one("res.partner",string="Patient", related="appointment_id.patient_id")
    doctor_id = fields.Many2one("res.users",string="Doctor", related="appointment_id.doctor_id")
    treatment_id = fields.Many2many("product.template",string="Treatment")
    medication_details = fields.One2many('clinic.medication.detail', 'prescription_id', string='Medication Details')
    notes = fields.Text(string="Add notes")
    medical_record_id = fields.Many2one("clinic.medical_record","prescription_id") 
    @api.model
    def create(self,vals):
        vals['prescription_id'] = self.env['ir.sequence'].next_by_code('clinic.prescription')
        return super().create(vals)

class MedicationDetail(models.Model):
    _name = 'clinic.medication.detail'

    treatment_id = fields.Many2one('product.template') 
    name = fields.Char(string='Medication Name',related="treatment_id.name",required=True)
    dosage = fields.Char(string='Dosage', required=True)
    duration = fields.Char(string='Duration', required=True)
    prescription_id = fields.Many2one('clinic.prescription', string='Prescription', required=True)