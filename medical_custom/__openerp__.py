# -*- coding: utf-8 -*-
##############################################################################
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Odoo Medical, HMS Opensource Solution
##############################################################################

{
    'name': 'Odoo Medical Colombia Setup',
    "description":"""\
Medical Module Modification
==================================

    """,
    'version': '8.0.1.1.0',
    'category': 'Medical',
    'depends': [
        'medical','base','medical_disease','jmedical_emr',
    ],
    'author': 'John Winston Viloria Amaris',
    'license': 'AGPL-3',
    'data': [
        'views/medical_appointment_view.xml',
        'views/medical_patient_view.xml',
        'views/medical_pathology_view.xml',
        'res.country.state.csv',
        'res.country.state.city.csv',
        'medical.patient.occupation.csv',
        'medical.specialty.csv',
        'security/ir.model.access.csv',
        'views/report_layouts.xml',
        'views/medical_eapb_view.xml',
        'views/medical_eapb_order_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
