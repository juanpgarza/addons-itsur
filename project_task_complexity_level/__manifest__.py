# Copyright 2021 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Level of complexity of project tasks",
    "version": "15.0.1.0.0",
    "author": "juanpgarza",
    "website": "https://github.com/juanpgarza/addons-itsur",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list    
    "category": "Project",
    
    "license": "AGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["juanpgarza"],
    'depends': [
        'project'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/project_task_views.xml',
        'views/project_task_complexity_views.xml',        
    ],
    'installable': True,
}