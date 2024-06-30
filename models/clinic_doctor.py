from odoo import models,fields

class ClinicDoctor(models.Model):
    _inherit = "res.users"

    specialty = fields.Text(string="Specialty")
    availability = fields.Date(string="Availability") 