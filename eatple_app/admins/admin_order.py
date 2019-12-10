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

class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = (
            'order_id',
            'order_date',
            'totalPrice',
            'type'
            'payment_status',
            'status',
            'store__name',
            'store__store_id',
            'menu__name',
            'menu__menu_id',
            'ordersheet__user__phone_number',
        )


class OrderAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = OrderResource

    def user(self, obj):
        return obj.ordersheet.user

    def phone_number(self, obj):
        return obj.ordersheet.user.phone_number

    readonly_fields = (
        'ordersheet', 
        'order_id', 
        'payment_status',  
        'totalPrice', 
        'menu', 
        'count', 
        'store',
        'order_date', 
        'pickup_time',
        'type',
    )

    list_filter = (
        'order_date', 
        ('store',  RelatedDropdownFilter),
        ('menu', RelatedDropdownFilter),
        ('payment_status', ChoiceDropdownFilter),
        ('status', ChoiceDropdownFilter),
    )
    

    list_display = ('user', 'order_id',  'store', 'menu', 'type',
                    'payment_status', 'status', 'order_date')
