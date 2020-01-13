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
    class Meta:
        model = UserB2B
        fields = (
            'company',
            'name',
            'phone_number'
        )

class UserB2BAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = UserB2BResource

    list_per_page = 50

    search_fields = ['company', 'name', 'phone_number']

    def phonenumber(self, obj):
        return obj.phone_number.as_national
    phonenumber.short_description = "전화번호"
    

    list_filter = (
        ('company',)
    )

    list_display = (
        'company',
        'name',
        'phonenumber',
    )

    inlines = []
