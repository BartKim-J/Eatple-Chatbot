# Define
from eatple_app.define import *

# Models
from eatple_app.models import *

# Django Library
from django.contrib import admin
from django import forms
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

class OrderInline(ImportExportMixin, admin.TabularInline):
    """
        readonly_fields = ('order_id', 'payment_status', 'status', 'totalPrice', 'menu', 'count', 'store',
                       'order_date', 'pickup_time')
    """

    model = Order
    extra = 0
    min_num = 1

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderSheetAdmin(ImportExportMixin, admin.ModelAdmin):
    readonly_fields = ('management_code', 'user', 'create_date', 'update_date')

    list_filter = ('create_date',)
    list_display = ('management_code', 'user', 'create_date', 'update_date')

    inlines = [OrderInline]