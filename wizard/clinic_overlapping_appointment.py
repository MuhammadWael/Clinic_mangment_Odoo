from odoo import models, fields, api

class ClinicOverlappingAppointment(models.TransientModel):
    _name = 'clinic.overlapping.appointment'

    overlapping_appointments = fields.Text(readonly=True)

    def action_confirm(self):
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}
