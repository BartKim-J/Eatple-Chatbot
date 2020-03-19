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
        return STORE_TYPE


class CRNInline(CompactInline):
    verbose_name = "사업자 등록번호"
    verbose_name_plural = "사업자 등록번호"

    model = CRN
    min_num = 1

    readonly_fields = ('CRN_id',)


class PlaceInline(CompactInline):
    verbose_name = "장소"
    verbose_name_plural = "장소"

    model = Place
    min_num = 1

    formfield_overrides = {
        models.PointField: {"widget": GoogleStaticMapWidget}
    }


class RecordInline(CompactInline):
    verbose_name = '영업 활동 내역'
    verbose_name_plural = '영업 활동 내역'

    model = SalesRecord
    extra = 0

    fieldsets = [
        (
            '기본 정보',
            {
                'fields': [
                    'activity_memo', 'activity_date', 'record_date',
                ]
            }
        ),
    ]

    readonly_fields = ('store', 'record_date')


class MenuInline(CompactInline):
    verbose_name = "메뉴"
    verbose_name_plural = "메뉴"

    model = Menu
    extra = 0
    min_num = 1
    max_num = 50

    readonly_fields = ('menu_id', "image_preview",
                       "image_soldout_preview", 'pickuped_stock', 'current_stock',)

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
         'selling_time', 'pickup_time', 'tag', 'description',
         'image', 'image_preview',
         'soldout_image', 'image_soldout_preview',
         'price', ]}),
        (None,                  {'fields': [
         'current_stock', 'pickuped_stock', 'max_stock', 'status']}),
    ]


class StoreAdmin(ImportExportMixin, admin.GeoModelAdmin):
    readonly_fields = ('store_id', 'logo_preview')

    list_editable = ()

    fieldsets = [
        (
            '기본 정보',
            {
                'fields': [
                    'store_id',
                    'name',
                    'addr',
                    'owner',
                    'phone_number'
                ]
            }
        ),
        (
            '설정',
            {
                'fields': [
                    'category',
                    'description',
                    'logo',
                    'logo_preview'
                ]
            }
        ),
        (
            '상태',
            {
                'fields':
                    [
                        'status',
                        'type',
                        'area'
                    ]
            }
        ),
        (
            '영업 관리',
            {
                'fields':
                    [
                        'customer_level',
                        'sales_memo',
                        'container_support',
                        'spoon_support',
                        'plastic_bag_support',
                    ]
            }
        )
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

    def menu_pickup_status(self, obj):
        menu = Menu.objects.filter(store=obj, status=OC_OPEN).order_by(
            '-current_stock').first()

        if(menu != None):
            current_stock = menu.current_stock

            if(current_stock != 0):
                return "{}개".format(current_stock)
            else:
                return "들어온 주문 없음"

        else:
            return "열린 메뉴가 없음"

    menu_pickup_status.short_description = "들어온 주문"

    list_filter = (
        'status',
        'area',
        'type',
    )

    def field_status_flag(self, obj):
        if(obj.status == OC_OPEN):
            return 'O'
        else:
            return 'X'

        return False
    field_status_flag.short_description = "상태"

    list_display = (
        'name',
        'store_id',
        'crn',
        'type',
        'area',
        'field_status_flag',
    )

    search_fields = ['name', 'store_id', 'area', 'menu__name']

    def store_open(self, request, queryset):
        updated_count = queryset.update(status=OC_OPEN)  # queryset.update
        self.message_user(request, '{}건의 제휴 점포를 열림 상태로 변경'.format(
            updated_count))  # django message framework 활용
    store_open.short_description = '지정 제휴 점포를 열림 상태로 변경'

    def store_close(self, request, queryset):
        updated_count = queryset.update(status=OC_CLOSE)  # queryset.update
        self.message_user(request, '{}건의 제휴 점포을 닫힘 상태로 변경'.format(
            updated_count))  # django message framework 활용
    store_close.short_description = '지정 제휴 점포를 닫힘 상태로 변경'

    actions = ['store_open', 'store_close']

    inlines = [RecordInline, PlaceInline, MenuInline, CRNInline]
