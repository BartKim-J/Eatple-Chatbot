# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.apis.slack.slack_logger import SlackLogFollow, SlackLogUnfollow
from eatple_app.apis.rest.api.user.validation import *


@csrf_exempt
def GET_KAKAO_PAY_OrderSheet(request):
    print(request)
    try:
        ordersheet_id = request.GET.get('ordersheet_id')
        zip_code = request.GET.get('zip_code')
    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 400, })

    try:
        order = orderValidation(ordersheet_id)
        if(order == None):
            message = '주문번호를 찾을 수 없습니다.'
            print(message)
            return JsonResponse({'status': 300, 'message': message})

        user = userValidation(order.ordersheet.user.app_user_id)
        if(user == None):
            message = '유효하지 않는 유저입니다.'
            print(message)
            return JsonResponse({'status': 400, 'message': message})

        if(order.payment_status == EATPLE_ORDER_STATUS_FAILED):
            order.status = ORDER_STATUS_MENU_CHOCIED
            order.payment_status = EATPLE_ORDER_STATUS_READY
            order.save()

        if(order.payment_status == EATPLE_ORDER_STATUS_PAID):
            message = '이미 결제가 완료되었습니다.'
            print(message)
            return JsonResponse({'status': 300, 'message': message})
        elif(order.payment_status == EATPLE_ORDER_STATUS_CANCELLED):
            message = '이미 환불한 주문번호입니다.'
            print(message)
            return JsonResponse({'status': 300, 'message': message})

        # Eatple Pass Check
        eatplePassStatus = eatplePassValidation(user)
        if(eatplePassStatus == False):
            message = '이미 다른 주문을 하셨습니다.'
            print(message)
            return JsonResponse({'status': 300, 'message': message})

        # Time Check
        sellingTime = order.menu.selling_time
        currentSellingTime = sellingTimeCheck()
        isClosedDay = weekendTimeCheck(SELLING_TIME_LUNCH)

        if(currentSellingTime != sellingTime or isClosedDay == True):
            message = '현재 주문 가능시간이 아닙니다.'
            return JsonResponse({'status': 301, 'message': message})

        if(order.store.status != OC_OPEN or order.menu.status != OC_OPEN):
            message = '현재 주문 가능시간이 아닙니다.'
            return JsonResponse({'status': 301, 'message': message})

        order.payment_type = ORDER_PAYMENT_KAKAO_PAY
        order.save()
    except Exception as ex:
        return JsonResponse({'status': 400, 'message': ex})

    try:
        approval_url = '{}{}'.format(EATPLE_KAKAO_API_URL, '/payment/approve')
        encoded_approval_url = urllib.parse.quote(approval_url)

        print(approval_url)
        data = {
            'rest_api_key': KAKAO_REST_API_KEY,
            'cid': KAKAO_PAY_CID,

            'partner_order_id': order.order_id,
            'partner_user_id': order.ordersheet.user.app_user_id,

            'item_name': order.menu.name,
            'item_code': order.menu.menu_id,

            'quantity': 1,

            'total_amount': order.totalPrice,
            'tax_free_amount': 0,

            'approval_url':  'https://talk-plugin.kakao.com/kakaopay/callback?approval_url={encoded_approval_url}'.format(
                encoded_approval_url=encoded_approval_url
            ),
            'cancel_url':  'https://talk-plugin.kakao.com/kakaopay/callback?approval_url={encoded_approval_url}'.format(
                encoded_approval_url=encoded_approval_url
            ),
            'fail_url':  'https://talk-plugin.kakao.com/kakaopay/callback?approval_url={encoded_approval_url}'.format(
                encoded_approval_url=encoded_approval_url
            ),

            'use_shipping': False,

            'order_agreements': [
                {
                    'company': '잇플',
                    'title': '구매조건 확인 및 결제진행 동의',
                    'url': 'https://www.eatple.com'
                }
            ],
        }
    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 300, })

    payload = {
        'status': 200,
        'data': data
    }

    return JsonResponse(payload, status=200)
