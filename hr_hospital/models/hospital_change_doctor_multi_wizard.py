from odoo import fields, models


class HospitalChangeDoctorMultiWizard(models.TransientModel):
    _name = 'hospital.change.doctor.multi.wizard'
    _description = 'Hospital wizard to change observing doctors'

    patient_ids = fields.Many2many(comodel_name='hospital.patient',
                                   string='Patients')
    doctor_id = fields.Many2one(comodel_name='hospital.doctor')

    def action_change_observing_doctor(self):
        for rec in self:
            rec.write({'patient_ids': [(1, rec.patient_ids.ids, {'observing_doctor_id': rec.doctor_id.id})]})
