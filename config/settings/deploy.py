'phonenumber_field'"""
Django settings for eatplus project.

Generated by 'django-admin startproject' using Django 2.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from django.utils.translation import gettext_lazy as _

SETTING_ID = 'DEPLOY'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)

# PATH
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8b%m$==a68uz-y#zl&hb^rb$oyl3ejy5=8c!5**l5x#lou1(i$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'ec2-52-198-15-69.ap-northeast-1.compute.amazonaws.com',
    '54.65.75.156',
    'skill.eatple.com',
    'www.eatple.com',
    'eatple.com',
    'localhost'
]

# Application definition

INSTALLED_APPS = [
    # 'suit',
    # 'eatple_app.apps.SuitConfig',

    'django.contrib.gis',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_admin_listfilter_dropdown',

    'import_export',
    'phonenumber_field',

    'rest_framework',
    'rest_framework_swagger',

    # local-app
    'eatple_app.apps.EatpleChatbotAppConfig',

    'corsheaders',

    'rangefilter',
    'mapwidgets',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Make sure you have this line
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.debug.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.mysql',
        'NAME': 'eatple_DB',
        'USER': 'eatple',
        'PASSWORD': 'eatple0000',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': 'SET foreign_key_checks = 0; SET sql_mode="STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION"',
            'charset': 'utf8mb4',
            'use_unicode': True,
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


MAP_WIDGETS = {
    "GooglePointFieldWidget": (
        ("zoom", 55),
        ("mapCenterLocation", [37.49492000000000, 127.02739000000000]),
    ),

    "GoogleStaticMapWidget": (
        ("zoom", 18),
        ("size", "480x480"),
        ("scale", ""),
        ("format", ""),
        ("maptype", ""),
        ("path", ""),
        ("visible", ""),
        ("style", ""),
        ("language", ""),
        ("region", "")
    ),

    "GOOGLE_MAP_API_KEY": "AIzaSyDRhnn4peSzEfKzQ_WjwDqDF9pzDiuVRhM"
}

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGES = [
    ('ko', _('Korean')),
    ('en', _('English')),
]

LANGUAGE_CODE = 'ko'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Rest framework
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'

STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    STATIC_DIR,
]
STATIC_ROOT = os.path.join(ROOT_DIR, 'static')

# COOKIES
#SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# CORS
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = [
    'http://ec2-54-65-75-156.ap-northeast-1.compute.amazonaws.com',
    'https://www.eatple.com',
    'https://www.eatple.com:8000',
    'https://www.eatple.com:8001',
    'http://www.eatple.com:8080',
    'http://www.eatple.com:8081',
    'https://eatple.com',
    'https://eatple.com:8000',
    'https://eatple.com:8001',
    'http://localhost:3000',
    'http://localhost:5000',
]
