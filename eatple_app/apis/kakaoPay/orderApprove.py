# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.apis.slack.slack_logger import Slack_LogFollow, Slack_LogUnfollow
from eatple_app.apis.rest.api.user.validation import *


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

    order = orderValidation(partner_order_id)
    if(order == None):
        message = '주문번호를 찾을 수 없습니다.'
        return JsonResponse({'status': 300, 'message': message})

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
