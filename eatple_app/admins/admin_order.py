# Define
from eatple_app.define import *

# Models
from eatple_app.models import *

# Django Library
from django.contrib import admin
from django import forms
from django.db import models
from django.db.models import Q
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from django.contrib.admin import SimpleListFilter


class TypeFilter(MultipleChoiceListFilter):
    title = '주문 타입'
    parameter_name = 'type__in'

    def lookups(self, request, model_admin):
        return ORDER_TYPE


class KakaoPayInline(admin.StackedInline):
    verbose_name = "카카오 페이"
    verbose_name_plural = "카카오 페이"

    model = Order_KakaoPay
    extra = 0

    readonly_fields = ('tid', 'pg_token', )


class OrderShareFlagFilter(SimpleListFilter):
    title = '부탁하기'
    parameter_name = '부탁하기 플래그'

    def lookups(self, request, model_admin):
        return [
            ('on', '사용자'),
            ('off', '위임자 또는 미사용자'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'on':
            return queryset.filter(~Q(delegate=None))

        if self.value() == 'off':
            return queryset.filter(Q(delegate=None))


class OrderResource(resources.ModelResource):
    def dehydrate_b2b_name(self, obj):
        if(obj.ordersheet.user.company != None):
            return obj.ordersheet.user.company.name
        else:
            return '일반'

    def dehydrate_phone_number(self, obj):
        if(obj.ordersheet.user.field_phone_number != None):
            return obj.ordersheet.user.field_phone_number.as_national
        else:
            return ''

    def dehydrate_type(self, obj):
        return dict(ORDER_TYPE)[obj.type]

    def dehydrate_payment_status(self, obj):
        return dict(EATPLE_ORDER_STATUS)[obj.payment_status]

    def dehydrate_payment_type(self, obj):
        return dict(ORDER_PAYMENT_TYPE)[obj.payment_type]

    def dehydrate_user_name(self, obj):
        return obj.ordersheet.user.nickname

    def dehydrate_order_date(self, obj):
        return dateByTimeZone(obj.order_date).strftime(
            '%Y-%m-%d')

    def dehydrate_pickup_complete_date(self, obj):
        return dateByTimeZone(obj.pickup_complete_date).strftime(
            '%Y-%m-%d')

    def dehydrate_payment_date(self, obj):
        return dateByTimeZone(obj.payment_date).strftime(
            '%Y-%m-%d')

    order_id = Field(attribute='order_id', column_name='주문번호')
    user_name = Field(attribute='ordersheet__user__nickname',
                      column_name='주문자')
    store = Field(attribute='store__name', column_name='상점')
    menu = Field(attribute='menu__name', column_name='메뉴')
    type = Field(column_name='주문 타입')
    b2b_name = Field(column_name='B2B')
    payment_status = Field(column_name='결제 상태')
    totalPrice = Field(attribute='totalPrice', column_name='총 결제금액')
    field_phone_number = Field(column_name='전화번호')
    order_date = Field(column_name='주문 시간')
    payment_date = Field(column_name='결제 완료 시간')
    pickup_complete_date = Field(column_name='픽업 완료 시간')
    payment_type = Field(column_name='결제 타입')
    tid = Field(attribute='order_kakaopay__tid', column_name='카카오 고유 주문번호')

    class Meta:
        model = Order
        exclude = ('id', 'ordersheet', 'count', 'status',
                   'delegate', 'update_date', 'pickup_time')


class OrderAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = OrderResource
    list_per_page = 50

    def get_queryset(self, request):
        qs = super(OrderAdmin, self).get_queryset(request)

        # return qs.exclude(Q(store=None) & Q(menu=None))
        return qs

    def make_enable(self, request, queryset):
        updated_count = queryset.update(
            status=ORDER_STATUS_ORDER_CONFIRMED, payment_status=EATPLE_ORDER_STATUS_PAID)  # queryset.update
        self.message_user(request, '{}건의 주문을 Enable 상태로 변경'.format(
            updated_count))  # django message framework 활용

    make_enable.short_description = '지정 주문을 Enable 상태로 변경'

    def field_owner(self, obj):
        return obj.ordersheet.user.nickname
    field_owner.short_description = "사용자"

    def field_owner_id(self, obj):
        return obj.ordersheet.user.app_user_id
    field_owner_id.short_description = "사용자 고유번호"

    def field_user_type(self, obj):
        return obj.ordersheet.user.type

    def field_phone_number(self, obj):
        return obj.ordersheet.user.field_phone_number

    def field_delegate_flag(self, obj):
        if(obj.delegate != None):
            return 'O'
        else:
            return 'X'

        return False
    field_delegate_flag.short_description = "부탁하기"

    def b2b_name(self, obj):
        if(obj.ordersheet.user.company != None and obj.type == ORDER_TYPE_B2B):
            return obj.ordersheet.user.company.name
        else:
            return ''
    b2b_name.short_description = "소속 회사"

    fieldsets = [
        (
            '기본 정보',
            {
                'fields': [
                    'order_id',
                    'ordersheet',
                    'store',
                    'menu',
                    'type',
                ]
            }
        ),
        (
            '구성',
            {
                'fields': [
                    'totalPrice',
                    'count',
                ]
            }
        ),
        (
            '상태',
            {
                'fields': [
                    'payment_type',
                    'payment_status',
                    'status',
                ]
            }
        ),
        (
            '부탁하기',
            {
                'fields': [
                    'delegate',
                ]
            }
        ),
        (
            '시간',
            {
                'fields': [
                    'order_date',
                    'payment_date',
                    'pickup_time',
                    'pickup_complete_date',
                    'update_date',
                ]
            }
        ),
    ]

    search_fields = ['order_id', 'ordersheet__user__nickname',
                     'ordersheet__user__app_user_id']

    readonly_fields = (
        'update_date',
    )

    list_editable = (
        'status',
    )

    list_filter = (
        ('payment_date', DateRangeFilter),
        ('pickup_time', DateRangeFilter),
        OrderShareFlagFilter,
        'ordersheet__user__company',
        'status',
        'payment_status',
        TypeFilter,
        'store',
        'ordersheet__user__is_staff',
    )

    actions = ['make_enable']

    list_display = ('order_id', 'field_owner', 'field_owner_id',  'store', 'menu', 'type', 'b2b_name',
                    'payment_type', 'payment_status', 'status', 'field_delegate_flag', 'pickup_time', 'payment_date', 'pickup_complete_date')

    inlines = [KakaoPayInline]
