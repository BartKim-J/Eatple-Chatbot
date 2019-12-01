# Models
from eatple_app.models import *

# Django Library
from django.contrib import admin
from django import forms
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from import_export.admin import ExportActionModelAdmin, ImportExportMixin, ImportMixin
from import_export import resources

class PartnerAdmin(ImportExportMixin, admin.ModelAdmin):
    readonly_fields = ('store', 'app_user_id', 'nickname', 'profile_image_url',
                       'phone_number', 'email', 'birthyear', 'birthday', 'gender', 'ci', 'ci_authenticated_at')

    list_filter = ('create_date', 'gender')
    list_display = ('app_user_id', 'nickname',
                    'phone_number', 'email', 'gender')