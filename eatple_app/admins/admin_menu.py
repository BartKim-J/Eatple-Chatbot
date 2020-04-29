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

from django.contrib.admin import SimpleListFilter


class MenuPickupZoneFilter(SimpleListFilter):
    title = '픽업존'
    parameter_name = '픽업존'

    def lookups(self, request, model_admin):
        return [
            ('on', '픽업존'),
            ('off', '테이크아웃'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'on':
            return queryset.filter(Q(tag__name="픽업존"))

        if self.value() == 'off':
            return queryset.filter(~Q(tag__name="픽업존"))


class MenuStockFilter(SimpleListFilter):
    title = '주문 여부'
    parameter_name = '주문 여부'

    def lookups(self, request, model_admin):
        return [
            ('on', '주문 있음'),
            ('off', '주문 없음'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'on':
            return queryset.filter(Q(current_stock__gt=0))

        if self.value() == 'off':
            return queryset.filter(~Q(current_stock=0))


class TypeFilter(MultipleChoiceListFilter):
    title = '유형'
    parameter_name = 'type__in'

    def lookups(self, request, model_admin):
        return OC_TYPE


class StockTableInline(CompactInline):
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

    save_as = True

    readonly_fields = ('menu_id', "image_preview",
                       "image_soldout_preview", "current_stock", "pickuped_stock")

    def stock_status(self, obj):
        return '{} / {}'.format(obj.getCurrentStock().count(), obj.max_stock)
    stock_status.short_description = "일일 재고 상태"

    def stock_by_pickup(self, obj):
        pickupTimes = obj.pickup_time.all()
        stockList = ''
        onDisplay = 0

        for pickupTime in pickupTimes:
            refPickupTime = [x.strip()
                             for x in str(pickupTime.time).split(':')]
            datetime_pickup_time = dateNowByTimeZone().replace(
                hour=int(refPickupTime[0]),
                minute=int(refPickupTime[1]),
                second=0,
                microsecond=0
            )

            orderByPickupTime = Order.objects.filter(menu=obj).filter(
                (
                    Q(status=ORDER_STATUS_PICKUP_COMPLETED) |
                    Q(status=ORDER_STATUS_PICKUP_WAIT) |
                    Q(status=ORDER_STATUS_PICKUP_PREPARE) |
                    Q(status=ORDER_STATUS_ORDER_CONFIRM_WAIT) |
                    Q(status=ORDER_STATUS_ORDER_CONFIRMED)
                ) &
                Q(pickup_time=datetime_pickup_time)
            )

            orderCount = orderByPickupTime.count()
            if(orderCount > 0):
                stockList += '{}개({})'.format(
                    orderCount,
                    pickupTime.time.strftime(
                        '%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')
                )
                onDisplay += orderCount

                if(pickupTime != pickupTimes.last()):
                    stockList += ', '

        if(onDisplay == 0):
            stockList = '주문 없음'
        return stockList
    stock_by_pickup.short_description = "일일 재고 상태"

    def image_preview(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} /><a href="{url}" download>다운로드</a>'.format(
            url=obj.image.url,
            width=obj.image.width * 0.4,
            height=obj.image.height * 0.4,
        )
        )
    image_preview.short_description = "이미지 미리보기"

    def image_soldout_preview(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} /><a href="{url}" download>다운로드</a>'.format(
            url=obj.soldout_image.url,
            width=obj.soldout_image.width * 0.4,
            height=obj.soldout_image.height * 0.4,
        )
        )
    image_soldout_preview.short_description = "매진 이미지 미리보기"

    fieldsets = [
        (
            '기본 정보',
            {
                'fields':
                    [
                        'menu_id',
                        'store'
                    ]
            }
        ),
        (
            '메뉴 정보',
            {
                'fields': [
                    'name',
                    'selling_time',
                    'pickup_time',
                    'tag',
                    'description',
                    'price',
                    'price_origin'
                ]
            }
        ),
        (
            '이미지',
            {
                'fields': [
                    'image',
                    'image_preview',
                    'soldout_image',
                    'image_soldout_preview',
                ]
            }
        ),
        (
            '메뉴 상태',
            {
                'fields': [
                    'current_stock',
                    'pickuped_stock',
                    'max_stock',
                    'status'
                ]
            }
        ),
    ]

    search_fields = [
        'name',
        'tag__name',
        'menu_id',
        'store__name',
        'stocktable__company__name'
    ]

    list_filter = (
        'store',
        'store__area',
        MenuPickupZoneFilter,
        MenuStockFilter,
        # 'stocktable__company__name',
        'status',
        'selling_time',
    )

    list_display = (
        'name',
        'selling_time',
        'price',
        'price_origin',
        'stock_status',
        'stock_by_pickup',
        'status',
        'store',
    )

    list_editable = (
        'status',
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
