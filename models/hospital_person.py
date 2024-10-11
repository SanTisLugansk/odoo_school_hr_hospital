from odoo import fields, models


class HospitalPerson(models.AbstractModel):
    # Особи
    _name = 'hospital.person'
    _description = 'Hospital Person'

    name = fields.Char(string='Full name', required=True, size=200)
    phone = fields.Char(size=20)
    email = fields.Char(string='e-mail', size=100)
    photo = fields.Image(max_width=1980, max_height=1980, store=True)
    gender = fields.Selection(default='male', selection=[('male', 'Male'),
                                                         ('female', 'Female'),
                                                         ('other', 'Other / Underfined')])
