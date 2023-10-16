from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HospitalDoctorSchedule(models.Model):
    _name = 'hospital.doctor.schedule'
    _description = 'Hospital Doctor Schedule'

    doctor_id = fields.Many2one(comodel_name='hospital.doctor', required=True)
    date = fields.Date(required=True)
    hour = fields.Integer(required=True)

    @api.constrains('hour', 'date', 'doctor_id')
    def _constrains_hour(self):
        for rec in self:
            if rec.hour < 0 or rec.hour > 23:
                raise ValidationError(_('The hour must be from 0 to 23'))
            found_sp = self.search([('doctor_id.id', '=', rec.doctor_id.id),
                                    ('date', '=', rec.date),
                                    ('hour', '=', rec.hour),
                                    ('id', '!=', rec.id)])
            if found_sp.id:
                raise ValidationError(_('Entry is already in the schedule'))

    def name_get(self):
        return [(rec.id, f'{rec.doctor_id.name}  {rec.date} '
                         f' hour: {rec.hour}') for rec in self]
