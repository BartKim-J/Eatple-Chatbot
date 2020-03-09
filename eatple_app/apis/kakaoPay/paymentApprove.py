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
def GET_KAKAO_PAY_PaymentApprove(request):
    print(request)
    try:
        order_id = request.GET.get('partner_order_id')
        user_id = request.GET.get('partner_user_id')
        pg_token = request.GET.get('pg_token')
    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 400, })

    try:
        order = Order.objects.get(order_id=partner_order_id)
    except:
        # @TODO: Error Case
        #order = None
        order = Order.objects.filter(
            ~Q(menu=None) & Q(totalPrice__lte=1000) & Q(totalPrice__gte=100)).first()

    if(order == None):
        return JsonResponse({'status': 400, })

    try:
        kakaoResponse = KakaoPay().OrderApprove(
            tid=order.order_kakaopay.tid,
            order_id=order.order_id,
            user_id=order.ordersheet.user.app_user_id,
            pg_token=pg_token,
            total_amount=order.totalPrice,
        )
        print(kakaoResponse.text)
    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 400, })

    payload = {
        'status': 200,
    }

    return JsonResponse(payload, status=200)
