from django.contrib import admin
from django.urls import path, include

from django.views.static import serve

from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url

## Do Not Remove this codeblock ##
from eatple_app import views
from eatple_app import api
from eatple_app import templates
##################################

from config.url.system import *
from config.url.templates import TEMPLATES_URLS
from config.url.api.rest import RESTFUL_API_URLS, RESTFUL_API_DOC_URLS
from config.url.api.kakao import KAKAO_API_URLS, KAKAO_PAY_API_URLS
from config.url.api.slack import SLACK_API_URLS
from config.url.kakao_skill.user import KAKAO_SKILL_USER_URLS, KAKAO_SKILL_USER_EVENT_URLS
from config.url.kakao_skill.partner import KAKAO_SKILL_PARTNER_URLS

# Urls
urlpatterns = []

# Admin
urlpatterns += ADMIN_URLS

# Templates
urlpatterns += TEMPLATES_URLS

# User App
urlpatterns += KAKAO_SKILL_USER_URLS

# Partner App
urlpatterns += KAKAO_SKILL_PARTNER_URLS

# KAKAO API
urlpatterns += KAKAO_API_URLS
urlpatterns += KAKAO_PAY_API_URLS

# SLACK API
urlpatterns += SLACK_API_URLS

# REST API
urlpatterns += RESTFUL_API_URLS
urlpatterns += RESTFUL_API_DOC_URLS

# Media Link Url
urlpatterns += MEDIA_URLS
urlpatterns += MEDIA_STAIC_URLS

# Static URL
urlpatterns += STATIC_URLS
urlpatterns += STATIC_STATIC_URLS
