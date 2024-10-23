from datetime import datetime, time
from pytz import timezone, utc
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HospitalPatientVisit(models.Model):
    # Візити пацієнтів
    _name = 'hospital.patient.visit'
    _description = 'Hospital Patient Visit'

    state = fields.Selection(selection=[('done', 'Done'), ('draft', 'Draft')], default='draft', required=True)
    active = fields.Boolean(default=True)
    patient_id = fields.Many2one(comodel_name='hospital.patient', readonly=False, states={'done': [('readonly', True)]})
    date = fields.Datetime(readonly=False, states={'done': [('readonly', True)]})
    doctor_id = fields.Many2one(comodel_name='hospital.doctor', compute='_compute_doctor_id', inverse='_inverse_doctor_id')
    diagnosis_ids = fields.One2many(comodel_name='hospital.diagnosis', inverse_name='visit_id',
                                    # domain="[('doctor_id', '=', doctor_id), ('patient_id', '=', patient_id)]")
                                    )
    diagnosis_is_editable = fields.Boolean(compute='_compute_diagnosis_is_editable')
    schedule = fields.Many2one(comodel_name='hospital.doctor.schedule', readonly=False, states={'done': [('readonly', True)]})

    def name_get(self):
        return [(rec.id, f'patient: {rec.patient_id.name}  at {rec.date}  doctor: {rec.doctor_id.name}') for rec in self]

    @api.depends('date')
    def _compute_diagnosis_is_editable(self):
        for rec in self:
            if rec.date and rec.date <= datetime.now():
                rec.diagnosis_is_editable = True
            else:
                rec.diagnosis_is_editable = False

    @api.depends('schedule')
    def _compute_doctor_id(self):
        for rec in self:
            rec.doctor_id = rec.schedule.doctor_id

    @api.depends('doctor_id')
    def _inverse_doctor_id(self):
        for rec in self:
            if rec.doctor_id != rec.schedule.doctor_id:
                rec.schedule = False
            rec._set_domain()

    def _set_domain(self):
        if self.date and self.doctor_id:
            return {"domain": {'schedule': [('doctor_id', '=', self.doctor_id.id), ('date', '=', self.date.date())]}}
        if self.date:
            return {"domain": {'schedule': [('date', '=', self.date.date())]}}
        if self.doctor_id:
            return {"domain": {'schedule': [('doctor_id', '=', self.doctor_id.id)]}}
        return {"domain": {'schedule': []}}

    @api.model
    def cron_done(self):
        # ця процедура автоматично виконується кожної години (Settings / Technical / Automation / Scheduled Actions)
        found_sp = self.search([('date', '<', fields.datetime.now()), ('state', '!=', 'done')])
        # for rec in found_sp:
        #    print('rec.date = ', rec.date)
        found_sp.write({'state': 'done'})

    @api.onchange('schedule')
    def _onchange_schedule(self):
        for rec in self:
            domain = [('schedule.id', '=', rec.schedule.id)]
            if rec._origin.id is not False:
                domain.append(('id', '!=', rec._origin.id))
            if rec.schedule.id and self.search_count(domain) > 0:
                raise ValidationError(_('This time is already taken'))

    @api.onchange('doctor_id', 'patient_id', 'date')
    def _set_done(self):
        self.cron_done()

    @api.onchange('date')
    def _onchange_date(self):
        for rec in self:
            rec._set_domain()

    @api.onchange('schedule', 'date')
    def _set_date(self):
        user_tz = timezone(self.env.user.tz)
        if self.date is not False:
            local_date = self.date.astimezone(user_tz)
        if self.schedule.date and (self.date is False or local_date.date() != self.schedule.date or local_date.hour != self.schedule.hour):
            local_date = user_tz.localize(datetime.combine(self.schedule.date, time(self.schedule.hour, 0, 0)))
            date_in_utc = local_date.astimezone(utc)
            self.date = date_in_utc.replace(tzinfo=None)

    @api.constrains('active')
    def _constrains_date(self):
        for rec in self:
            if len(rec.diagnosis_ids) > 0 and (not rec.active):
                raise ValidationError(_('You cannot archive a visit with a diagnosis'))

    @api.ondelete(at_uninstall=False)
    def _ondelete_patient_visit(self):
        for rec in self:
            if len(rec.diagnosis_ids) > 0:
                raise ValidationError(_("You cannot delete a visit with a diagnosis"))
            if self.state == 'done' and (not rec.active):
                raise ValidationError(_('You cannot delete a visit that has already taken place'))

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
