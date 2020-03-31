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


class UserServiceLocationFilter(SimpleListFilter):
    title = '지역'
    parameter_name = 'service area'

    def lookups(self, request, model_admin):
        return [
            ('all', '전체 지역'),
            ('service', '서비스 지역'),
            ('fastfive_sinsa_1', '패파 신사점'),
            ('fastfive_gangnam_1', '패파 강남 1호점'),
            ('fastfive_gangnam_2', '패파 강남 2호점'),
            ('fastfive_gangnam_3', '패파 강남 3호점'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'all':
            return queryset

        if self.value() == 'service':
            distance = 500
            ref_gangnam = Point(y=37.497907, x=127.027635, srid=4326)
            ref_yeoksam = Point(y=37.500787, x=127.036919, srid=4326)
            ref_samsung = Point(y=37.508852, x=127.063145, srid=4326)
            ref_sinsa = Point(y=37.518487, x=127.024381, srid=4326)

            queryset = queryset.annotate(
                distance_gangnam=Distance(
                    F('location__point'), ref_gangnam) * 100 * 1000,
                distance_yeoksam=Distance(
                    F('location__point'), ref_yeoksam) * 100 * 1000,
                distance_samsung=Distance(
                    F('location__point'), ref_samsung) * 100 * 1000,
                distance_sinsa=Distance(
                    F('location__point'), ref_sinsa) * 100 * 1000,
            ).filter(
                (Q(distance_gangnam__lte=distance) &
                 Q(distance_gangnam__gte=0)) |
                Q(distance_yeoksam__lte=distance) |
                Q(distance_samsung__lte=distance) |
                Q(distance_sinsa__lte=distance)
            )
            return queryset

        if self.value() == 'fastfive_sinsa_1':
            distance = 50
            ref_location = Point(y=37.518487, x=127.024381, srid=4326)

            queryset = queryset.annotate(
                distance=Distance(
                    F('location__point'), ref_location) * 100 * 1000,
            ).filter(
                Q(distance__lte=distance)
            )
            return queryset

        if self.value() == 'fastfive_gangnam_1':
            distance = 50
            ref_location = Point(y=37.496949, x=127.028679, srid=4326)

            queryset = queryset.annotate(
                distance=Distance(
                    F('location__point'), ref_location) * 100 * 1000,
            ).filter(
                Q(distance__lte=distance)
            )
            return queryset

        if self.value() == 'fastfive_gangnam_2':
            distance = 50
            ref_location = Point(y=37.495536, x=127.029352, srid=4326)

            queryset = queryset.annotate(
                distance=Distance(
                    F('location__point'), ref_location) * 100 * 1000,
            ).filter(
                Q(distance__lte=distance)
            )
            return queryset

        if self.value() == 'fastfive_gangnam_3':
            distance = 50
            ref_location = Point(y=37.496608, x=127.025092, srid=4326)

            queryset = queryset.annotate(
                distance=Distance(
                    F('location__point'), ref_location) * 100 * 1000,
            ).filter(
                Q(distance__lte=distance)
            )
            return queryset


class UserResource(resources.ModelResource):

    def dehydrate_latlng(self, obj):
        try:
            return "{}, {}".format(obj.location.lat, obj.location.long)
        except Exception:
            return "{}, {}".format(LOCATION_DEFAULT_LAT, LOCATION_DEFAULT_LNG)

    def dehydrate_phone_number(self, obj):
        if(obj.phone_number != None):
            return obj.phone_number.as_national
        else:
            return ''

    nickname = Field(attribute='nickname', column_name='닉네임')
    app_user_id = Field(attribute='app_user_id', column_name='계정 ID')
    latlng = Field(column_name='위도/경도')
    phone_number = Field(column_name='연락처')
    

    class Meta:
        model = User
        fields = (
            'nickname',
            'phone_number',
            'app_user_id',
            'latlng'
        )


class LocationInline(admin.TabularInline):
    model = Location
    min_num = 0

    readonly_field = (
        'lat',
        'long',
        'address'
    )

    formfield_overrides = {
        models.PointField: {"widget": GooglePointFieldWidget}
    }


class UserAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = UserResource

    list_per_page = 50

    def address(self, obj):
        if(obj.location.address == LOCATION_DEFAULT_ADDR or
           (obj.location.lat == LOCATION_DEFAULT_LAT and obj.location.long ==
            LOCATION_DEFAULT_LNG)
           ):
            return "위치 미등록"
        else:
            return obj.location.address
    address.short_description = "주소"

    def phonenumber(self, obj):
        return obj.phone_number.as_national
    phonenumber.short_description = "전화번호"

    readonly_fields = (
        'app_user_id',
        'nickname',
        'phonenumber',
        'email',
        'birthyear',
        'birthday',
        'gender',
        'ci',
        'ci_authenticated_at',
        'flag_promotion',
    )

    search_fields = ['nickname', 'app_user_id',
                     'phone_number', 'location__address']

    list_filter = (
        ('create_date', DateRangeFilter),
        UserServiceLocationFilter,
        'gender',
        'flag_promotion',
        'type',
    )

    list_display = (
        'nickname',
        'type',
        'app_user_id',
        'phonenumber',
        'email',
        'address',
    )

    inlines = [LocationInline]
