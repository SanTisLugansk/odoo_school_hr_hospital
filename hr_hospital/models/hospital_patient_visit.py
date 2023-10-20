from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HospitalPatientVisit(models.Model):
    _name = 'hospital.patient.visit'
    _description = 'Hospital Patient Visit'

    state = fields.Selection(selection=[('done', 'Done'),
                                        ('draft', 'Draft')],
                             default='draft', required=True)
    active = fields.Boolean(default=True)
    patient_id = fields.Many2one(comodel_name='hospital.patient')
    date = fields.Datetime(readonly=False,
                           states={'done': [('readonly', True)]})
    date_only = fields.Date(compute='_compute_date_only', readonly=True)
    doctor_id = fields.Many2one(comodel_name='hospital.doctor', readonly=False,
                                states={'done': [('readonly', True)]})
    diagnosis_ids = fields.Many2many(comodel_name='hospital.diagnosis',
                                     domain="[('doctor_id', '=', doctor_id), "
                                            "('patient_id', '=', patient_id)]")
    schedule = fields.Many2one(comodel_name='hospital.doctor.schedule',
                               domain="[('doctor_id', '=', doctor_id), "
                                      "('date', '=', date_only)]")

    def name_get(self):
        return [(rec.id, f'patient: {rec.patient_id.name}  at {rec.date}  '
                         f'doctor: {rec.doctor_id.name}') for rec in self]

    @api.model
    def cron_done(self):
        # ця процедура автоматично виконується кожної години
        # (технічні налаштування / заплановані дії)
        found_sp = self.search([('date', '<', fields.datetime.now()),
                                ('state', '!=', 'done')])
        # for rec in found_sp:
        #    print('rec.date = ', rec.date)
        found_sp.write({'state': 'done'})

    @api.onchange('schedule')
    def _onchange_schedule(self):
        for rec in self:
            find_count = self.search_count([('schedule.id',
                                             '=', rec.schedule.id)])
            if find_count > 0:
                raise ValidationError(_('This time is already taken'))

    @api.onchange('doctor_id', 'date')
    def _set_done(self):
        self.cron_done()

    @api.depends('date')
    def _compute_date_only(self):
        for rec in self:
            rec.date_only = fields.Date.to_date(rec.date)

    @api.constrains('active')
    def _constrains_date(self):
        for rec in self:
            if len(rec.diagnosis_ids) > 0 and (not rec.active):
                raise ValidationError(_('You cannot archive '
                                        'a visit with a diagnosis'))

    @api.ondelete(at_uninstall=False)
    def _ondelete_patient_visit(self):
        for rec in self:
            if len(rec.diagnosis_ids) > 0:
                raise ValidationError(_('You cannot delete '
                                        'a visit with a diagnosis'))

    def hospital_change_appointment_wizard_act_window(self):
        # patient_ids = []
        # for rec in self:
        #     patient_ids.append(rec.id)
        return {'name': _('Change observing doctor wizard'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'hospital.change.doctor.appointment.wizard',
                'target': 'new',
                'context': {'default_visit_id': self.id,
                            # 'default_visit_doctor_id': self.doctor_id.id,
                            # 'default_visit_date': self.date
                            }}
