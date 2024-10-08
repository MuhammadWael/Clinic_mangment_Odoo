from odoo import models,fields,api
from odoo.exceptions import ValidationError,UserError

class ClinicMedicalRecord(models.Model):
    _name = "clinic.medical_record"

    patient_id = fields.Many2one("res.partner",string="Patient")
    appointment_id_to_be_shown = fields.Char(string="Appointment ID")  
    entry_datetime = fields.Datetime(string="Date&Time")
    treatment_id = fields.Many2one("product.template",string="Treatment")
    prescription_id = fields.Many2one("clinic.prescription")
   
    notes = fields.Text(string="Add notes")

    upload_file = fields.Binary(string="Upload File", attachment=True)
    upload_file_name = fields.Char(string="File Name", compute="_compute_upload_file_name", store=True)

    # def _compute_upload_file_name(self):
    #     for record in self:
    #         if record.upload_file:
    #             record.upload_file_name = record.upload_file_filename or 'Uploaded File'
    #         else:
    #             record.upload_file_name = False