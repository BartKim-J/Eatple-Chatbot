from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.core import validators
from django import forms
from django.contrib import admin
from eatple_app.models import *
from eatple_app.define import *
# Define

# Models

# Django Library


class SurveyAdmin(ImportExportMixin, admin.ModelAdmin):

    def field_app_user_id(self, obj):
        if(obj.user.app_user_id != None):
            return obj.user.app_user_id
        else:
            return '미등록'
    field_app_user_id.short_description = '계정 고유 번호'

    def field_phonenumber(self, obj):
        print(obj.user)
        if(obj.user.phone_number != None):
            return obj.user.phone_number.as_national
        else:
            return '미등록'
    field_phonenumber.short_description = '연락처'

    readonly_fields = (
        'user',
        'field_app_user_id',
        'field_phonenumber',
        'type',
        'answer',
        'update_date',
        'create_date',
    )

    search_fields = ['user__nickname', 'user__app_user_id',
                     'user__phone_number']

    list_filter = (
        ('create_date', DateRangeFilter),
        'type',
    )

    list_display = (
        'user',
        'field_app_user_id',
        'field_phonenumber',
        'type',
        'answer',
        'update_date',
        'create_date',
    )
