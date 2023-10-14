from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HospitalDisease(models.Model):
    _name = 'hospital.disease'
    _description = 'Hospital Disease'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(string='Title', required=True)
    complete_name = fields.Char(compute='_compute_complete_name',
                                recursive=True, store=True)
    parent_id = fields.Many2one(comodel_name='hospital.disease', index=True,
                                ondelete='cascade')
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many(comodel_name='hospital.disease',
                                inverse_name='parent_id')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for rec in self:
            if rec.parent_id:
                rec.complete_name = \
                    f'{rec.parent_id.complete_name} / {rec.name}'
            else:
                rec.complete_name = rec.name

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive diseases.'))
