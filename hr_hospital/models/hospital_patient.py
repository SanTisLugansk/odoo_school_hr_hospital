from odoo import api, fields, models, _


class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Hospital Patient'
    _inherit = {'hospital.person'}

    date_of_birth = fields.Date()
    age = fields.Integer(compute='_compute_age')
    passport_data = fields.Text()
    contact_person_ids = fields.Many2many(
        comodel_name='hospital.contact.person')
    observing_doctor_id = fields.Many2one(comodel_name='hospital.doctor')
    history_ids = fields.One2many(comodel_name='hospital.doctor.change',
                                  inverse_name='patient_id')
    doctor_change_ids = fields.One2many(comodel_name='hospital.doctor.change',
                                        inverse_name='patient_id')
    diagnosis_ids = fields.One2many(comodel_name='hospital.diagnosis',
                                    inverse_name='patient_id')

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth is False:
                rec.age = 0
            else:
                today = fields.datetime.now()
                rec.age = today.year-rec.date_of_birth.year
                if rec.age > 0 and (rec.date_of_birth.month > today.month or
                                    (rec.date_of_birth.month == today.month and
                                     rec.date_of_birth.day > today.day)):
                    rec.age -= 1

    def write(self, vals):
        if 'observing_doctor_id' in vals:
            for rec in self:
                rec.write({
                    'history_ids': [(0, 0,
                                     {'date': fields.datetime.now(),
                                      'doctor_id': vals['observing_doctor_id'],
                                      'patient_id': rec.id})]})
        return super().write(vals)

    # @api.model
    @api.model_create_multi
    def create(self, vals_list):
        res = super(self).create(vals_list)
        for rec_res in res:
            if rec_res.observing_doctor_id:
                rec_res.write(dict(history_ids=[(0, 0, {'date': fields.datetime.now(),
                                                        'doctor_id': rec_res.observing_doctor_id.id,
                                                        'patient_id': rec_res.id})]))
        return res

    def hospital_change_doctor_multi_wizard_act_window(self):
        patient_ids = []
        for rec in self:
            patient_ids.append(rec.id)
        return {'name': _('Change observing doctor wizard'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'hospital.change.doctor.multi.wizard',
                'target': 'new',
                'context': {'default_patient_ids': patient_ids}}
