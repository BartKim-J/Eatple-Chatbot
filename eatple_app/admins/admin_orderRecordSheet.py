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


class OrderRecordInline(admin.TabularInline):
    model = OrderRecord
    extra = 0
    min_num = 0

    readonly_fields = (
        'status',
        'record_date',
    )


class OrderRecordSheetAdmin(ImportExportMixin, admin.ModelAdmin):
    list_per_page = 50

    def get_queryset(self, request):
        qs = super(OrderRecordSheetAdmin, self).get_queryset(request)

        return qs.exclude(Q(user__is_staff=True))

    def delegate_status(self, obj):
        if(obj.order.menu != None):
            return 'O'
        else:
            return 'X'
    delegate_status.short_description = "메뉴 선택 여부"

    def delegate_paid(self, obj):
        if(obj.order.payment_status == EATPLE_ORDER_STATUS_PAID):
            return 'O'
        else:
            return 'X'
    delegate_paid.short_description = "결제 완료 여부"

    def get_menu(self, obj):
        if(obj.order == None or obj.order.menu == None):
            return "미선택"
        else:
            return obj.order.menu
    get_menu.short_description = "선택한 메뉴"

    fieldsets = [
        (
            '레코드 시트 정보',
            {
                'fields': [
                    'order',
                    'user',
                    'created_date',
                    'update_date',
                ]
            }
        ),
    ]

    readonly_fields = (
        'order',
        'user',
        'status',
        'paid',
        'created_date',
        'update_date'
    )

    list_filter = (
        'status',
        'update_date',
        'created_date'
    )

    list_display = (
        'order',
        'user',
        'get_menu',
        'delegate_status',
        'delegate_paid',
        'created_date',
        'update_date'
    )

    search_fields = [
        'order__order_id',
        'user__nickname',
        'user__phone_number',
        'user__app_user_id'
    ]

    inlines = [OrderRecordInline]
