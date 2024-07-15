from odoo import models,fields,api
from odoo.exceptions import ValidationError,UserError
from datetime import date

class ClinicPatient(models.Model):
    _inherit = "res.partner"

    patient_id = fields.Char(string='Patient ID', readonly=True, copy=False, index=True)
    birth_date = fields.Date(string="Date of Birth")
    emergency_contact = fields.Char(string="Emergency Contact")
    insurance_info = fields.Text(string="Isurance Info")
    medical_record_id = fields.One2many("clinic.medical_record","patient_id",string="Medical Records")
    is_patient = fields.Boolean(string="is Patient?", default=False)
    age = fields.Integer(string="Age", compute="_compute_age")
    
    @api.model
    def create(self,vals):
        vals['patient_id'] = self.env['ir.sequence'].next_by_code('clinic.patient')
        return super().create(vals)
    
    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = date.today()
                if record.birth_date > today:
                    raise UserError("Birth Day Can't be in the Future") 
                else:
                    birth_date = fields.Date.from_string(record.birth_date)
                    record.age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            else:
                record.age = 0


    

