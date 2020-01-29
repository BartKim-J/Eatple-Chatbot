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
    
class CRNInline(admin.TabularInline):
    model = CRN
    min_num = 1

    readonly_fields = ('CRN_id',)

class PlaceInline(admin.TabularInline):
    model = Place
    min_num = 1

    formfield_overrides = {
        models.PointField: {"widget": GooglePointFieldWidget}
    }

class MenuInline(admin.StackedInline):
    model = Menu
    extra = 0
    min_num = 1
    max_num = 2
    
    readonly_fields = ('menu_id', "image_preview", "image_soldout_preview")

    def image_preview(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url=obj.image.url,
            width=obj.image.width * 0.4,
            height=obj.image.height * 0.4,
        )
    )
    image_preview.short_description = "이미지 미리보기"

    def image_soldout_preview(self, obj):            
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url=obj.soldout_image.url,
            width=obj.soldout_image.width * 0.4,
            height=obj.soldout_image.height * 0.4,
        )
    )
    image_soldout_preview.short_description = "매진 이미지 미리보기"

    fieldsets = [
        (None,                  {'fields': ['menu_id']}),
        ('메뉴 정보',                  {'fields': ['name']}),
        (None,                  {'fields': [
         'selling_time', 'pickup_time', 'tag', 'description', 'image', 'image_preview', 'soldout_image', 'image_soldout_preview', 'price', 'discount']}),
        (None,                  {'fields': [
         'current_stock', 'max_stock', 'status']}),
    ]
    
class StoreAdmin(ImportExportMixin, admin.GeoModelAdmin):        
    readonly_fields = ('store_id', 'logo_preview')

    list_editable = ()

    fieldsets = [
        (None,                   {'fields': ['store_id']}),
        ('기본 정보',            {'fields': ['name', 'addr', 'owner' ,'phone_number']}),
        ('설정',                 {'fields': ['category', 'description', 'logo', 'logo_preview']}),
        ('상태',                 {'fields': ['status', 'type', 'area']}),
    ]

    def logo_preview(self, obj):
        return mark_safe(
            '<img src="{url}" width="{width}" height={height} />'.format(
            url=obj.logo.url,
            width=58,
            height=58,
        )
    )
    logo_preview.short_description = "이미지 미리보기"

    def menu_done_stock(self, obj):
        current_pickup_order = Menu.objects.filter(store=obj).order_by('-current_stock').first().getCurrentStock().filter(Q(status=ORDER_STATUS_PICKUP_COMPLETED)).count()
        current_stock = Menu.objects.filter(store=obj).order_by('-current_stock').first().current_stock

        if(current_stock != 0):
            return "{} ({}%)".format(current_pickup_order, round(( current_pickup_order / current_stock ) * 100))
        else:
            return "0 (100%)"
        
    menu_done_stock.short_description = "일일 픽업완료"    

    def menu_current_stock(self, obj):
        return Menu.objects.filter(store=obj).order_by('-current_stock').first().current_stock
    menu_current_stock.short_description = "일일 주문량"
    
    def menu_max_stock(self, obj):
        return Menu.objects.filter(store=obj).order_by('-current_stock').first().max_stock
    menu_max_stock.short_description = "일일 재고"
    
    def menu_name(self, obj):
        return Menu.objects.filter(store=obj).first().name
    menu_name.short_description = "메뉴명"
    
    list_filter = (
        ('status', ChoiceDropdownFilter), 
        ('area', ChoiceDropdownFilter), 
        ('type', ChoiceDropdownFilter)
    )

    def status_flag(self, obj):
        if(obj.status == OC_OPEN):
            return True
        else:
            return False
        
        return False
    status_flag.short_description = "상태"
    status_flag.boolean = True
    
    list_display = (
        'name', 
        'store_id', 
        'crn', 
        'type', 
        'area',
        'status_flag',
        'menu_name',
        'menu_current_stock',
        'menu_done_stock',
        'menu_max_stock',
    )

    def store_open(self, request, queryset):
            updated_count = queryset.update(status='open') #queryset.update
            self.message_user(request, '{}건의 제휴 점포를 열림 상태로 변경'.format(updated_count)) #django message framework 활용
    store_open.short_description = '지정 제휴 점포를 열림 상태로 변경'

    def store_close(self, request, queryset):
            updated_count = queryset.update(status='close') #queryset.update
            self.message_user(request, '{}건의 제휴 점포을 닫힘 상태로 변경'.format(updated_count)) #django message framework 활용
    store_close.short_description = '지정 제휴 점포를 닫힘 상태로 변경'
    
    actions = ['store_open', 'store_close']

    inlines = [PlaceInline, CRNInline, MenuInline]
