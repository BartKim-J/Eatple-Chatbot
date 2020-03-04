from config.url.system import *
from config.url.templates import TEMPLATES_URLS
from config.url.rest import RESTFUL_API_URLS, RESTFUL_API_DOC_URLS
from config.url.kakao import KAKAO_API_URLS
from config.url.slack import SLACK_API_URLS
from config.url.kakao_skill.user import KAKAO_SKILL_USER_URLS, KAKAO_SKILL_USER_EVENT_URLS
from config.url.kakao_skill.partner import KAKAO_SKILL_PARTNER_URLS

# Urls
urlpatterns = []

# Admin
urlpatterns += ADMIN_URLS

# Templates
urlpatterns += TEMPLATES_URLS

# Urls - User App
urlpatterns += KAKAO_SKILL_USER_URLS

# Urls - User Events App
urlpatterns += KAKAO_SKILL_USER_EVENT_URLS

# Urls - Partner App
urlpatterns += KAKAO_SKILL_PARTNER_URLS

# Urls - KAKAO API
urlpatterns += KAKAO_API_URLS

# Urls - SLACK API
urlpatterns += SLACK_API_URLS

# Urls - REST API
urlpatterns += RESTFUL_API_DOC_URLS
urlpatterns += RESTFUL_API_URLS

# Media Link Url
urlpatterns += MEDIA_URLS
urlpatterns += MEDIA_STAIC_URLS

# Static URL
urlpatterns += STATIC_URLS
urlpatterns += STATIC_STATIC_URLS
