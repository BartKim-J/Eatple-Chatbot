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
def GET_KAKAO_PAY_OrderSheet(request):
    print(request)

    try:
        ordersheet_id = request.GET.get('ordersheet_id')
        zip_code = request.GET.get('zip_code')
    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 400, })

    try:
        order = Order.objects.get(order_id=ordersheet_id)
    except:
        # @TODO: Error Case
        #order = None
        order = Order.objects.filter(
            ~Q(menu=None) & Q(totalPrice__lte=1000) & Q(totalPrice__gte=100)).first()

    if(order == None):
        return JsonResponse({'status': 300, })

    try:
        approval_url = 'https://admin.eatple.com/payment/approve'
        encoded_approval_url = urllib.parse.quote(approval_url)
        
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

            'approval_url':  "https://talk-plugin.kakao.com/kakaopay/callback?approval_url={encoded_approval_url}".format(
                encoded_approval_url=encoded_approval_url
            ),
            # 'cancel_url':  "https://plus.kakao.com/talk/bot/@eatple/잇플패스%20확인",
            # 'fail_url':  "https://plus.kakao.com/talk/bot/@eatple/잇플패스%20확인",

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
