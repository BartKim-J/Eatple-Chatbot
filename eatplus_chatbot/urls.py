"""eatplus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from store_app import views

# Urls
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    path('home', views.home),

    # Kakao Plus Skills
    path('getSellingTime', views.getSellingTime),
    path('selectMenu', views.selectMenu),
    path('getPickupTime', views.getPickupTime),
    path('orderConfirm', views.orderConfirm),

    path('getOrderList', views.getOrderList),
]

# Media Link Url
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)