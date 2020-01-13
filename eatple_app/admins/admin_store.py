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
    
    readonly_fields = ('menu_id', "image_preview")

    def image_preview(self, obj):
        class Meta:
            verbose_name = "픽업 시간"
            verbose_name_plural = "픽업 시간"
            
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url=obj.image.url,
            width=obj.image.width * 0.4,
            height=obj.image.height * 0.4,
        )
    )
    image_preview.short_description = "이미지 미리보기"
    
    fieldsets = [
        (None,                  {'fields': ['menu_id']}),
        ('메뉴 정보',                  {'fields': ['name']}),
        (None,                  {'fields': [
         'selling_time', 'pickup_time','tag', 'description', 'image','image_preview', 'price', 'discount']}),
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
