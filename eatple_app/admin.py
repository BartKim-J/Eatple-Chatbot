# Django Library
from django.contrib import admin
from django import forms
from django.core import validators
from django.utils.translation import ugettext_lazy as _

# Models
from .models import *


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


class PickupTimeInline(admin.TabularInline):
    model = PickupTime
    extra = 0
    min_num = 2

    fieldsets = [
        (None, {'fields': ['status', 'time']}),
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

    inlines = [CRNInline, MenuInline, PickupTimeInline]


admin.site.register(Store, StoreAdmin)


class OrderInline(admin.TabularInline):
    readonly_fields = ('order_code', 'menu', 'count', 'store',
                       'order_date', 'pickup_time')

    model = Order
    extra = 0
    min_num = 1

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderSheetAdmin(admin.ModelAdmin):
    readonly_fields = ('management_code', 'user', 'order_date', 'update_date')

    list_filter = ('order_date',)
    list_display = ('management_code', 'user', 'order_date', 'update_date')

    inlines = [OrderInline]


admin.site.register(OrderSheet, OrderSheetAdmin)


class OrderRecordInline(admin.TabularInline):
    model = OrderRecord
    extra = 0
    min_num = 0

    readonly_fields = ('status', 'record_date', )


class OrderRecordSheetAdmin(admin.ModelAdmin):
    readonly_fields = ('status', 'created_date', 'update_date')

    list_filter = ('update_date', 'created_date')
    list_display = ('status', 'user', 'created_date', 'update_date')

    inlines = [OrderRecordInline]


admin.site.register(OrderRecordSheet, OrderRecordSheetAdmin)

# Main Models
admin.site.register(Partner)


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('app_user_id', 'nickname', 'profile_image_url',
                       'phone_number', 'email', 'birthyear', 'birthday', 'gender', 'ci', 'ci_authenticated_at')

    list_filter = ('create_date', 'gender')
    list_display = ('app_user_id', 'nickname',
                    'phone_number', 'email', 'gender')


admin.site.register(User, UserAdmin)


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
