
from collections import Counter

from odoo import fields, models, _, api
from odoo.tools import date_utils


class ReportDiseaseWizard(models.TransientModel):
    _name = 'report.disease.wizard'
    _description = 'Getting parameters for report disease for the month'

    name = fields.Char(compute='_compute_name')
    date_month = fields.Date(string='month from date')
    detail_report = fields.Boolean(string='Detail')

    @api.depends('date_month')
    def _compute_name(self):
        self.name = _('Diseases during the period ')
        if self.date_month is not False:
            month = date_utils.get_month(self.date_month)
            self.name += str(month[0].day) + ' - ' + str(month[1].day) + ' ' + self.date_month.strftime('%B %Y')
        if self.detail_report:
            self.name += ' (detail)'

    def generate_report(self):
        data = {'date_start': date_utils.start_of(self.date_month, "month"),
                'date_end': date_utils.end_of(self.date_month, "month"),
                'report_name': self.name,
                'detail_report': self.detail_report}
        return self.env.ref('odoo_school_hr_hospital.action_report_disease').report_action(self, data)


class ReportDisease(models.AbstractModel):
    _name = 'report.odoo_school_hr_hospital.report_disease_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['date_start']
        date_end = data['date_end']
        detail_report = data['detail_report']
        diagnosis_ids = self.env['hospital.diagnosis'].sudo().search([('date', '>=', date_start), ('date', '<=', date_end)])
        results = []
        if detail_report:
            for diagnos in diagnosis_ids:
                for disease in diagnos.disease_ids:
                    results.append({'doctor_id': diagnos.doctor_id,
                                    'patient_id': diagnos.patient_id,
                                    'disease_id': disease,
                                    'date': diagnos.date,
                                    'disease_count': False})
        else:
            disease_ids = diagnosis_ids.mapped('disease_ids').ids  # Отримуємо всі хвороби з діагнозів
            # disease_counts = self.env['hospital.disease'].sudo().read_group(domain=[('id', 'in', disease_ids)],
            #                                                                 fields=['id'],  # Отримуємо id хвороби
            #                                                                 groupby=['id'])  # Групуємо за id хвороби
            disease_counts = Counter(disease_ids)
            diseases = self.env['hospital.disease'].sudo().search([('id', 'in', disease_ids)])
            # for record in disease_counts:
            for id_value, id_count in disease_counts.items():
                results.append({'doctor_id': False,
                                'patient_id': False,
                                # 'disease_id': diseases.browse(record['id']),
                                'disease_id': diseases.browse(id_value),
                                'date': False,
                                # 'disease_count': record['__count']})
                                'disease_count': id_count})
        return {'doc_ids': docids,
                'doc_model': 'report.disease',
                'docs': results,
                'data': data, }
