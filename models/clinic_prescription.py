from odoo import models,fields,api
from odoo.exceptions import ValidationError,UserError

class ClinicPrescription(models.Model):
    _name = "clinic.prescription"

    prescription_id = fields.Char(string='Precription ID', readonly=True, copy=False, index=True)
    patient_id = fields.Many2one("res.partner",string="Patient")
    doctor_id = fields.Many2one("res.users",string="Doctor")
    treatment_id = fields.Many2one("clinic.treatment",string="Treatment")
    medication_details = fields.One2many('clinic.medication.detail', 'prescription_id', string='Medication Details')
    notes = fields.Text(string="Add notes")
    
    @api.model
    def create(self,vals):
        vals['prescription_id'] = self.env['ir.sequence'].next_by_code('clinic.prescription')
        return super().create(vals)

class MedicationDetail(models.Model):
    _name = 'clinic.medication.detail'

    name = fields.Char(string='Medication Name', required=True)
    dosage = fields.Char(string='Dosage', required=True)
    duration = fields.Char(string='Duration', required=True)
    prescription_id = fields.Many2one('clinic.prescription', string='Prescription', required=True)
