# Django Library
from django.contrib import admin
from django import forms
from django.core import validators
from django.utils.translation import ugettext_lazy as _

# Models
from .models import DefaultImage
from .models import UserManual, PartnerManual
from .models import UserIntro, PartnerIntro
from .models import Store, CRN
from .models import Menu
from .models import Category, Tag
from .models import Order, OrderSheet
from .models import User
from .models import Partner


class CRNInline(admin.TabularInline):
    model = CRN
    min_num = 1


class MenuInline(admin.StackedInline):
    model = Menu
    extra = 0
    min_num = 1

    readonly_fields = ('menu_id',)

    fieldsets = [
        (None,                  {'fields': ['menu_id']}),
        (None,                  {'fields': ['name']}),
        (None,                  {'fields': [
         'sellingTime', 'tag', 'description', 'image', 'price', 'discount']}),
        (None,                  {'fields': [
         'current_stock', 'max_stock', 'status']}),
    ]


class StoreAdmin(admin.ModelAdmin):
    readonly_fields = ('store_id',)

    list_editable = ('status',)

    fieldsets = [
        (None,                   {'fields': ['store_id']}),
        ('Information',          {'fields': ['name', 'addr', 'owner']}),
        ('Setting',              {'classes': ('collapse',),
                                  'fields': ['description', 'logo']}),
        ('Status',               {'fields': ['status']}),
    ]

    list_filter = ('status',)
    list_display = ('name', 'status', 'store_id', 'crn')

    inlines = [CRNInline, MenuInline]


admin.site.register(Store, StoreAdmin)


class OrderInline(admin.TabularInline):
    readonly_fields = ('order_code', 'menu',  'store',
                       'order_date', 'pickup_time')

    model = Order
    extra = 0
    min_num = 1

class OrderSheetAdmin(admin.ModelAdmin):
    readonly_fields = ('management_code', 'user', 'order_date', 'update_date')
    
    list_filter = ('order_date',)
    list_display = ('management_code', 'user', 'order_date', 'update_date')
    
    inlines = [OrderInline]


admin.site.register(OrderSheet, OrderSheetAdmin)

# Main Models
admin.site.register(Partner)
admin.site.register(User)


# Defulat Images
admin.site.register(DefaultImage)

# Menu Category-Tag
admin.site.register(Category)
admin.site.register(Tag)

# Manual
# admin.site.register(UserManual)
# admin.site.register(PartnerManual)

# Intro
# admin.site.register(UserIntro)
# admin.site.register(PartnerIntro)
