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

from eatple_app.admins.admin_survey import SurveyAdmin
from eatple_app.admins.admin_company import CompanyAdmin
from eatple_app.admins.admin_user import UserAdmin
from eatple_app.admins.admin_userB2B import UserB2BAdmin
from eatple_app.admins.admin_partner import PartnerAdmin
from eatple_app.admins.admin_store import StoreAdmin
from eatple_app.admins.admin_menu import MenuAdmin
from eatple_app.admins.admin_order import OrderAdmin
from eatple_app.admins.admin_orderSheet import OrderSheetAdmin
from eatple_app.admins.admin_orderRecordSheet import OrderRecordSheetAdmin
from eatple_app.admins.admin_defaultImage import DefaultImageAdmin


class HideAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}


admin.site.register(PickupTime, HideAdmin)
admin.site.register(Category, HideAdmin)
admin.site.register(Tag, HideAdmin)
admin.site.register(OrderSheet, HideAdmin)
admin.site.register(OrderRecordSheet, OrderRecordSheetAdmin)

admin.site.register(DefaultImage, DefaultImageAdmin)

admin.site.register(Store, StoreAdmin)
admin.site.register(Menu, MenuAdmin)

admin.site.register(Company, CompanyAdmin)

admin.site.register(Order, OrderAdmin)

admin.site.register(User, UserAdmin)

admin.site.register(UserB2B, UserB2BAdmin)

admin.site.register(Partner, PartnerAdmin)

admin.site.register(Survey, SurveyAdmin)
