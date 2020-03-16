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

from jet.admin import CompactInline


class TypeFilter(MultipleChoiceListFilter):
    title = '유형'
    parameter_name = 'type__in'

    def lookups(self, request, model_admin):
        return STORE_TYPE


class CRNInline(CompactInline):
    verbose_name = "사업자 등록번호"
    verbose_name_plural = "사업자 등록번호"

    model = CRN
    extra = 0

    readonly_fields = ('CRN_id',)


class PlaceInline(CompactInline):
    verbose_name = "장소"
    verbose_name_plural = "장소"

    model = Place
    min_num = 1
    max_num = 1
    extra = 0

    formfield_overrides = {
        models.PointField: {"widget": GoogleStaticMapWidget}
    }


class MemberInline(CompactInline):
    verbose_name = "직원 리스트"
    verbose_name_plural = "직원 리스트"

    model = Member
    extra = 0

    def phonenumber(self, obj):
        return obj.phone_number.as_national
    phonenumber.short_description = "전화번호"

    fieldsets = [
        (
            '직원 리스트',
            {
                'fields': [
                    'name', 'phone_number', 'level',
                ]
            }
        ),
    ]

    readonly_fields = ('store', )


class RecordInline(CompactInline):
    verbose_name = "영업 활동 내역"
    verbose_name_plural = "영업 활동 내역"

    model = SalesRecord
    extra = 0

    fieldsets = [
        (
            '기본 정보',
            {
                'fields': [
                    'activity_date', 'activity_memo', 'record_date',
                ]
            }
        ),
    ]

    readonly_fields = ('store', 'record_date')


class StoreAdmin(ImportExportMixin, admin.GeoModelAdmin):
    def field_phonenumber(self, obj):
        return obj.phone_number.as_national
    field_phonenumber.short_description = "연락처"

    def field_category(self, obj):
        if(obj.category.exists()):
            categoryList = ''
            for category in obj.category.all():
                categoryList += "{} ,".format(category.name)

            categoryList = replaceRight(categoryList, ",", "", 1)
            return categoryList
        else:
            return "미등록"
    field_category.short_description = "가게분류"

    def field_tag(self, obj):
        if(obj.tag.exists()):
            tagList = ''
            for tag in obj.tag.all():
                tagList += "{} ,".format(tag.name)

            tagList = replaceRight(tagList, ",", "", 1)
            return tagList
        else:
            return "미등록"
    field_tag.short_description = "분류-세부"

    def field_activity(self, obj):
        activityList = SalesRecord.objects.filter(store=obj)
        if(activityList.exists()):
            return activityList.first().activity_memo
        else:
            return "활동 기록 없음"
    field_activity.short_description = "최근 활동내역"

    def field_activity_date(self, obj):
        activityList = SalesRecord.objects.filter(store=obj)
        if(activityList.exists()):
            return activityList.first().activity_date
        else:
            return "활동 기록 없음"
    field_activity_date.short_description = "최근 활동내역"

    list_editable = (
        'progress_level',
    )

    fieldsets = [
        (
            '기본정보',
            {
                'fields': [
                    'name', 'area', 'addr', 'category', 'tag', 'owner', 'level', 'phone_number',
                ]
            }
        ),
        (
            '세부정보',
            {
                'fields': [
                    'pickup_time', 'container_support', 'spoon_support', 'plastic_bag_support', 'store_memo',
                ]
            }
        ),
        (
            '고객관리',
            {
                'fields': [
                    'customer_level', 'customer_memo'
                ]
            }
        ),
        (
            '영업현황',
            {
                'fields': [
                    'progress_level', 'sales_memo',
                ]
            }
        ),
    ]

    list_filter = (
        'progress_level',
        'area',
    )

    list_display = (
        'name',
        'area',
        'field_category',
        'field_tag',
        'owner',
        'field_phonenumber',
        'progress_level',
        'field_activity',
        'field_activity_date',
    )

    search_fields = [
        'name',
        'owner',
        'phone_number',
        'member__name',
        'member__phone_number',
    ]

    inlines = [RecordInline, MemberInline, CRNInline, PlaceInline, ]
