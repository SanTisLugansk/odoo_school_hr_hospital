from odoo import fields, models


class HospitalDoctorChange(models.Model):
    _name = 'hospital.doctor.change'
    _description = 'Hospital Doctors Changes'

    date = fields.Datetime(readonly=True)
    doctor_id = fields.Many2one(comodel_name='hospital.doctor', readonly=True)
    patient_id = fields.Many2one(comodel_name='hospital.patient',
                                 readonly=True)
