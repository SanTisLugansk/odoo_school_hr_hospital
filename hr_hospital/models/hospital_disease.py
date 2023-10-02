from odoo import fields, models


class HospitalDisease(models.Model):
    _name = 'hospital.disease'
    _description = 'Hospital Disease'

    name = fields.Char(string='Title', required=True)
    # active = fields.Boolean(default=True,)
