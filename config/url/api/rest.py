from django.urls import path, include
from django.conf.urls import url

from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from eatple_app import api

schema_view = get_schema_view(
    openapi.Info(
        title="Eatple Inbase API",
        default_version='v1.0.0',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="bart@eatple.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

partner_schema_view = get_schema_view(
    openapi.Info(
        title="Eatple Public API",
        default_version='v1.0.0',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="bart@eatple.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

RESTFUL_API_DOC_URLS = [
    url('rest/doc/swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url('rest/doc/swagger/$', schema_view.with_ui('swagger',
                                                  cache_timeout=0), name='schema-swagger-ui'),
    url('rest/redoc/$', schema_view.with_ui('redoc',
                                            cache_timeout=0), name='schema-redoc'),
]

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'order/validation', api.OrderValidation)
router.register(r'order/information', api.OrderInformation)

router.register(r'partner', api.PartnerViewSet)
router.register(r'order', api.OrderViewSet)

RESTFUL_API_URLS = [
    path('rest/api/', include(router.urls)),
]
