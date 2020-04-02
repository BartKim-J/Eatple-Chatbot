from django.urls import path, include

from eatple_app import templates

TEMPLATES_URLS = [
    path('aisthefuture', templates.dashboard),
    path('aisthefuture/404', templates.error404),
    path('aisthefuture/sales/dashboard', templates.sales_dashboard),
    path('aisthefuture/sales/menu_list', templates.sales_menulist),
]
