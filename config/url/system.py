from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.urls import path, include

from django.views.static import serve

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url

from eatple_app import views


if(settings.SETTING_ID == 'DEPLOY'):
    admin.site.site_header = "라이브 서버"
else:
    admin.site.site_header = "개발 서버"

admin.site.index_title = "Dashboard"
admin.site.site_title = "Eat+ Admin"

ADMIN_URLS = [
    # Admin
    path('jet/dashboard/', include('jet.dashboard.urls',
                                   'jet-dashboard')),  # Django JET dashboard URLS
    path('jet/', include('jet.urls', 'jet')),  # Django JET URLS

    path('admin/', admin.site.urls),
    path('admin/api/auth/login', views.POST_AdminLogin),
    path('admin/api/auth/logout', views.POST_AdminLogout),
]


MEDIA_URLS = [
    url(r'^media/(?P<path>.*)$', serve,
        {'document_root': settings.MEDIA_ROOT}),
]
MEDIA_STAIC_URLS = static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

STATIC_URLS = [
    url(r'^static/(?P<path>.*)$', serve,
        {'document_root': settings.STATIC_ROOT}),
]

STATIC_STATIC_URLS = static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT)
