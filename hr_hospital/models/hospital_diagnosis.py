from odoo import api, fields, models


class HospitalDiagnosis (models.Model):
    _name = 'hospital.diagnosis'
    _description = 'Hospital Diagnosis'

    date = fields.Date(string='Date of diagnosis')
    date_year = fields.Integer(compute='_compute_date')
    date_month = fields.Integer(compute='_compute_date')
    doctor_id = fields.Many2one(comodel_name='hospital.doctor', required=True)
    patient_id = fields.Many2one(comodel_name='hospital.patient',
                                 required=True)
    disease_ids = fields.Many2many(comodel_name='hospital.disease',
                                   required=True)
    appointment = fields.Char(string='Appointment for treatment')
    needed_doctor_comment = fields.Boolean(compute='_compute_need_doctor_com')

    def name_get(self):
        return [(rec.id, f'{rec.patient_id.name}  {rec.doctor_id.name} '
                         f' {rec.date}') for rec in self]

    def _compute_need_doctor_com(self):
        for rec in self:
            if rec.doctor_id._is_intern():
                rec.needed_doctor_comment = True
            else:
                rec.needed_doctor_comment = False

    @api.depends('date')
    def _compute_date(self):
        for rec in self:
            rec.date_month = rec.date.month
            rec.date_year = rec.date.year

