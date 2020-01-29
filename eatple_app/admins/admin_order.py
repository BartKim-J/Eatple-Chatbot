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
        if(obj.ordersheet.user.phone_number != None):
            return obj.ordersheet.user.phone_number.as_national
        else:
            return ''

    def dehydrate_type(self, obj):
        return dict(ORDER_TYPE)[obj.type]
    
    def dehydrate_payment_status(self, obj):
         return dict(IAMPORT_ORDER_STATUS)[obj.payment_status]

    def dehydrate_order_date(self, obj):
        return obj.order_date.strftime(
                    '%Y년 %-m월 %-d일 %-H시 %-M분 %-S초')

    def dehydrate_payment_date(self, obj):
        return obj.payment_date.strftime(
                    '%Y년 %-m월 %-d일 %-H시 %-M분 %-S초')

    order_id = Field(attribute='order_id', column_name='주문번호')
    store = Field(attribute='store__name', column_name='상점')
    menu = Field(attribute='menu__name', column_name='메뉴')
    type = Field(column_name='주문 타입')
    b2b_name = Field(column_name='B2B')
    payment_status = Field(column_name='결제 상태')
    totalPrice = Field(attribute='totalPrice', column_name='총 결제금액')
    phone_number = Field(column_name='전화번호')
    order_date = Field(column_name='주문 시간')
    payment_date = Field(column_name='결제 완료 시간')
    
    class Meta:
        model = Order
        exclude = ('id', 'ordersheet', 'count', 'status', 'delegate', 'update_date', 'pickup_time')

class OrderAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = OrderResource
    list_per_page = 50

    def get_queryset(self, request):
        qs = super(OrderAdmin, self).get_queryset(request)
        
        return qs.exclude(Q(store=None) & Q(menu=None))

    def make_enable(self, request, queryset):
        updated_count = queryset.update(status=ORDER_STATUS_ORDER_CONFIRMED,payment_status= IAMPORT_ORDER_STATUS_PAID) #queryset.update
        self.message_user(request, '{}건의 주문을 Enable 상태로 변경'.format(updated_count)) #django message framework 활용
        
    make_enable.short_description = '지정 주문을 Enable 상태로 변경'
    
    def owner(self, obj):
            return obj.ordersheet.user.nickname
    owner.short_description = "사용자"
    
    def owner_id(self, obj):
        return obj.ordersheet.user.app_user_id
    owner_id.short_description = "사용자 고유번호"

    def user_type(self, obj):
        return obj.ordersheet.user.type

    def phone_number(self, obj):
        return obj.ordersheet.user.phone_number
    
    def delegate_flag(self, obj):
        if(obj.delegate != None):
            return True
        else:
            return False
        
        return False
    delegate_flag.short_description = "부탁하기"
    delegate_flag.boolean = True
    
    def b2b_name(self, obj):
        if(obj.ordersheet.user.company != None and obj.type == ORDER_TYPE_B2B):
            return obj.ordersheet.user.company.name
        else:
            return ''
    b2b_name.short_description = "B2B"
        
    search_fields = ['order_id', 'ordersheet__user__nickname', 'ordersheet__user__app_user_id']

    readonly_fields = (
    )
    
    list_filter = (
        ('payment_date', DateRangeFilter),
        ('pickup_time', DateRangeFilter),
        ('store',  RelatedDropdownFilter),
        ('payment_status', ChoiceDropdownFilter),
        ('status', ChoiceDropdownFilter),
        ('ordersheet__user__company', RelatedDropdownFilter),
        ('type', ChoiceDropdownFilter),
        ('ordersheet__user__type', ChoiceDropdownFilter),
        OrderShareFlagFilter,
    )
    
    actions = ['make_enable']

    list_display = ('order_id', 'owner', 'owner_id',  'store', 'menu', 'type', 'b2b_name',
                    'payment_status', 'status', 'delegate_flag', 'pickup_time', 'payment_date')
