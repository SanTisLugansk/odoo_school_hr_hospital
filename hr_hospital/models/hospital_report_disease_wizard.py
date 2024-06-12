from odoo import fields, models
from odoo.tools import date_utils


class HospitalReportDiseaseWizard(models.TransientModel):
    _name = 'hospital.report.disease.wizard'
    _description = 'Hospital disease report for the month'

    date_month = fields.Date(string='month from date')

    def get_data_report(self, detail=True):
        self.env['hospital.report.disease.line'].sudo().search([]).unlink()

        domain_month = [('date', '>=', date_utils.start_of(self.date_month, "month")),
                        ('date', '<=', date_utils.end_of(self.date_month, "month"))]
        diagnosis_ids = self.env['hospital.diagnosis'].sudo().search(domain_month)
        for diagnosis in diagnosis_ids:
            for disease in diagnosis.disease_ids:
                if detail:
                    self.env['hospital.report.disease.line'].sudo().create({'doctor_id': diagnosis.doctor_id.id,
                                                                            'patient_id': diagnosis.patient_id.id,
                                                                            'disease_id': disease.id,
                                                                            'disease_count': 1,
                                                                            'date': diagnosis.date,
                                                                            'wizard_id': self.id})
                else:
                    domain = [('disease_id', '=', disease.id)]
                    disease_count = self.env['hospital.report.disease.line'].sudo().search_count(domain)
                    if disease_count == 0:
                        self.env['hospital.report.disease.line'].sudo().create({'disease_id': disease.id,
                                                                                'disease_count': 1,
                                                                                'wizard_id': self.id})
                    else:
                        disease_find = self.env['hospital.report.disease.line'].sudo().search(domain)
                        disease_find.update({'disease_count': disease_find.disease_count + 1})

    def generate_report_detail(self):
        self.get_data_report(True)

        return {'name': 'Generate report detail',
                'type': 'ir.actions.act_window',
                'view_mode': 'list',
                'res_model': 'hospital.report.disease.line',
                'target': 'inline'}

    def generate_report(self):
        self.get_data_report(False)

        return {'name': 'Generate report',
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
    disease_count = fields.Integer()
    date = fields.Date()

    wizard_id = fields.Many2one(comodel_name='hospital.report.disease.wizard')

    def get_month_year(self):
        result = ''
        for rec in self:
            result += date_utils.get_month(rec.date)
            result += ' '
            result += rec.date.strftime('%Y')
            return result
        return result
