
from odoo import fields, models, _, api
from odoo.exceptions import UserError


class HospitalAnalysis(models.Model):
    # Аналізи
    _name = 'hospital.analysis'
    _description = 'Hospital Analysis'

    state = fields.Selection(selection=[('plan', 'Is planned'), ('done', 'Done')], default='plan', required=True)
    patient_id = fields.Many2one(comodel_name='hospital.patient', required=True, readonly=False, states={'done': [('readonly', True)]})
    date_referral = fields.Datetime(required=True, readonly=False, states={'done': [('readonly', True)]})
    date_passing = fields.Datetime(string='Date of passing', readonly=False, states={'done': [('readonly', True)]})
    doctor_referral_id = fields.Many2one(comodel_name='hospital.doctor', required=True, readonly=False, states={'done': [('readonly', True)]})
    doctor_who_did_id = fields.Many2one(string='Doctor who did the analysis', comodel_name='hospital.doctor', readonly=False, states={'done': [('readonly', True)]})
    type = fields.Selection(selection=[('blood_general', 'general blood test'),
                                       ('blood_comp', 'comprehensive blood analysis'),
                                       ('urine', 'urine analysis')],
                            required=True, readonly=False, states={'done': [('readonly', True)]})
    indicator_value_ids = fields.One2many(comodel_name='hospital.analysis.indicator.value', inverse_name='analysis_id')

    def name_get(self):
        result = []
        for rec in self:
            type_label = dict(self._fields['type'].selection).get(rec.type)
            if rec.date_passing is False:
                result.append((rec.id, f'{type_label} - patient: {rec.patient_id.name} at {rec.date_referral}'))
            else:
                result.append((rec.id, f'{type_label} - patient: {rec.patient_id.name} at {rec.date_passing}'))
        return result


class HospitalAnalysisIndicator(models.Model):
    # Показники аналізів
    _name = 'hospital.analysis.indicator'
    _description = 'Hospital analysis indicator'

    name = fields.Char(required=True)
    limit_lower = fields.Float(string='Lower limit of the norm', digits=(15, 3))
    limit_upper = fields.Float(string='Upper limit of the norm', digits=(15, 3))

    def write(self, vals):
        if 'name' in vals:
            for record in self:
                if record.name:
                    raise UserError(_("You cannot change the value of this field for an existing record."))
        return super().write(vals)


class HospitalAnalysisIndicatorValue(models.Model):
    # Значення показників аналізів
    _name = 'hospital.analysis.indicator.value'
    _description = 'Values of analysis indicators'

    analysis_indicator = fields.Many2one(comodel_name='hospital.analysis.indicator', required=True)
    analysis_indicator_limit_lower = fields.Float(string='norm min', compute='_compute_analysis_indicator_limit')
    analysis_indicator_limit_upper = fields.Float(string='norm max', compute='_compute_analysis_indicator_limit')
    analysis_indicator_limit_norm = fields.Char(string='norm', compute='_compute_analysis_indicator_limit')
    indicator_value = fields.Float(digits=(15, 3))
    comment = fields.Char()
    analysis_id = fields.Many2one(comodel_name='hospital.analysis', required=True)

    def name_get(self):
        return [(rec.id, f'{rec.analysis_indicator.name}: {rec.indicator_value}') for rec in self]

    @api.depends('analysis_indicator')
    def _compute_analysis_indicator_limit(self):
        for rec in self:
            if rec.analysis_indicator is False:
                rec.analysis_indicator_limit_upper = 0
                rec.analysis_indicator_limit_lower = 0
                rec.analysis_indicator_limit_norm = ''
            else:
                rec.analysis_indicator_limit_upper = rec.analysis_indicator.limit_upper
                rec.analysis_indicator_limit_lower = rec.analysis_indicator.limit_lower
                rec.analysis_indicator_limit_norm = f'({rec.analysis_indicator.limit_lower:.3f} - {rec.analysis_indicator.limit_upper:.3f})'
