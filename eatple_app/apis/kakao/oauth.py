# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from eatple_app.apis.slack.slack_logger import SlackLogFollow, SlackLogUnfollow

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# Modules
from eatple_app.module_kakao.responseForm import *
from eatple_app.module_kakao.requestForm import *
from eatple_app.module_kakao.kakaoPay import *
from eatple_app.module_kakao.form import *
from eatple_app.module_kakao.validation import *

# View-System
from eatple_app.views_system.debugger import *

from eatple_app.views import *


@csrf_exempt
def GET_KAKAO_Oauth(request):
    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)

    print(received_json_data)

    data = {
        'status': 200
    }

    return JsonResponse(data, status=200)
