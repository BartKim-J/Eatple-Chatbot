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

    try:
        order = Order.objects.get(order_id=order_id)
    except:
        order = None

    if(order == None):
        return JsonResponse({'status': 300, })

    if(order.order_kakaopay.pg_token != None):
        try:
            response = KakaoPay().OrderApprove(
                tid=order.order_kakaopay.tid,
                order_id=order.order_id,
                user_id=order.ordersheet.user.app_user_id,
                pg_token=order.order_kakaopay.pg_token,
                total_amount=order.totalPrice,
            )

            approveResponse = json.loads(response.text)

            print(approveResponse)
        except Exception as ex:
            print(ex)
            return JsonResponse({'status': 400, })

    try:
        response = KakaoPay().OrderStatus(tid=order.order_kakaopay.tid)
    except Order.order_kakaopay.RelatedObjectDoesNotExist as ex:
        return JsonResponse({'status': 400, })

    try:
        kakaoPayStatus = json.loads(response.text)['status']
        print(kakaoPayStatus)
        if(
            kakaoPayStatus == 'READY' or
            kakaoPayStatus == 'SEND_TMS' or
            kakaoPayStatus == 'OPEN_PAYMENT' or
            kakaoPayStatus == 'SELECT_METHOD' or
            kakaoPayStatus == 'ARS_WAITING' or
            kakaoPayStatus == 'AUTH_PASSWORD'
        ):
            order_status = 'W'
            message = '결제가 진행중입니다.'
        elif(
            kakaoPayStatus == 'SUCCESS_PAYMENT'
        ):
            order_status = 'S'
            message = '결제가 완료되었습니다.'
        elif(
            kakaoPayStatus == 'CANCEL_PAYMENT' or
            kakaoPayStatus == 'PART_CANCEL_PAYMENT'
        ):
            order_status = 'C'
            message = '이미 취소된 주문 번호입니다.'
        elif(
            kakaoPayStatus == 'QUIT_PAYMENT' or
            kakaoPayStatus == 'FAIL_AUTH_PASSWORD' or
            kakaoPayStatus == 'FAIL_PAYMENT'
        ):
            order_status = 'F'
            if(order.order_kakaopay.pg_token != None):
                message = approveResponse['extras']['method_result_message']
            else:
                message = '결제에 실패했습니다.'
        else:
            order_status = 'F'
            message = '잘못된 경로에 진입했습니다.'
    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 400, })

    data = {
        'order_status': order_status,
        'message': message,
    }

    payload = {
        'status': 200,
        'data': data,
    }

    print(data)
    return JsonResponse(payload, status=200)
