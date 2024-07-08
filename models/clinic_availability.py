from odoo import models,fields,api

class ClinicAvailability(models.Model):
    _name = "clinic.availability"

    doctor_id = fields.One2many("res.users","availability",string="Availability")
    week_day = fields.Selection( string="Day",
        selection=[
            ('sat ','Sat'),
            ('sun ','Sun'),
            ('mon ','Mon'),
            ('tues','Tues'),
            ('wed ','Wed'),
            ('thurs ','Thrus'),
            ('fri ','Fri')
        ],
        required=True
    )
    start_time = fields.Float(string="Start Time",widget="float_time",required=True)
    end_time = fields.Float(string="End Time",widget="float_time",required=True)