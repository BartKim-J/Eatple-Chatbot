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
def GET_KAKAO_PAY_OrderStatus(request):
    print(request)
    try:
        order_id = request.GET.get('order_id')
    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 400, })

    data = {
        "order_status": "S",
        "message": "주문 상품이 품절되었습니다.",
        "order_id": order_id
    }

    payload = {
        'status': 200,
        'data': data,
    }

    return JsonResponse(payload, status=200)
