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

class OrderRecordInline(admin.TabularInline):
    model = OrderRecord
    extra = 0
    min_num = 0

    readonly_fields = (
        'status', 
        'record_date', 
    )


class OrderRecordSheetAdmin(ImportExportMixin, admin.ModelAdmin):
    readonly_fields = (
        'user', 
        'menu', 
        'status', 
        'created_date', 
        'update_date'
    )

    list_filter = (
        'status', 
        ('menu', RelatedDropdownFilter),
        'update_date', 
        'created_date'
    )
    
    list_display = (
        'user', 
        'status', 
        'menu', 
        'created_date', 
        'update_date'
    )

    inlines = [OrderRecordInline]
