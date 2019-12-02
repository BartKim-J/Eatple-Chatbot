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

class CRNInline(admin.TabularInline):
    model = CRN
    min_num = 1

    readonly_fields = ('CRN_id',)

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