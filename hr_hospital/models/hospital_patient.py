from odoo import fields, models


class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Hospital Patient'

    name = fields.Char(string='Full name', required=True)
    # active = fields.Boolean(default=True, )
    observing_doctor = fields.Many2many(comodel_name='hospital.doctor')
