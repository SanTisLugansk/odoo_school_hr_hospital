from odoo import fields, models


class HospitalPatientVisit(models.Model):
    _name = 'hospital.patient.visit'
    _description = 'Hospital Patient Visit'

    patient = fields.Many2many(comodel_name='hospital.patient')
    # active = fields.Boolean(default=True, )
    date = fields.Datetime()
    disease = fields.Many2many(comodel_name='hospital.disease')
