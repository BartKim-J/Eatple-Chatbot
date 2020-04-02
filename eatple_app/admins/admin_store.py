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

# Coustom Model Type
from eatple_app.system.model_type_bank import *


class TypeFilter(MultipleChoiceListFilter):
    title = '유형'
    parameter_name = 'type__in'

    def lookups(self, request, model_admin):
        return STORE_TYPE


class CRNInline(admin.TabularInline):
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
                    'activity_date', 'activity_memo', 'record_date',
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
                'fields': [
                    'menu_id',
                    'store',
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


class StoreResource(resources.ModelResource):
    def dehydrate_bank_code(self, obj):
        return obj.bank_type

    def dehydrate_bank_type(self, obj):
        return dict(BANK_CODE)[obj.bank_type]

    id = Field(attribute='id', column_name='ID')
    store_id = Field(attribute='store_id', column_name='상점 고유 번호')
    name = Field(attribute='name', column_name='상호')
    area = Field(attribute='area', column_name='지역코드')
    owner = Field(attribute='owner', column_name='점주명')
    owner_email = Field(attribute='owner_email', column_name='이메일')
    phone_number = Field(attribute='phone_number', column_name='연락처')
    bank_code = Field(column_name='은행코드')
    bank_type = Field(column_name='은행명')
    bank_account = Field(attribute='bank_account', column_name='계좌번호')
    bank_owner = Field(attribute='bank_owner', column_name='예금주명')
    crn = Field(attribute='crn', column_name='사업자 등록 번호')

    class Meta:
        model = Store
        exclude = (
            'description',
            'logo',
            'addr',
            'category',
            'customer_level',
            'sales_memo',
            'container_support',
            'spoon_support',
            'plastic_bag_support',
            'status',
            'type'
        )


class StoreAdmin(ImportExportMixin, admin.GeoModelAdmin):
    resource_class = StoreResource
    readonly_fields = ('store_id', 'logo_preview', 'brc_preview', 'hc_preview')

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
        ),
        (
            '계좌 정보',
            {
                'fields':
                    [
                        'bank_email',
                        'bank_owner',
                        'bank_type',
                        'bank_account',
                    ]
            }
        ),
        (
            '사업자 & 영업 신고증',
            {
                'fields':
                    [
                        'brc_document_file',
                        'hc_document_file',
                    ]
            }
        )
    ]

    def brc_preview(self, obj):
        print(obj.brc_document_file.url)
        if(obj.brc_document_file.url != 'STORE_DB/images/'):
            return mark_safe('<img src="{url}" width="{width}" height={height} /><a href="{url}" download>다운로드</a>'.format(
                url=obj.brc_document_file.url,
                width=obj.brc_document_file.width * 0.4,
                height=obj.brc_document_file.height * 0.4,
            )
            )
        else:
            return None
    brc_preview.short_description = "사업자등록증 미리보기"

    def hc_preview(self, obj):
        print(obj.brc_document_file.url)
        if(obj.brc_document_file.url != 'STORE_DB/images/'):
            return mark_safe('<img src="{url}" width="{width}" height={height} /><a href="{url}" download>다운로드</a>'.format(
                url=obj.hc_document_file.url,
                width=obj.hc_document_file.width * 0.4,
                height=obj.hc_document_file.height * 0.4,
            )
            )
        else:
            return None
    hc_preview.short_description = "영업신고증 미리보기"

    def logo_preview(self, obj):
        return mark_safe(
            '<img src="{url}" width="{width}" height={height} /><a href="{url}" download>다운로드</a>'.format(
                url=obj.logo.url,
                width=58,
                height=58,
            ),
        )
    logo_preview.short_description = "이미지 미리보기"

    def field_status_flag(self, obj):
        if(obj.status == OC_OPEN):
            return 'O'
        else:
            return 'X'

        return False
    field_status_flag.short_description = "상태"

    list_filter = (
        'status',
        'area',
        'type',
    )

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
        self.message_user(request, '{}건의 제휴 매장을 열림 상태로 변경'.format(
            updated_count))  # django message framework 활용
    store_open.short_description = '지정 제휴 매장을 열림 상태로 변경'

    def store_close(self, request, queryset):
        updated_count = queryset.update(status=OC_CLOSE)  # queryset.update
        self.message_user(request, '{}건의 제휴 매장을 닫힘 상태로 변경'.format(
            updated_count))  # django message framework 활용
    store_close.short_description = '지정 제휴 매장을 닫힘 상태로 변경'

    actions = ['store_open', 'store_close']

    inlines = [MenuInline, RecordInline, PlaceInline, CRNInline]
