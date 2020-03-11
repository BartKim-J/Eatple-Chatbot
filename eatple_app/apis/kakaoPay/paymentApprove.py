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

from eatple_app.apis.rest.validation import *

# View-System
from eatple_app.views_system.debugger import *

from eatple_app.views import *


@csrf_exempt
def GET_KAKAO_PAY_PaymentApprove(request):
    print(request)
    try:
        order_id = request.GET.get('partner_order_id')
        user_id = request.GET.get('partner_user_id')
        pg_token = request.GET.get('pg_token')
    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 400, })

    order = orderValidation(order_id)
    if(order == None):
        message = '주문번호를 찾을 수 없습니다.'
        return JsonResponse({'status': 400, 'message': message})

    try:
        order = order.order_kakaopay.approve(
            order.order_kakaopay.tid, pg_token)
    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 400, })

    try:
        kakaoResponse = KakaoPay().OrderApprove(
            tid=order.order_kakaopay.tid,
            order_id=order.order_id,
            user_id=order.ordersheet.user.app_user_id,
            pg_token=order.order_kakaopay.pg_token,
            total_amount=order.totalPrice,
        )
    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 400, })

    payload = {
        'status': 200,
    }

    return JsonResponse(payload, status=200)
