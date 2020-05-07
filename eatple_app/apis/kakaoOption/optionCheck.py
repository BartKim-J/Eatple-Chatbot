# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.apis.rest.api.user.validation import *


@csrf_exempt
def GET_KAKAO_OPTION_OptionCheck(request):
    print(request)
    try:
        id = request.GET.get('id')
        print(id)
    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 400, 'message': ''})

    try:
        order = Order.objects.get(order_id=id)

        data = {
            'id': '{product_id}'.format(product_id=order.order_id),
            'name': order.menu.name,
            'price': order.totalPrice,
            'min_quantity': 1,
            'max_quantity': 1,
            'default_quantity': 1,
            'option_groups': [
                {
                    'id': '사이즈',
                    'name': '사이즈',
                    'option_sub_groups': [
                        {
                            'id': '사이즈',
                            'default_option_id': 'N',
                            'options': [
                                {
                                    'id': 'N',
                                    'value': '일반',
                                },
                                {
                                    'id': 'B',
                                    'value': '사이즈 업',
                                    'add_price': 500,
                                },
                            ]
                        }
                    ],
                    'description': '사이즈를 선택해 주세요.',
                    'type': 'SELECT'
                },
                {
                    'id': '추가 수수료',
                    'name': '추가 수수료',
                    'option_sub_groups': [
                        {
                            'id': '추가 수수료',
                            'default_option_id': 'D',
                            'options': [
                                {
                                    'id': 'D',
                                    'value': '배달비',
                                    'add_price': 500,
                                },
                            ]
                        },
                    ],
                    'description': '배달료 500원이 추가됩니다.',
                    'type': 'SELECT'
                },
            ]
        }

    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 300, 'message': '메뉴가 존재하지 않습니다.'})

    payload = {
        'status': 200,
        'data': data,
    }

    return JsonResponse(payload, status=200)
