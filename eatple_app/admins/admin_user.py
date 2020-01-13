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
            
            queryset = queryset.annotate(
                distance_gangnam=Distance(F('location__point'), ref_gangnam) * 100 * 1000,
                distance_yeoksam=Distance(F('location__point'), ref_yeoksam) * 100 * 1000,
            ).filter(
                (Q(distance_gangnam__lte=distance) &
                Q(distance_gangnam__gt=0)) |
                Q(distance_yeoksam__lte=distance)
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
    
    def latlng(self,obj):
        return "{}, {}".format(obj.location.lat, obj.location.long)
    class Meta:
        model = User
        fields = (
            'nickname',
            'location__address',
            'location__lat',
            'location__long',
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
           (obj.location.lat == LOCATION_DEFAULT_LAT and obj.location.long == LOCATION_DEFAULT_LNG)
        ):
            return "위치 미등록"
        else:
            return obj.location.address
        
    address.short_description = "주소"
    
    readonly_fields = (
        'app_user_id',
        'nickname',
        'phone_number',
        'email',
        'birthyear',
        'birthday',
        'gender',
        'ci',
        'ci_authenticated_at',
        'flag_promotion',
    )

    search_fields = ['nickname', 'app_user_id', 'phone_number', 'location__address']

    list_filter = (
        ('create_date', DateRangeFilter),
        UserServiceLocationFilter,
        'gender',
        'flag_promotion',
        'type',
    )

    list_display = (
        'app_user_id',
        'nickname',
        'phone_number',
        'email',
        'gender',
        'flag_promotion',
        'address',
    )

    inlines = [LocationInline]
