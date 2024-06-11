from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HospitalDoctor(models.Model):
    # Лікарі
    _name = 'hospital.doctor'
    _description = 'Hospital Doctor'
    _inherit = {'hospital.person'}

    specialty = fields.Char(required=True)
    intern_ids = fields.One2many(comodel_name='hospital.doctor',
                                 inverse_name='mentor_id', string='Interns')
    mentor_id = fields.Many2one(comodel_name='hospital.doctor')

    @api.constrains('mentor_id')
    def _constrains_mentor(self):
        for rec in self:
            if rec.mentor_id._is_intern():
                raise ValidationError(_('Intern ' + rec.mentor_id.name +
                                        ' cannot be a mentor'))
            if rec._is_mentor() and rec.mentor_id.id:
                raise ValidationError(_('You cannot install a mentor for'
                                        ' a mentor ' + rec.name))

    def _is_intern(self):
        for rec in self:
            return bool(rec.mentor_id.id)

    def _is_mentor(self):
        for rec in self:
            found_count = self.search_count([('mentor_id.id', '=', rec.id)])
            return bool(found_count)
