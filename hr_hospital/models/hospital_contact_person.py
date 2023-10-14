# from odoo import models, fields, api
from odoo import models


class ContactPerson(models.Model):
    _name = 'hospital.contact.person'
    _description = 'Hospital Contact Person'
    _inherit = {'hospital.person'}
