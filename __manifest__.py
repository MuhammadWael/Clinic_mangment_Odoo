# estate/__manifest__.py
{
    'name': "clinic",
    'version': '1.0',
    'depends': ['base','account'],
    'author': "Muhammad wael",
    'description': """
    Description text
    """,
    
    'data': [
        "security/ir.model.access.csv",
        
        "data/sequence_data.xml",
        

        "views/clinic_patient_views.xml",
        "views/clinic_appointment_views.xml",
        "views/clinic_doctor_views.xml",
        "views/clinic_treatments_views.xml",
        "views/clinic_medical_record_views.xml",
        "views/clinic_prescription_views.xml",
        "views/clinic_account_views.xml",
        "views/clinic_log_views.xml",
        "views/clinic_menus.xml",

        "report/clinic_patient_report.xml",       
        "report/clinic_reports.xml"       
    ],
}
