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
def GET_KAKAO_PAY_OrderApprove(request):
    print(request)
    try:
        json_str = ((request.body).decode('utf-8'))
        received_json_data = json.loads(json_str)

        partner_order_id = received_json_data['partner_order_id']
        tid = received_json_data['tid']
    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 400, })

    try:
        order = Order.objects.get(order_id=partner_order_id)
    except:
        order = None

    if(order == None):
        return JsonResponse({'status': 400, })

    try:
        order.payment_type = ORDER_PAYMENT_KAKAO_PAY
        try:
            order.order_kakaopay.approve(tid)
        except Exception as ex:
            order.order_kakaopay = Order_KakaoPay(order=order)
            order.order_kakaopay.approve(tid)

        order.save()
    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 400, })

    payload = {
        'status': 200,
    }

    return JsonResponse(payload, status=200)
