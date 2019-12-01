# Models
from .models import *

# Django Library
from django.contrib import admin
from django import forms
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from import_export.admin import ExportActionModelAdmin, ImportExportMixin, ImportMixin
from import_export import resources

class CRNInline(admin.TabularInline):
    model = CRN
    min_num = 1


class MenuInline(admin.StackedInline):
    model = Menu
    extra = 0
    min_num = 1

    readonly_fields = ('menu_id', "image_preview")

    def image_preview(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url=obj.image.url,
            width=obj.image.width * 0.4,
            height=obj.image.height * 0.4,
        )
    )
        
    fieldsets = [
        (None,                  {'fields': ['menu_id']}),
        (None,                  {'fields': ['name']}),
        (None,                  {'fields': [
         'sellingTime', 'tag', 'description', 'image','image_preview', 'price', 'discount']}),
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


class StoreAdmin(ImportExportMixin, admin.ModelAdmin):
    readonly_fields = ('store_id', 'logo_preview')

    list_editable = ('status',)

    fieldsets = [
        (None,                   {'fields': ['store_id']}),
        ('Information',          {'fields': ['name', 'addr', 'owner' ,'phone_number']}),
        ('Setting',              {'fields': ['category', 'description', 'logo', 'logo_preview']}),
        ('Status',               {'fields': ['status']}),
    ]

    def logo_preview(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url=obj.logo.url,
            width=58,
            height=58,
        )
    )

    list_filter = ('status',)
    list_display = ('name', 'status', 'store_id', 'crn')

    inlines = [CRNInline, MenuInline, PickupTimeInline]


admin.site.register(Store, StoreAdmin)


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


admin.site.register(OrderSheet, OrderSheetAdmin)


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


admin.site.register(Order, OrderAdmin)


class OrderRecordInline(admin.TabularInline):
    model = OrderRecord
    extra = 0
    min_num = 0

    readonly_fields = ('status', 'record_date', )


class OrderRecordSheetAdmin(ImportExportMixin, admin.ModelAdmin):
    readonly_fields = ('user', 'menu', 'status', 'created_date', 'update_date')

    list_filter = ('update_date', 'created_date')
    list_display = ('status', 'user', 'created_date', 'update_date')

    inlines = [OrderRecordInline]


admin.site.register(OrderRecordSheet, OrderRecordSheetAdmin)

# Main Models
admin.site.register(Partner)


class UserAdmin(ImportExportMixin, admin.ModelAdmin):
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
