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


class TypeFilter(MultipleChoiceListFilter):
    title = '유형'
    parameter_name = 'type__in'

    def lookups(self, request, model_admin):
        return OC_TYPE


class StockTableInline(admin.TabularInline):
    verbose_name = "재고 관리"
    verbose_name_plural = "재고 관리"

    model = StockTable
    extra = 0

    readonly_fields = ('pickuped_stock', 'current_stock',)


class MenuAdmin(ImportExportMixin, admin.GeoModelAdmin):
    verbose_name = "메뉴"
    verbose_name_plural = "메뉴"

    model = Menu
    extra = 0
    min_num = 1
    max_num = 5

    readonly_fields = ('menu_id', "image_preview",
                       "image_soldout_preview", "current_stock", "pickuped_stock", "store")

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
        ('기본 정보',                  {'fields': ['menu_id', 'store', 'name']}),
        ('설정',                  {'fields': [
         'selling_time', 'pickup_time', 'tag', 'description',
         'image', 'image_preview',
         'soldout_image', 'image_soldout_preview',
         'price',]}),
        ('상태',                  {'fields': [
         'current_stock', 'pickuped_stock', 'max_stock', 'status']}),
    ]

    list_display = (
        'name',
        'store',
        'max_stock',
        'status',
        'selling_time',
    )

    def menu_open(self, request, queryset):
        updated_count = queryset.update(status=OC_OPEN)  # queryset.update
        self.message_user(request, '{}건의 메뉴를 열림 상태로 변경'.format(
            updated_count))  # django message framework 활용
    menu_open.short_description = '지정 메뉴를 열림 상태로 변경'

    def menu_close(self, request, queryset):
        updated_count = queryset.update(status=OC_CLOSE)  # queryset.update
        self.message_user(request, '{}건의 메뉴을 닫힘 상태로 변경'.format(
            updated_count))  # django message framework 활용
    menu_close.short_description = '지정 메뉴를 닫힘 상태로 변경'

    actions = ['menu_open', 'menu_close']

    inlines = [StockTableInline]
