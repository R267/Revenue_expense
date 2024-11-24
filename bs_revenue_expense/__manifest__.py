# -*- coding: utf-8 -*-
{
    'name': 'BonSens Revenue and Expense',
    'summary': """ BonSens for Revenue and Expense """,
    'description': """ BonSens for Revenue and Expense """,
    'author': "BonSens",
    'website': "https://www.bonsens.com.ua",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '17.0.1.0.1',
    # any module necessary for this one to work correctly
    'depends': ['base','account'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/bs_cost_item_views.xml',
        'views/bs_payment_expense_views.xml',
        'views/product_product_views.xml',
        'views/account_payment_views.xml',
        'views/hr_department_views.xml',
        'views/bs_payment_expense_entry_views.xml',
    ],
}
