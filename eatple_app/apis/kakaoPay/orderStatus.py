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
def GET_KAKAO_PAY_OrderStatus(request):
    print(request)
    try:
        order_id = request.GET.get('order_id')
    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 400, })

    order = orderValidation(order_id)
    if(order == None):
        message = '주문번호를 찾을 수 없습니다.'
        return JsonResponse({'status': 400, 'message': message})

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
        print(json.loads(response.text))

        if(
            kakaoPayStatus == 'READY' or
            kakaoPayStatus == 'SEND_TMS' or
            kakaoPayStatus == 'OPEN_PAYMENT' or
            kakaoPayStatus == 'SELECT_METHOD' or
            kakaoPayStatus == 'ARS_WAITING'
        ):
            order_status = 'W'
            message = '결제가 진행중입니다.'
        elif(kakaoPayStatus == 'AUTH_PASSWORD'):
            order_status = 'W'
            message = '유저 인증이 완료되었습니다.'
        elif(
            kakaoPayStatus == 'SUCCESS_PAYMENT'
        ):
            order_status = 'S'
            message = '결제가 완료되었습니다.'
            order.payment_status = EATPLE_ORDER_STATUS_PAID
            order.save()

            order.orderStatusUpdate()
        elif(
            kakaoPayStatus == 'CANCEL_PAYMENT' or
            kakaoPayStatus == 'PART_CANCEL_PAYMENT'
        ):
            order_status = 'C'
            message = '이미 취소된 주문 번호입니다.'
            order.payment_status = EATPLE_ORDER_STATUS_CANCELLED
        elif(
            kakaoPayStatus == 'QUIT_PAYMENT' or
            kakaoPayStatus == 'FAIL_AUTH_PASSWORD' or
            kakaoPayStatus == 'FAIL_PAYMENT'
        ):
            order_status = 'F'
            if(order.order_kakaopay.pg_token != None):
                message = approveResponse['extras']['method_result_message']
                if(
                    # 계좌 잔액부족
                    approveResponse['extras']['method_result_code'] == 'LACK_BALANCE' or
                    # 사용한도초과
                    approveResponse['extras']['method_result_code'] == '8326'

                ):
                    order.payment_status = EATPLE_ORDER_STATUS_NOT_PUSHED
                elif(approveResponse['extras']['method_result_code'] == '9999'):
                    order.payment_status = EATPLE_ORDER_STATUS_NOT_PUSHED
                    message = "계좌에 잔액이 부족하거나, 한도가 초과되었습니다."
                elif(int(approveResponse['code']) == -702):
                    order_status = 'S'
                    message = "이미 결제가 완료되었습니다."
                    order.payment_status = EATPLE_ORDER_STATUS_PAID
                else:
                    order.payment_status = EATPLE_ORDER_STATUS_FAILED
            else:
                message = '결제에 실패했습니다.'
                order.payment_status = EATPLE_ORDER_STATUS_FAILED
        elif(
            kakaoPayStatus == 'ZID_CERTIFICATE'
        ):
            order_status = 'W'
            message = '카카오 서버로부터 응답이 없습니다.'
            order.payment_status = EATPLE_ORDER_STATUS_FAILED
        else:
            order_status = 'F'
            message = '잘못된 경로에 진입했습니다.'
            order.payment_status = EATPLE_ORDER_STATUS_FAILED

        order.save()
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

    return JsonResponse(payload)
