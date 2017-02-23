# -*- coding: utf-8 -*-
##############################################################################
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Odoo Medical, HMS Opensource Solution
##############################################################################

{
    'name': 'Medical Physician Schedule',
    "description":"""\
Medical Module Modification
==================================

    """,
    'version': '8.0.1.1.0',
    'category': 'Medical',
    'depends': [
        'jmedical',
    ],
    'author': 'John Winston Viloria Amaris',
    'license': 'AGPL-3',
    'data': [
        'views/medical_physician_schedule_template_view.xml',
        'views/medical_appointment_view.xml',
        'security/ir.model.access.csv',
        'medical_appointment_data.xml',
    ],
    'installable': True,
    'auto_install': False,
}
