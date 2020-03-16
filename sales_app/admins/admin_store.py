# Define
from sales_app.define import *


# Models
from sales_app.models import *

# Eatple App Models
from eatple_app.system.model_type import STORE_AREA

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


class CRNInline(CompactInline):
    verbose_name = "사업자 등록번호"
    verbose_name_plural = "사업자 등록번호"

    model = CRN
    max_num = 1
    extra = 0

    readonly_fields = ('CRN_id',)


class PlaceInline(CompactInline):
    verbose_name = "장소"
    verbose_name_plural = "장소"

    model = Place
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


class StoreSalesResource(resources.ModelResource):
    def dehydrate_name(self, obj):
        return obj.name

    def dehydrate_phone_number(self, obj):
        return obj.phone_number.as_national

    def dehydrate_area(self, obj):
        return dict(STORE_AREA)[obj.area]

    def dehydrate_category(self, obj):
        if(obj.category.exists()):
            categoryList = ''
            for category in obj.category.all():
                categoryList += "{} ,".format(category.name)

            categoryList = replaceRight(categoryList, ",", "", 1)
            return categoryList
        else:
            return "미등록"

    def dehydrate_tag(self, obj):
        if(obj.tag.exists()):
            tagList = ''
            for tag in obj.tag.all():
                tagList += "{} ,".format(tag.name)

            tagList = replaceRight(tagList, ",", "", 1)
            return tagList
        else:
            return "미등록"

    def dehydrate_level(self, obj):
        return dict(MEMBER_LEVEL_TYPE)[obj.level]

    def dehydrate_customer_level(self, obj):
        return dict(UP_AND_LOW_LEVEL_TYPE)[obj.customer_level]

    def dehydrate_progress_level(self, obj):
        return dict(PROGRESS_LEVEL_TYPE)[obj.progress_level]

    id = Field(attribute='id', column_name='ID')
    name = Field(attribute='name', column_name='점포명')

    area = Field(attribute='area', column_name='지역')
    addr = Field(attribute='addr', column_name='주소')

    category = Field(attribute='category', column_name='가게 분류')
    tag = Field(attribute='tag', column_name='분류 - 세부')

    owner = Field(attribute='owner', column_name='담당자')
    level = Field(attribute='level', column_name='직급')
    phone_number = Field(attribute='phone_number', column_name='연락처')
    store_memo = Field(attribute='store_memo', column_name='상점 메모')

    progress_level = Field(attribute='progress_level', column_name='진척도')
    sales_memo = Field(attribute='sales_memo', column_name='영업 메모')

    customer_level = Field(attribute='customer_level', column_name='우호도')
    customer_memo = Field(attribute='customer_memo', column_name='특이사항')

    class Meta:
        model = Store

        exclude = (
            'pickup_time',
            'container_support',
            'spoon_support',
            'plastic_bag_support',
        )


class StoreAdmin(ImportExportMixin, admin.GeoModelAdmin):
    resource_class = StoreSalesResource
    list_per_page = 50

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
        'partnership_manager',
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
                    'menu', 'price', 'pickup_time', 'container_support', 'spoon_support', 'plastic_bag_support', 'store_memo',
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
        'partnership_manager',
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
        'partnership_manager',
    )

    search_fields = [
        'name',
        'owner',
        'phone_number',
        'member__name',
        'member__phone_number',
    ]

    inlines = [RecordInline, MemberInline]
