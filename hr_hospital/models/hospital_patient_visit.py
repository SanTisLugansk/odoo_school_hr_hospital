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
    doctor_id = fields.Many2one(comodel_name='hospital.doctor', readonly=False,
                                states={'done': [('readonly', True)]})
    diagnosis_ids = fields.Many2many(comodel_name='hospital.diagnosis')
    schedule_sel = fields.Selection(selection='_selection_schedule')
    schedule = fields.Many2one(comodel_name='hospital.doctor.schedule')

    @api.model
    def cron_done(self):
        # ця процедура автоматично виконується кожної години
        # (технічні налаштування / заплановані дії)
        found_sp = self.search([('date', '<', fields.datetime.now()),
                                ('state', '!=', 'done')])
        # for rec in found_sp:
        #    print('rec.date = ', rec.date)
        found_sp.write({'state': 'done'})

    def _selection_schedule(self):
        res_find = self.schedule.search([('doctor_id.id', '=',
                                          self.doctor_id.id),
                                        # ('date', '=', self.date.Date())
                                         ])
        res = []
        for fin_rec in res_find:
            res.append((fin_rec.id, fin_rec.name))
        return res

    @api.onchange('schedule')
    def _onchange_schedule(self):
        for rec in self:
            find_count = self.search_count([('schedule', '=', rec.schedule),
                                            ('id', '!=', rec.id)])
            if find_count > 0:
                raise ValidationError(_('This time is already taken'))

    @api.onchange('doctor_id', 'date')
    def _set_done(self):
        self.cron_done()

    @api.constrains('active')
    def _constrains_date(self):
        for rec in self:
            if len(rec.disease_ids) > 0 and (not rec.active):
                raise ValidationError(_('You cannot archive '
                                        'a visit with a diagnosis'))

    @api.ondelete(at_uninstall=False)
    def _ondelete_patient_visit(self):
        for rec in self:
            if len(rec.disease_ids) > 0:
                raise ValidationError(_('You cannot delete '
                                        'a visit with a diagnosis'))

    @api.constrains('diagnosis_ids')
    def _constrains_mentor(self):
        for rec in self:
            for diag in self.diagnosis_ids:
                if rec.doctor_id != diag.doctor_id:
                    raise ValidationError(_('Intern ' + rec.name +
                                            ' cannot be a mentor'))
