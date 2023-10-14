from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HospitalDoctor(models.Model):
    _name = 'hospital.doctor'
    _description = 'Hospital Doctor'
    _inherit = {'hospital.person'}

    specialty = fields.Char(required=True)
    intern_ids = fields.One2many(comodel_name='hospital.doctor',
                                 inverse_name='mentor_id', string='Interns')
    mentor_id = fields.Many2one(comodel_name='hospital.doctor')

    @api.constrains('mentor_id')
    def _constrains_mentor(self):
        found_sp = self.search([('mentor_id.id', '!=', False)])
        for rec in found_sp:
            if rec == self.mentor_id:
                raise ValidationError(_('Intern ' + rec.name +
                                        ' cannot be a mentor'))
