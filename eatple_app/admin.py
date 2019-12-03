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

from eatple_app.admins.admin_user import UserAdmin
from eatple_app.admins.admin_partner import PartnerAdmin
from eatple_app.admins.admin_store import StoreAdmin
from eatple_app.admins.admin_order import OrderAdmin
from eatple_app.admins.admin_orderSheet import OrderSheetAdmin
from eatple_app.admins.admin_orderRecordSheet import OrderRecordSheetAdmin
from eatple_app.admins.admin_defaultImage import DefaultImageAdmin


admin.site.register(PickupTime)

admin.site.register(Store, StoreAdmin)

admin.site.register(OrderSheet, OrderSheetAdmin)

admin.site.register(Order, OrderAdmin)

admin.site.register(OrderRecordSheet, OrderRecordSheetAdmin)

admin.site.register(User, UserAdmin)

admin.site.register(Partner, PartnerAdmin)

admin.site.register(DefaultImage, DefaultImageAdmin)

admin.site.register(Category)
admin.site.register(Tag)

# Manual
# admin.site.register(UserManual)
# admin.site.register(PartnerManual)

# Intro
# admin.site.register(UserIntro)
# admin.site.register(PartnerIntro)
