{
    'name': "hospital",
    'summary': 'keeping records of doctors and users',

    'author': "O. Tischik",
    'website': "https://www.mywebsite.com",

    # Categories can be used to filter modules in modules listing
    # Check
    # https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'license': 'OPL-1',
    'version': '16.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hospital_menu.xml',
        'views/hospital_disease.xml',
        'views/hospital_doctor.xml',
        'views/hospital_patient.xml',
        'views/hospital_patient_visit.xml',
        'data/disease_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/doctor_demo.xml',
        'demo/patient_demo.xml',
    ],
}
