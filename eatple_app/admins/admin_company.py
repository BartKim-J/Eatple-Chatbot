# Define
from eatple_app.define import *

# Models
from eatple_app.models import *

# Django Library
from django.contrib.gis import admin
from django.contrib.gis import forms
from django.contrib.gis.db import models

from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe


class CRNInline(admin.TabularInline):
    model = CompanyCRN
    min_num = 1

    readonly_fields = ('CRN_id',)


class PlaceInline(admin.TabularInline):
    model = CompanyPlace
    min_num = 1

    formfield_overrides = {
        models.PointField: {"widget": GooglePointFieldWidget}
    }


class CompanyAdmin(ImportExportMixin, admin.GeoModelAdmin):
    readonly_fields = ('company_id', 'logo_preview')

    list_editable = ('status', )

    fieldsets = [
        ('기본 정보',            {'fields': [
         'company_id', 'name', 'addr', 'phone_number']}),
        ('설정',                 {'fields': ['logo', 'logo_preview']}),
        ('상태',                 {'fields': ['status']}),
    ]

    def logo_preview(self, obj):
        return mark_safe(
            '<img src="{url}" width="{width}" height={height} />'.format(
                url=obj.logo.url,
                width=58,
                height=58,
            )
        )
    logo_preview.short_description = "이미지 미리보기"

    search_fields = ['name', 'phone_number']

    list_filter = (
        'status',
    )

    list_display = (
        'name',
        'status',
        'company_id',
        'companycrn',
    )

    inlines = [PlaceInline, CRNInline]
