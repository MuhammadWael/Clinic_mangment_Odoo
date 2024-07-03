from odoo import models,fields,api
from odoo.exceptions import ValidationError,UserError

class ClinicTreatment(models.Model):
    _name = "clinic.treatment"

    treatment_id = fields.Char(string='Treatment ID', readonly=True, copy=False, index=True)
    name = fields.Char(string='Name', compute='_compute_name', store=True)
    patient_id = fields.Many2one("res.partner",string="Patient")
    doctor_id = fields.Many2one("res.users",string="Doctor")
    appointment_id = fields.Many2one("clinic.appointment",string="Appointment")
    prescription_id = fields.One2many("clinic.prescription","treatment_id",string="Prescription")
    treatment_details = fields.One2many('clinic.treatment.details', 'treatment_id', string='Treatment Details')
    notes = fields.Text(string="Add notes")
    total_price = fields.Integer(string="Price")

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
    
    @api.depends('treatment_id')    
    def _compute_name(self):
        for record in self:
            if record.treatment_id:
                record.name = f"Treatment {record.treatment_id}"
    
    def pay_action(self):
        for record in self:
            self.env['account.move'].create_clinic_invoice(record.patient_id.id, None, record.id)
        
        return True
class ClinicTreatmentDetails(models.Model):
    _name = "clinic.treatment.details"


    diagnoses = fields.Char(string='Diagnoses')
    prescriped_medication = fields.Char(string='Prescriped Medication')
    proceduers = fields.Char(string='proceduers')
    treatment_id = fields.Many2one('clinic.treatment', string='Treatment', required=True)
