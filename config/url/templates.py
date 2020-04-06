from django.urls import path, include

from eatple_app import templates

TEMPLATES_URLS = [
    path('', templates.dashboard, name='index'),
    path('404', templates.error404),
    path('sales', templates.sales),
    path('sales/menu_list', templates.sales_menulist),
]
