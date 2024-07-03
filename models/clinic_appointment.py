from odoo import models,fields,api,Command
from odoo.exceptions import ValidationError,UserError

class ClinicAppointment(models.Model):
    _name = "clinic.appointment"

    appointment_id = fields.Char(string='Appointment ID', readonly=True, copy=False, index=True)
    patient_id = fields.Many2one("res.partner",string="Patient",required=True)
    doctor_id = fields.Many2one("res.users",string="Doctor",required=True)
    log_id = fields.One2many("clinic.log","appointment_id")
    treatment_id = fields.One2many("clinic.treatment","appointment_id")
    appointment = fields.Datetime(string="Appointment Time",required=True)
    appointment_type = fields.Selection(
        required=True,
        selection=[
        ('consultation','Consultation'),
        ('checkup','Checkup'),
        ('emergency','Emergency')
    ])
    status = fields.Selection([
        ('pending','Pending'),
        ('canceled', 'Canceled'),
        ('confirmed', 'Confirmed')
    ])
    notes = fields.Text(string="Add notes")
    
    @api.model
    def create(self, vals):
        if not vals.get('appointment_id'):
            vals['appointment_id'] = self.env['ir.sequence'].next_by_code('clinic.appointment.sequence')
        
        appointment = super(ClinicAppointment, self).create(vals)
        
        appointment.log_id.create({
            'patient_id': appointment.patient_id.id,
            'appointment_id': appointment.id,
            'create_uid': appointment.create_uid.id,
            'entry_datetime': appointment.appointment,
            'notes': appointment.notes
        })
        
        return appointment
    
    @api.constrains
    def _check_conflict(self):
        for record in self:
            if record.status != 'canceled':
                overlapping_appointments = self.search([
                    ('doctor_id', '=', record.doctor_id.id),
                    ('appontment','=',record.appointment),
                    ('id', '!=', record.id),
                    ('status', '!=','canceled')
                ])
                if overlapping_appointments:
                    raise ValidationError("This appointment isn't available")
    
    def pay_action(self):
        for record in self:
            if record.status != 'confirmed':
                record.status = 'confirmed'
        
        self.env["account.move"].create({
            "partner_id": self.patient_id.id,
            "move_type": "out_invoice",
            "invoice_line_ids": [
                Command.create({
                    "name": self.name,
                    "quantity": "1",
                    "price_unit": self.price
                })
            ],
        })
        return super().pay_action()

    # @api.model
    # def create(self, vals):    
    #     self.log_id.create({
    #         'patient_id': self.patient_id.id,
    #         'appointment_id': self.id,
    #         'create_uid': self.create_uid,
    #         'entry_datetime': self.appointment,
    #         'notes': self.notes
    #     })
    #     return super().create(vals)    