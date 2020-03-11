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
    readonly_fields = (
        'user',
        'type',
        'answer',
        'update_date',
        'create_date',
    )

    search_fields = ['user__nicknam', 'user__app_user_id',
                     'user__phone_number']

    list_filter = (
        ('create_date', DateRangeFilter),
        'type',
    )

    list_display = (
        'user',
        'type',
        'answer',
        'update_date',
        'create_date',
    )
