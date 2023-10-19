from odoo import fields, models
from odoo.tools import date_utils


class HospitalReportDiseaseWizard(models.TransientModel):
    _name = 'hospital.report.disease.wizard'
    _description = 'Hospital disease report for the month'

    date_month = fields.Date(string='month from date')

    def generate_report_method(self):
        self.env['hospital.report.disease.line'].sudo().search([]).unlink()

        diagnosis_ids = self.env['hospital.diagnosis'].sudo().search(
            [('date', '>=', date_utils.start_of(self.date_month, "month")),
             ('date', '<=', date_utils.end_of(self.date_month, "month"))])
        for diagnosis in diagnosis_ids:
            for disease in diagnosis.disease_ids:
                self.env['hospital.report.disease.line'].sudo().create({
                    'doctor_id': diagnosis.doctor_id.id,
                    'patient_id': diagnosis.patient_id.id,
                    'disease_id': disease.id,
                    'date': diagnosis.date,
                    'wizard_id': self.id
                })

        return {'name': 'Generate report method',
                'type': 'ir.actions.act_window',
                'view_mode': 'list',
                'res_model': 'hospital.report.disease.line',
                'target': 'inline'}


class HospitalReportDiseaseLine(models.TransientModel):
    _name = 'hospital.report.disease.line'
    _description = 'Data selection for the report'

    doctor_id = fields.Many2one(comodel_name='hospital.doctor')
    patient_id = fields.Many2one(comodel_name='hospital.patient')
    disease_id = fields.Many2one(comodel_name='hospital.disease')
    date = fields.Date()

    wizard_id = fields.Many2one(comodel_name='hospital.report.disease.wizard')
