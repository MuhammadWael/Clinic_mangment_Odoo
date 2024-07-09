from odoo import models,fields,api,Command
from odoo.exceptions import ValidationError,UserError
from pytz import timezone

class ClinicAppointment(models.Model):
    _name = "clinic.appointment"

    appointment_id = fields.Char(string='Appointment ID', readonly=True, copy=False, index=True)
    name = fields.Char(string='Name', compute='_compute_name', store=True)
    patient_id = fields.Many2one("res.partner",string="Patient",required=True)
    doctor_id = fields.Many2one("res.users",string="Doctor",required=True)
    specialty = fields.Char(related='doctor_id.specialty', string='Specialty', store=True)
    log_id = fields.One2many("clinic.log","appointment_id")
    treatment_id = fields.One2many("clinic.treatment","appointment_id")
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
    duration = fields.Float(string="How Many slots?" ,default=1)
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
        
        appointment.log_id.create({
            'patient_id': appointment.patient_id.id,
            'appointment_id': appointment.id,
            'create_uid': appointment.create_uid.id,
            'entry_datetime': appointment.appointment,
            'notes': appointment.notes
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
        
            self.env['account.move'].create_clinic_invoice(record.patient_id.id, record.id, record.treatment_id.id)
        return True

