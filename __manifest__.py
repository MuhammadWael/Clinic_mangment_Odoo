# estate/__manifest__.py
{
    'name': "clinic",
    'version': '1.0',
    'depends': ['base'],
    'author': "Muhammad wael",
    'description': """
    Description text
    """,
    
    'data': [
        "security/ir.model.access.csv",
        "data/sequence_data.xml",
        "views/clinic_patient_views.xml",
        "views/clinic_menus.xml"
        
    ],
}
