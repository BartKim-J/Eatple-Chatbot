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

from django.contrib.admin import SimpleListFilter


class UserB2BResource(resources.ModelResource):
    def dehydrate_company(self, obj):
        if(obj.company != None):
            return obj.company.name
        else:
            return '일반'

    def dehydrate_phone_number(self, obj):
        if(obj.phone_number != None):
            return obj.phone_number.as_national
        else:
            return ''

    company = Field(column_name='소속 회사')
    name = Field(attribute='name', column_name='이름')
    phone_number = Field(column_name='전화번호')

    class Meta:
        model = UserB2B
        exclude = ('id', 'create_date',)


class UserB2BAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = UserB2BResource

    list_per_page = 50

    def account_sync_flag(self, obj):
        try:
            User.objects.get(phone_number=obj.phone_number)
            return 'O'
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return 'X'

        return False
    account_sync_flag.short_description = "카카오 계정 연동 상태"

    def account_info(self, obj):
        try:
            user = User.objects.get(phone_number=obj.phone_number)
            return "{} : {}".format(user.nickname, user.app_user_id)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return "미등록"

    account_info.short_description = "카카오 계정"

    def phonenumber(self, obj):
        return obj.phone_number.as_national
    phonenumber.short_description = "전화번호"

    search_fields = ['company__name', 'name', 'phone_number']

    list_filter = (
        'company',
        ('create_date', DateRangeFilter),
    )

    list_display = (
        'company',
        'name',
        'phonenumber',
        'account_info',
        'account_sync_flag',
    )

    inlines = []
