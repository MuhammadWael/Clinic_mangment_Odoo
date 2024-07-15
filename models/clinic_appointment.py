from odoo import models,fields,api,Command
from odoo.exceptions import ValidationError,UserError
from pytz import timezone

class ClinicAppointment(models.Model):
    _name = "clinic.appointment"

    appointment_id = fields.Char(string='Appointment ID', readonly=True, copy=False, index=True)
    name = fields.Char(string='Name', compute='_compute_name', store=True)
    patient_id = fields.Many2one("res.partner",string="Patient")
    doctor_id = fields.Many2one("res.users",string="Doctor",required=True)
    specialty = fields.Selection(related='doctor_id.specialty', string='Specialty', store=True)
    log_id = fields.One2many("clinic.log","appointment_id")
    treatment_id = fields.Many2many("product.template","appointment_id")
    prescription_id = fields.One2many("clinic.prescription","appointment_id",string="Prescription")
    medical_record_id = fields.One2many("clinic.medical_record","appointment_id")
    appointment = fields.Datetime(string="Appointment Time",required=True)
    appointment_type = fields.Selection(
        selection=[
        ('consultation','Consultation'),
        ('checkup','Checkup'),
        ('emergency','Emergency')
    ],
    default ='checkup')
    status = fields.Selection([
        ('available','Available'),
        ('pending','Pending'),
        ('canceled', 'Canceled'),
        ('confirmed', 'Confirmed')
    ])
    notes = fields.Text(string="Add notes")
    total_price = fields.Integer(string="Price")

    @api.model
    def create(self, vals):
        if 'appointment' in vals:
            cairo_tz = timezone('Africa/Cairo')
            appointment_datetime = cairo_tz.localize(fields.Datetime.from_string(vals['appointment']), is_dst=None)
            vals['appointment'] = appointment_datetime.astimezone(timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S')
  
        if not vals.get('appointment_id'):
            vals['appointment_id'] = self.env['ir.sequence'].next_by_code('clinic.appointment.sequence')
        
        appointment = super(ClinicAppointment, self).create(vals)
        if vals.get('patient_id'):
            appointment.log_id.create({
                'patient_id': appointment.patient_id.id,
                'appointment_id': appointment.id,
                'create_uid': appointment.create_uid.id,
                'entry_datetime': appointment.appointment,
                'notes': appointment.notes,
                'status': appointment.status
            })
        return appointment
    
    @api.depends('appointment_id')    
    def _compute_name(self):
        for record in self:
            if record.appointment_id:
                record.name = f"Appointment {record.appointment_id}"
    
    @api.constrains
    def _check_conflict(self):
        for record in self:
          
            if not record.patient_id:
                record.status = 'available'

            if record.status != 'canceled':
                overlapping_appointments = self.search([
                    ('doctor_id', '=', record.doctor_id.id),
                    ('appointment','=',record.appointment),
                    ('id', '!=', record.id),
                    ('status', '!=','canceled')
                ])
                if overlapping_appointments:
                    raise ValidationError("This appointment isn't available")
    
    def pay_action(self):
        for record in self:
            if record.patient_id:
                if record.status != 'confirmed':
                    record.status = 'confirmed'
                self.env['account.move'].create_clinic_invoice(
                      record.patient_id.id,
                      record.id, 
                      record.treatment_id.id)
            else:
                raise ValidationError("This appointment has no patient")
        return True
    def cancel_action(self):
        for record in self:
            if record.patient_id:
                if record.status == 'confirmed':
                    raise ValidationError("This appointment already Payed")
                else:
                    record.status = 'canceled'
            else:
                raise ValidationError("This appointment has no patient")
        return True

    @api.onchange('patient_id')
    def _change_status_to_pending(self):
        for record in self:
            if record.patient_id:
                record.status = 'pending'
            
    def write(self, vals):
        res = super().write(vals)
        if 'status' in vals:
            self._record_status_change()
        return res
    
    def _record_status_change(self):
        for record in self:
            self.env['clinic.log'].create({
                'patient_id': record.patient_id.id,
                'appointment_id': record.id,
                'appointment_id_to_be_shown': record.appointment_id,
                'entry_datetime': fields.datetime.now(),
                'status': record.status,
                'notes': record.notes,
            })
            self.env['clinic.medical_record'].create({
                'patient_id': record.patient_id.id,
                'appointment_id': record.id,
                'treatment_id': record.treatment_id,
                'entry_datetime': fields.datetime.now(),
                'notes': record.notes
            })
            



