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

class LanlngInline(admin.TabularInline):
    model = CRN
    min_num = 1

    readonly_fields = ('CRN_id',)

class CRNInline(admin.TabularInline):
    model = latlng
    min_num = 1

class MenuInline(admin.StackedInline):
    model = Menu
    extra = 0
    min_num = 1
    max_num = 2
    
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
         'sellingTime', 'pickupTime','tag', 'description', 'image','image_preview', 'price', 'discount']}),
        (None,                  {'fields': [
         'current_stock', 'max_stock', 'status']}),
    ]
    
class StoreAdmin(ImportExportMixin, admin.ModelAdmin):
    readonly_fields = ('store_id', 'logo_preview')

    list_editable = ('status', )

    fieldsets = [
        (None,                   {'fields': ['store_id']}),
        ('Information',          {'fields': ['name', 'addr', 'owner' ,'phone_number']}),
        ('Setting',              {'fields': ['category', 'description', 'logo', 'logo_preview']}),
        ('Status',               {'fields': ['status', 'type', 'area']}),
    ]

    def logo_preview(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url=obj.logo.url,
            width=58,
            height=58,
        )
    )

    list_filter = (
        ('status', ChoiceDropdownFilter), ('area', ChoiceDropdownFilter), ('type', ChoiceDropdownFilter)
    )
    
    list_display = ('name', 'status', 'store_id', 'crn', 'type', 'area', 'latlng')

    inlines = [LanlngInline, CRNInline, MenuInline]
