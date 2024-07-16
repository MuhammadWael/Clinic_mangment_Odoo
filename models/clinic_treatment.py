from odoo import models,fields,api
from odoo.exceptions import ValidationError,UserError

class ClinicTreatment(models.Model):
    _inherit = "product.template"

    treatment_id = fields.Char(string='Treatment ID', readonly=True, copy=False, index=True)
    notes = fields.Text(string="Add notes")
    treatment_details = fields.One2many('clinic.treatment.details', 'treatment_id', string='Treatment Details')
    is_treatment = fields.Boolean(string="is Patient?", default=False)
    #appointment_id = fields.Many2one("clinic.appointment",string="Appointment")
    # # Fields May be usefull for tracking the Treatmnet
    # patient_id = fields.Many2one("res.partner",string="Patient")
    # doctor_id = fields.Many2one("res.users",string="Doctor")
    # prescription_id = fields.One2many("clinic.prescription","treatment_id",string="Prescription")

    @api.model
    def create(self,vals):
        vals['treatment_id'] = self.env['ir.sequence'].next_by_code('clinic.treatment')
        return super().create(vals)
    
    # @api.onchange('appointment_id')
    # def _onchange_appointment(self):
    #     for record in self:
    #         if record.appointment_id:
    #             record.patient_id = self.env['clinic.appointment'].browse(record.appointment_id.id).patient_id.id
    #             record.doctor_id = self.env['clinic.appointment'].browse(record.appointment_id.id).doctor_id.id       
    
    def pay_action(self):
        for record in self:
            if not record.appointment_id:
                raise UserError("Treatment must be linked to an appointment before creating an invoice.")
            if not record.price:
                raise UserError("Treatment must have a price before creating an invoice.")
            
            invoice = self.env['account.move'].create_clinic_invoice(
                patient_id=record.appointment_id.patient_id.id,
                treatment_id=record.id,
                amount=record.price,
                taxes=record.taxes_id
            )
            if not invoice:
                raise UserError("Invoice creation failed.")
        
        return True
class ClinicTreatmentDetails(models.Model):
    _name = "clinic.treatment.details"


    diagnoses = fields.Char(string='Diagnoses')
    prescriped_medication = fields.Char(string='Prescriped Medication')
    proceduers = fields.Char(string='proceduers')
    treatment_id = fields.Many2one('clinic.treatment', string='Treatment', required=True)
