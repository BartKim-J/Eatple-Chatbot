# External Library
import json
import sys

# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from eatple_app.apis.slack.slack_logger import Slack_LogFollow, Slack_LogUnfollow

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# System
from eatple_app.system.validation import *

# Modules
from eatple_app.module_kakao.responseForm import *
from eatple_app.module_kakao.requestForm import *
from eatple_app.module_kakao.kakaoPay import *
from eatple_app.module_kakao.kakao import *
from eatple_app.module_kakao.form import *
from eatple_app.module_kakao.validation import *

###########################################################################################
# Event Variable

FAST_FIVE_FLOOR = [3, 4, 5, 9, 11, 12, 13]

SERVICE_AREAS = {
    'yeoksam': {
        'name': '역삼',
        'y': 37.500682,
        'x': 127.036598
    },
    'sinsa': {
        'name': '신사',
        'y': 37.516433,
        'x': 127.020389
    },
    'samsung': {
        'name': '삼성',
        'y': 37.508845,
        'x': 127.063132
    },
    'gangnam': {
        'name': '강남',
        'y': 37.497899,
        'x': 127.027670
    },
}
