# -*- coding: utf-8 -*-
{
    'name': "pronto",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "juanpgarza",
    "license": "AGPL-3",
    'website': "https://github.com/juanpgarza/addons-itsur",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    "version": "15.0.1.3.0",

    # any module necessary for this one to work correctly
    'depends': [
                'base',
                'crm',
                'purchase',
                'sale_crm',
                'sale_margin',
                'stock',
                'stock_voucher',
                'stock_picking_invoice_link',
                'stock_ux',
                'product',
                'partner_manual_rank',
                'mail_activity_board',
                'project',
            ],

    # always loaded
    'data': [
        'views/report_deliveryslip.xml',
        'views/stock_quant_views.xml',
        'security/pronto_security.xml',
        'views/product_pricelist_item_history_views.xml',
        'views/project_task_views.xml',
        'views/mail_activity_view.xml',               
        'security/ir.model.access.csv',
        'views/company.xml',
        'views/crm_lead_views.xml',
        'views/report_stockpicking.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/sale_tipo_cliente_views.xml',
        'views/stock_picking_views.xml',
        'views/product_pricelist_item_views.xml',
        'views/product_template_views.xml',
        'views/res_users_views.xml',  
        'views/account_payment_group_views.xml',
        'wizards/update_price_views.xml',
        'data/product_stock_data.xml',
        'data/config_parameter.xml',
        'views/stock_location_views.xml',
        'views/report_stockpicking_operations.xml',        
        'data/pronto_data.xml',
        'wizards/stock_return_picking_views.xml',
        'views/stock_return_picking_reason_views.xml',
    ],
    'installable': True,
}
