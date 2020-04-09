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


class PartnerAdmin(ImportExportMixin, admin.ModelAdmin):
    list_per_page = 50

    readonly_fields = (
        'nickname',
        'app_user_id',
        'phonenumber',
        'email',
        'birthyear',
        'birthday',
        'gender',
        'ci',
        'ci_authenticated_at',
        'create_date',
    )

    def crn(self, obj):
        if(obj.store != None):
            return obj.store.crn
        else:
            return "상점 미등록"
    crn.short_description = "사업자 등록번호"

    def phonenumber(self, obj):
        return obj.phone_number.as_national
    phonenumber.short_description = "전화번호"

    fieldsets = [
        (
            '기본 정보',
            {
                'fields': [
                    'store',
                    'app_user_id',
                    'nickname',
                    'phonenumber',
                    'email',
                    'create_date',
                ]
            }
        ),
        (
            '사용자 플래그',
            {
                'fields': [
                    'type',
                    'is_inactive',
                    'is_staff',
                ]
            }
        ),
        (
            '카카오 연동 정보',
            {
                'fields': [
                    'birthyear',
                    'birthday',
                    'gender',
                    'ci',
                    'ci_authenticated_at',
                ]
            }
        ),
    ]

    search_fields = [
        'nickname',
        'app_user_id',
        'phone_number'
    ]

    list_filter = (
        ('create_date', DateRangeFilter),
        'type',
        'is_staff',
    )

    list_editable = (
        'is_staff',
        'is_inactive',
    )

    list_display = (
        'store',
        'type',
        'nickname',
        'app_user_id',
        'phonenumber',
        'crn',
        'is_staff',
        'is_inactive',
    )
