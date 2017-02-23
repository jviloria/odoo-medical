# -*- coding: utf-8 -*-
##############################################################################
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Odoo Medical, HMS Opensource Solution
##############################################################################

{
    'name': 'Odoo Medical Patient Evaluation Modification',
    "description":"""\
Medical EMR module Modification
==================================

    """,    
    'version': '8.0.1.1.0',
    'category': 'Medical',
    'depends': [
        'medical_emr','medical','oemedical_socioeconomics',
    ],
    'author': 'John Winston Viloria Amaris',
    'license': 'AGPL-3',
    'data': [
        'jmedical_emr_report.xml',
        'views/medical_patient_view.xml',
        'views/medical_patient_evaluation_view.xml',
        'views/medical_patient_record_view.xml',
    	'medical.evaluation.type.csv',
        'security/ir.model.access.csv',
        'views/report_patient_evaluation.xml',
        'views/report_patient_evolution.xml',
        'views/medical_patient_evolution_view.xml',
        'views/medical_menu.xml',
        
    ],
    'installable': True,
    'auto_install': False,
}
