{
    'name': "Hospital",
    'summary': 'keeping records of doctors and users',

    'author': "O. Tischik",
    'website': "https://www.mywebsite.com",

    # Categories can be used to filter modules in modules listing
    # Check
    # https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'license': 'OPL-1',
    'version': '16.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',],

    # always loaded
    'data': ['security/ir.model.access.csv',
             'views/hospital_menu_views.xml',
             'views/hospital_disease_views.xml',
             'views/hospital_doctor_views.xml',
             'views/hospital_diagnosis_views.xml',
             'views/hospital_patient_visit_views.xml',
             'views/hospital_patient_views.xml',
             'views/hospital_doctor_change_views.xml',
             'views/hospital_doctor_schedule_views.xml',
             'views/hospital_change_doctor_multi_wizard_views.xml',
             'views/report_disease_wizard_views.xml',
             'views/hospital_change_doctor_appointment_wizard.xml',
             'views/hospital_fill_doctor_schedule_wizard_views.xml',

             'data/disease_data.xml',
             'report/report_disease.xml',
             ],
    # only loaded in demonstration mode
    'demo': ['demo/disease_demo.xml',
             'demo/doctor_demo.xml',
             'demo/patient_demo.xml', ],

    'images': ['static/description/icon.png'],
}
