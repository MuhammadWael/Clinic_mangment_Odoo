from odoo import models,fields,api,Command
from odoo.exceptions import ValidationError,UserError,RedirectWarning
from pytz import timezone,UTC
from datetime import timedelta, datetime,date

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
    medical_record_id = fields.Many2one("clinic.medical_record")
    doctor_availability = fields.One2many('clinic.availability','appointmet_id',string="Doctor Availability")
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
    ],
    default='available')
    notes = fields.Text(string="Add notes")
    total_price = fields.Integer(string="Appointment Price",default=100)

    @api.model
    def create(self, vals):
        # if 'appointment' in vals:
        #     appointment_datetime = fields.Datetime.from_string(vals['appointment'])
        #     appointment_datetime_utc = self._convert_to_utc(appointment_datetime)
        #     vals['appointment'] = appointment_datetime.strftime('%Y-%m-%d %H:%M:%S')

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
        appointment._make_medical_record()
        return appointment
    
    @api.depends('appointment_id')    
    def _compute_name(self):
        for record in self:
            if record.appointment_id:
                record.name = f"Appointment {record.appointment_id}"
    
    # @api.constrains
    # def _check_conflict(self):
    #     for record in self:
    #         if not record.patient_id:
    #             record.status = 'available'

    #         if record.status != 'canceled':
    #             overlapping_appointments = self.search([
    #                 ('doctor_id', '=', record.doctor_id.id),
    #                 ('appointment','=',record.appointment),
    #                 ('id', '!=', record.id),
    #                 ('status', '!=','canceled')
    #             ])
    #             if overlapping_appointments:
    #                 raise ValidationError("This appointment isn't available")
    
    def pay_action(self):
        for record in self:
            if record.patient_id:
                if record.status != 'confirmed':
                    record.status = 'confirmed'
                self.env['account.move'].create_clinic_invoice(
                      record.patient_id.id,
                      record.id, 
                      )
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
      
                    # appointment_datetime_local = fields.Datetime.from_string(record.appointment)
                    # new_appointment_datetime_local = self._convert_to_local(
                    #     self._convert_from_local(appointment_datetime_local) + timedelta(hours=3)
                    # ).strftime('%Y-%m-%d %H:%M:%S')
                    # self.env['clinic.appointment'].create({
                    #     'doctor_id': record.doctor_id.id,
                    #     'appointment': new_appointment_datetime_local,
                    #     'doctor_availability': record.doctor_availability.id,
                    #     'status': 'available'
                    # })
            else:
                raise ValidationError("This appointment has no patient")
        return True

    @api.onchange('patient_id','doctor_id')
    def _change_status_to_pending(self):
        for record in self:
            if record.patient_id and record.doctor_id:
                record.status = 'pending'
        
    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        for record in self:
            if record.doctor_id:
                record.doctor_availability = record.doctor_id.availability
    
    @api.constrains('appointment')
    def _check_appointment(self):
        day_mapping = {
            'sat': 5,
            'sun': 6,
            'mon': 0,
            'tues': 1,
            'wed': 2,
            'thurs': 3,
            'fri': 4
        }

        for record in self:
            if record.doctor_id and record.appointment:

                appointment_datetime = fields.Datetime.from_string(record.appointment) + timedelta(hours=3)
                appointment_day = appointment_datetime.weekday()  
                appointment_time = appointment_datetime.time() 

                available = False

                for availability in record.doctor_id.availability:
                    availability_day = day_mapping.get(availability.week_day.strip().lower())
                    availability_start_time = (datetime.min + timedelta(hours=availability.start_time)).time()
                    availability_end_time = (datetime.min + timedelta(hours=availability.end_time)).time()

                    if (availability_day == appointment_day and
                            availability_start_time <= appointment_time <= availability_end_time):
                        available = True
                        break
                if not available:
                    raise ValidationError("The selected doctor is not available at the specified time.")
                
                overlapping_appointments = self.search([
                    ('doctor_id', '=', record.doctor_id.id),
                    ('appointment','=',record.appointment),
                    ('id', '!=', record.id),
                    ('status', '!=','canceled')
                ])
                if overlapping_appointments:
                    overlapping_info = "\n".join([
                        f"Appointment ID: {appt.appointment_id}, Patient: {appt.patient_id.name}"
                        for appt in overlapping_appointments
                    ])
                    raise RedirectWarning(f"This time slot has overlapping appointments:\n{overlapping_info}")
                return True

    def write(self, vals):
        res = super().write(vals)
        if 'status' in vals:
            self._record_status_change()
        self._make_medical_record()
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

    @api.onchange('treatment_id')
    def _make_medical_record(self):
        if self.patient_id and self.id:
            for treatment in self.treatment_id:
                self.env['clinic.medical_record'].create({
                    'patient_id': self.patient_id.id,
                    'appointment_id_to_be_shown': self.appointment_id,
                    # 'prescrption_id':self.prescription_id,
                    'treatment_id': treatment.id,
                    'entry_datetime': fields.Datetime.now(),
                    'notes': self.notes
                })
    
    @api.onchange('prescription_id')
    def _make_medical_record_for_prescription(self):
        if self.patient_id and self.prescription_id:
            for treatment in self.prescription_id.treatment_id:
                self.env['clinic.medical_record'].create({
                    'patient_id': self.patient_id.id,
                    'appointment_id_to_be_shown': self.appointment_id,
                    'prescription_id':self.prescription_id.id,
                    'treatment_id': treatment.id,
                    'entry_datetime': fields.Datetime.now(),
                    'notes': self.notes
                })

