from odoo import models,fields,api

class ClinicPatient(models.Model):
    _inherit = "res.partner"

    patient_id = fields.Char(string='Patient ID', readonly=True, copy=False, index=True)
    birth_date = fields.Date(string="Date of Birth")
    emergency_contact = fields.Text(string="Emergency Contact")
    insurance_info = fields.Text(string="Isurance Info")
    
    @api.model
    def create(self,vals):
        vals['patient_id'] = self.env['ir.sequence'].next_by_code('clinic.patient')
        return super().create(vals)
    

    

