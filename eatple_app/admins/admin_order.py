# Models
from eatple_app.models import *

# Django Library
from django.contrib import admin
from django import forms
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from import_export.admin import ExportActionModelAdmin, ImportExportMixin, ImportMixin
from import_export import resources

class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = (
            'order_id',
            'order_date',
            'totalPrice',
            'payment_status',
            'status',
            'store__name',
            'store__store_id',
            'menu__name',
            'menu__menu_id',
        )


class OrderAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = OrderResource

    readonly_fields = ('ordersheet', 'order_id', 'payment_status', 'status', 'totalPrice', 'menu', 'count', 'store',
                       'order_date', 'pickup_time')

    list_filter = ('order_date', 'store', 'menu', 'payment_status')
    list_display = ('order_id', 'store', 'menu',
                    'payment_status', 'status', 'order_date')
