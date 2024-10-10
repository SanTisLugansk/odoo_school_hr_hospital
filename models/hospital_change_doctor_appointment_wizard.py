from datetime import datetime, time
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HospitalChangeDoctorAppointmentWizard(models.TransientModel):
    _name = 'hospital.change.doctor.appointment.wizard'
    _description = 'Hospital change the visit of the doctor'

    visit_id = fields.Many2one(comodel_name='hospital.patient.visit')
    visit_doctor_id = fields.Many2one(comodel_name='hospital.doctor')
    visit_date = fields.Datetime()
    schedule_id = fields.Many2one(comodel_name='hospital.doctor.schedule')

    @api.onchange('schedule_id')
    def _onchange_schedule(self):
        if self.schedule_id.date:
            self.visit_doctor_id = self.schedule_id.doctor_id
            self.visit_date = datetime.combine(self.schedule_id.date, time(self.schedule_id.hour, 0, 0))

    def action_change_doctor_appointment(self):
        for rec in self:
            if rec.visit_id.state == 'done':
                raise ValidationError(_('The visit to the doctor has already take, changes are not possible'))

            schedule_count = self.env['hospital.patient.visit'].sudo().search_count([('schedule', '=', rec.schedule_id.id)])
            if schedule_count > 0:
                raise ValidationError(_('This time is already taken'))

            rec.visit_id.write({'schedule': rec.schedule_id.id,
                                'doctor_id': rec.visit_doctor_id,
                                'date': rec.visit_date})
