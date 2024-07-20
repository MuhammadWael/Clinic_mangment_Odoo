from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta, datetime
class ClinicAvailability(models.Model):
    _name = "clinic.availability"

    doctor_id = fields.Many2one("res.users", string="Doctor", required=True)
    week_day = fields.Selection(
        string="Day",
        selection=[
            ('sat', 'Sat'),
            ('sun', 'Sun'),
            ('mon', 'Mon'),
            ('tues', 'Tues'),
            ('wed', 'Wed'),
            ('thurs', 'Thurs'),
            ('fri', 'Fri')
        ],
        required=True
    )

    start_time = fields.Float(string="Start Time", required=True)
    end_time = fields.Float(string="End Time", required=True)
    appointmet_id = fields.One2many("clinic.appointment","doctor_availability")
    
    def _make_appointments(self):
        day_mapping = {
            'sat': 5,
            'sun': 6,
            'mon': 0,
            'tues': 1,
            'wed': 2,
            'thurs': 3,
            'fri': 4
        }
        current_date = datetime.now()
        end_date = current_date + timedelta(weeks=4)
        while current_date <= end_date:
            if current_date.weekday() == day_mapping.get(self.week_day.strip().lower()):
                start_time = self.start_time
                end_time = self.end_time
                while start_time < end_time:
                    appointment_datetime = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=start_time)
                    self.env['clinic.appointment'].create({
                        'doctor_id': self.doctor_id.id,
                        'appointment': appointment_datetime,
                        'doctor_availability': self.id,
                        'status': 'available'
                    })
                    start_time += 0.25
            current_date += timedelta(days=1)

    def _delete_related_appointments(self):
        for record in self:
            old_appointments = self.env['clinic.appointment'].search([('doctor_availability', '=', record.id)])
            old_appointments.unlink()

    @api.model
    def create(self, vals):
        res = super(ClinicAvailability, self).create(vals)
        res._make_appointments()
        return res

    def write(self, vals):
        res = super(ClinicAvailability, self).write(vals)
        for record in self:
            old_appointments = self.env['clinic.appointment'].search([('doctor_availability', '=', record.id)])
            old_appointments.unlink()
            record._make_appointments()
        return res
    
    def unlink(self):
        self._delete_related_appointments()
        return super(ClinicAvailability, self).unlink()

