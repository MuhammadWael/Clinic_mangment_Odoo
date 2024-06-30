from odoo import models,fields,api

class ClinicPatient(models.Model):
    _inherit = "res.partner"

    patient_id = fields.Char(string='Patient ID', readonly=True, copy=False, index=True)
    birth_date = fields.Date(string="Date of Birth")
    emergency_contact = fields.Text(string="Emergency Contact")
    insurance_info = fields.Text(string="Isurance Info")
    
    @api.model
    def create(self,vals):
        vals['pateient_id'] = self.env['ir.sqeuence'].next_by_code('clinic_patient')
        return super(ClinicPatient, vals)

    

