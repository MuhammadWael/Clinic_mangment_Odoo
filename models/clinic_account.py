from odoo import models,fields,api,Command

class ClinicAccount(models.Model):
    _inherit = "account.move"

    patient_id = fields.Many2one("res.partner",string="Patient")
    appointment_id = fields.Many2one("clinic.appointment",string="Appointment")
        
    
    @api.model
    def create_clinic_invoice(self, patient_id, appointment_id):
        if appointment_id:
            appointment = self.env['clinic.appointment'].browse(appointment_id)
            invoice_line = {
                'name': appointment.name,
                'quantity': 1,
                'price_unit': appointment.total_price,
            }
        invoice = self.create({
            'move_type': 'out_invoice',
            'partner_id': patient_id,
            'invoice_line_ids': [Command.create(invoice_line)],
            'appointment_id': appointment_id,
        })
        return invoice
