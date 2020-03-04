from django.urls import path, include

from eatple_app import templates

TEMPLATES_URLS = {
    path('', templates.dashboard),
    path('404', templates.error404),
    path('sales/dashboard', templates.sales_dashboard),
    path('sales/menu_list', templates.sales_menulist),
}
