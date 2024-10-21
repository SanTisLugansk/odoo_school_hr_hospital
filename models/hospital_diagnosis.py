from odoo import fields, models, _, api
from odoo.exceptions import ValidationError


class HospitalDiagnosis (models.Model):
    # Діагнози
    _name = 'hospital.diagnosis'
    _description = 'Hospital Diagnosis'

    date = fields.Date(string='Date of diagnosis')
    visit_id = fields.Many2one(comodel_name='hospital.patient.visit', required=True)
    visit_readonly = fields.Boolean(compute='_compute_visit_readonly')
    doctor_id = fields.Many2one(comodel_name='hospital.doctor', compute='_compute_doctor_patient')
    patient_id = fields.Many2one(comodel_name='hospital.patient', compute='_compute_doctor_patient')
    disease_ids = fields.Many2many(comodel_name='hospital.disease', required=True)
    appointment = fields.Char(string='Appointment for treatment')
    needed_doctor_comment = fields.Boolean(compute='_compute_need_doctor_com')

    @api.constrains('date')
    def _constrains_date(self):
        for rec in self:
            if rec.visit_id is False:
                raise ValidationError(_('First you have to choose a visit'))
            if rec.date < rec.visit_id.date.date():
                raise ValidationError(_('The date of diagnosis must be greater than the date of the visit'))

    @api.onchange('visit_id')
    def _compute_visit_readonly(self):
        self.visit_readonly = self.env.context.get('visit_readonly', False)

    def name_get(self):
        return [(rec.id, f'{rec.patient_id.name}  {rec.doctor_id.name}  {rec.date}') for rec in self]

    @api.depends('doctor_id')
    def _compute_need_doctor_com(self):
        for rec in self:
            if rec.doctor_id._is_intern():
                rec.needed_doctor_comment = True
            else:
                rec.needed_doctor_comment = False

    @api.depends('visit_id')
    def _compute_doctor_patient(self):
        for rec in self:
            rec.doctor_id = rec.visit_id.doctor_id
            rec.patient_id = rec.visit_id.patient_id
