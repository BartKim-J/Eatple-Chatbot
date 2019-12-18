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


class LocationInline(admin.TabularInline):
    model = Location
    min_num = 0

    readonly_field = (
        'lat',
        'long',
        'address'
    )

    formfield_overrides = {
        models.PointField: {"widget": GooglePointFieldWidget}
    }


class UserAdmin(ImportExportMixin, admin.ModelAdmin):
    readonly_fields = (
        'app_user_id',
        'nickname',
        'phone_number',
        'email',
        'birthyear',
        'birthday',
        'gender',
        'ci',
        'ci_authenticated_at',
        'flag_promotion'
    )

    search_fields = ['nickname', 'app_user_id', 'phone_number']

    list_filter = (
        'create_date',
        'gender',
        'flag_promotion',
    )

    list_display = (
        'app_user_id',
        'nickname',
        'phone_number',
        'email',
        'gender',
        'flag_promotion',
    )

    inlines = [LocationInline]
