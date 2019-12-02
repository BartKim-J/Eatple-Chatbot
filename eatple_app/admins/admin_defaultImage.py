# Models
from eatple_app.models import *

# Django Library
from django.contrib import admin
from django import forms
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

class DefaultImageAdmin(admin.ModelAdmin):

    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url=obj.image.url,
            width=obj.image.width,
            height=obj.image.height,
        )
    )