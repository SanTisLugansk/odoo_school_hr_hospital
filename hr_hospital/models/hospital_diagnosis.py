from odoo import fields, models


class HospitalDiagnosis (models.Model):
    _name = 'hospital.diagnosis'
    _description = 'Hospital Diagnosis'

    date = fields.Date(string='Date of diagnosis')
    doctor_id = fields.Many2one(comodel_name='hospital.doctor', required=True)
    patient_id = fields.Many2one(comodel_name='hospital.patient',
                                 required=True)
    disease_ids = fields.Many2many(comodel_name='hospital.disease',
                                   required=True)
    appointment = fields.Char(string='Appointment for treatment')

    def name_get(self):
        return [(rec.id, f'{rec.patient_id.name}  {rec.doctor_id.name} '
                         f' {rec.date}') for rec in self]
