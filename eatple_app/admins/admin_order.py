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
    
    def store_name(self,obj):
        return obj.store.name
    
    def menu_name(self, obj):
        return obj.menu.name
    
    class Meta:
        model = Order
        fields = (
            'order_id',
            'order_date',
            'payment_date',
            'totalPrice',
            'type'
            'payment_status',
            'status',
            'store_name',
            'store__name',
            'store__store_id',
            'menu_name',
            'menu__name',
            'menu__menu_id',
            'ordersheet__user__phone_number',
        )


class OrderAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = OrderResource

    def user(self, obj):
        return obj.ordersheet.user

    def nickname(self, obj):
        return obj.ordersheet.user.nickname

    def phone_number(self, obj):
        return obj.ordersheet.user.phone_number
    
    search_fields = ['order_id', 'ordersheet__user__nickname', 'ordersheet__user__app_user_id']

    readonly_fields = (
        'ordersheet', 
        'order_id', 
        'totalPrice', 
        'order_date', 
        'payment_date',
        'pickup_time',
    )
    
    list_filter = (
        ('order_date', DateRangeFilter), 
        ('payment_date', DateRangeFilter),
        ('store',  RelatedDropdownFilter),
        ('menu', RelatedDropdownFilter),
        ('payment_status', ChoiceDropdownFilter),
        ('status', ChoiceDropdownFilter),
        ('type', ChoiceDropdownFilter),
    )
    

    list_display = ('user', 'order_id',  'store', 'menu', 'type',
                    'payment_status', 'status', 'payment_date')
