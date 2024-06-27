from odoo import fields, models, _, api
from odoo.tools import date_utils


class HospitalReportDiseaseWizard(models.TransientModel):
    _name = 'hospital.report.disease.wizard'
    _description = 'Hospital disease report for the month'

    name = fields.Char(compute='_compute_report_name')
    date_month = fields.Date(string='month from date')
    detail_report = fields.Boolean(string='Detail')
    report_lines_ids = fields.One2many(comodel_name='hospital.report.disease.line', inverse_name='wizard_id')

    def get_data_report(self):
        self.report_lines_ids.unlink()
        domain_month = [('date', '>=', date_utils.start_of(self.date_month, "month")),
                        ('date', '<=', date_utils.end_of(self.date_month, "month"))]
        diagnosis_ids = self.env['hospital.diagnosis'].sudo().search(domain_month)
        for diagnosis in diagnosis_ids:
            for disease in diagnosis.disease_ids:
                if self.detail_report:
                    self.report_lines_ids.create({'doctor_id': diagnosis.doctor_id.id,
                                                  'patient_id': diagnosis.patient_id.id,
                                                  'disease_id': disease.id,
                                                  'date': diagnosis.date,
                                                  'wizard_id': self.id})
                else:
                    domain = [('disease_id', '=', disease.id), ('wizard_id', '=', self.id)]
                    disease_find = self.report_lines_ids.search(domain)
                    if bool(disease_find.ids) is False:
                        self.report_lines_ids.create({'doctor_id': False,
                                                      'patient_id': False,
                                                      'disease_id': disease.id,
                                                      'date': False,
                                                      'wizard_id': self.id})
                    else:
                        for rec in disease_find:
                            rec.disease_count += 1

    def get_data_report_old(self):
        self.env['hospital.report.disease.line'].sudo().search([]).unlink()

        domain_month = [('date', '>=', date_utils.start_of(self.date_month, "month")),
                        ('date', '<=', date_utils.end_of(self.date_month, "month"))]
        diagnosis_ids = self.env['hospital.diagnosis'].sudo().search(domain_month)
        for diagnosis in diagnosis_ids:
            for disease in diagnosis.disease_ids:
                if self.detail_report:
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

        if self.detail_report:
            report_name = 'Generate report detail'
        else:
            report_name = 'Generate report'
        return {'name': report_name,
                'type': 'ir.actions.act_window',
                'view_mode': 'list',
                'res_model': 'hospital.report.disease.line',
                'target': 'inline'}

    def generate_report(self):
        return self.get_data_report()

    @api.depends('date_month')
    def _compute_report_name(self):
        self.name = _('Diseases during the period ')
        if self.date_month is not False:
            month = date_utils.get_month(self.date_month)
            self.name += str(month[0].day) + ' - ' + str(month[1].day) + ' ' + self.date_month.strftime('%B %Y')
        # self.name = str(month[0].day) + ' - ' + str(month[1].day) + ' ' + self.date_month.strftime('%B %Y')


class HospitalReportDiseaseLine(models.TransientModel):
    _name = 'hospital.report.disease.line'
    _description = 'Data selection for the report'

    doctor_id = fields.Many2one(comodel_name='hospital.doctor')
    patient_id = fields.Many2one(comodel_name='hospital.patient')
    disease_id = fields.Many2one(comodel_name='hospital.disease')
    disease_count = fields.Integer(default=1, string='Quantity')
    date = fields.Date()

    wizard_id = fields.Many2one(comodel_name='hospital.report.disease.wizard')
