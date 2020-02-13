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
    readonly_fields = (
        'nickname',
        'app_user_id',
        'phone_number',
        'email',
        'birthyear',
        'birthday',
        'gender',
        'ci',
        'ci_authenticated_at'
    )

    search_fields = ['nickname', 'app_user_id',
                     'phone_number']

    list_filter = (
        ('create_date', DateRangeFilter),
        'type',
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

    list_display = (
        'store',
        'type',
        'nickname',
        'phonenumber',
        'crn',
    )
