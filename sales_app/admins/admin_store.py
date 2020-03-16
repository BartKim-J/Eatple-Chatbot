# Define
from sales_app.define import *

# Models
from sales_app.models import *

# Django Library
from django.contrib.gis import admin
from django.contrib.gis import forms
from django.contrib.gis.db import models

from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe


class TypeFilter(MultipleChoiceListFilter):
    title = '유형'
    parameter_name = 'type__in'

    def lookups(self, request, model_admin):
        return STORE_TYPE


class CRNInline(admin.TabularInline):
    verbose_name = "사업자 등록번호"
    verbose_name_plural = "사업자 등록번호"

    model = CRN
    extra = 0

    readonly_fields = ('CRN_id',)


class PlaceInline(admin.TabularInline):
    verbose_name = "장소"
    verbose_name_plural = "장소"

    model = Place
    min_num = 1

    formfield_overrides = {
        models.PointField: {"widget": GoogleStaticMapWidget}
    }


class RecordInline(admin.StackedInline):
    verbose_name = "영업 활동 내역"
    verbose_name_plural = "영업 활동 내역"

    model = SalesRecord
    extra = 0

    readonly_fields = ('store', )


class StoreAdmin(ImportExportMixin, admin.GeoModelAdmin):
    def phonenumber(self, obj):
        return obj.phone_number.as_national
    phonenumber.short_description = "전화번호"

    list_editable = ('progress_level', )

    fieldsets = [
        (
            '기본 정보',
            {
                'fields': [
                    'name', 'addr', 'owner', 'phone_number'
                ]
            }
        ),
        (
            '점포 정보',
            {
                'fields': [
                    'category', 'tag', 'description',
                ]
            }
        ),
        (
            '영업 상태',
            {
                'fields': ['progress_level',]
            }
        ),
    ]


    list_filter = (
        'progress_level',
    )

    list_display = (
        'name',
        'phonenumber',
        'progress_level',
    )

    search_fields = ['name']

    inlines = [PlaceInline, RecordInline, CRNInline]
