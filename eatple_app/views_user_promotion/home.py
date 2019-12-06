# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# Modules
from eatple_app.module_kakao.ReponseForm import *
from eatple_app.module_kakao.RequestForm import *
from eatple_app.module_kakao.Validation import *

# View-System
from eatple_app.views_system.debugger import *

from eatple_app.views import *

MENU_LIST_LENGTH = 5

DISCOUNT_FOR_PROMOTION = 5900
#DISCOUNT_FOR_PROMOTION = None

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Validation
#
# # # # # # # # # # # # # # # # # # # # # # # # #

def areaValidation(kakaoPayload):
    try:
        area = kakaoPayload.dataActionParams['area']['origin']
        
        if(area.count('강남')):
            area_id = 'A' # A = 강남
        elif(area.count('역삼')):
            area_id = 'B'
        else:
            area_id = 'A'
            
        area_code = area[2:3]
        
        return '{id}{code}'.format(id=area_id, code=area_code)
    
    except (TypeError, AttributeError, KeyError):
        return None

def PromotionEatplePassValidation(user):
    orderManager = UserOrderManager(user)
    orderManager.orderPaidCheck()
    
    orderManager.availableOrderStatusUpdate();

    lunchPurchaed = orderManager.getAvailableLunchOrderPurchased().exists()
    dinnerPurchaced = orderManager.getAvailableDinnerOrderPurchased().exists()    
    
    kakaoForm = KakaoForm()

    kakaoForm.QuickReplies_AddWithMap(DEFAULT_QUICKREPLIES_MAP)

    if ((lunchPurchaed or dinnerPurchaced) and user.flag_promotion == False):
        kakaoForm.SimpleText_Add(
            '아직 사용하지 않은 잇플패스가 있어요.\n발급된 잇플패스를 먼저 사용해주세요.'
        )
        return JsonResponse(kakaoForm.GetForm())
     
    if ((lunchPurchaed or dinnerPurchaced) or user.flag_promotion):
        kakaoForm.SimpleText_Add(
            '이미 프로모션에 참여해주셨습니다.\n프로모션은 한 번만 참여 가능합니다.'
        )
        return JsonResponse(kakaoForm.GetForm())

    return None
    
# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
   
def kakaoView_MenuListup(kakaoPayload):
     # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    # User's Eatple Pass Validation
    eatplePassStatus = PromotionEatplePassValidation(user)
    if(eatplePassStatus != None):
        return eatplePassStatus

    area = areaValidation(kakaoPayload)
    if(area == None):
        return errorView('Invalid Area Code', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')
    
    # Order Log Record
    orderRecordSheet = OrderRecordSheet()
    orderRecordSheet.user = user
    orderRecordSheet.recordUpdate(ORDER_RECORD_GET_MENU)

    order = orderValidation(kakaoPayload)
    if(order == None):
        orderSheet = OrderSheet()
        order = orderSheet.pushOrder(
            user=user,
            menu=None,
            store=None,
            pickup_time="00:00",
            totalPrice=0,
            count=1,
            type=ORDER_TYPE_PROMOTION
        )
    else:
        return errorView('Invalid Store Paratmer', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    menuList = Menu.objects.filter(
        store__type=STORE_TYPE_EVENT,
        store__area=area,
        ).order_by('menu_id')[:MENU_LIST_LENGTH]

    if menuList:
        kakaoForm = KakaoForm()

        # Menu Carousel Card Add
        for menu in menuList:
            imageUrl = '{}{}'.format(HOST_URL, menu.imgURL())
            
            thumbnail = {
                'imageUrl': imageUrl,
                'fixedRatio': 'true',
                'width': 800,
                'height': 800,
            }

            kakaoMapUrl = 'https://map.kakao.com/link/map/{},{}'.format(
                menu.store.name, menu.store.place)

            buttons = [
                {
                    'action': 'block',
                    'label': '주문하기',
                    'messageText': '로딩중..',
                    'blockId': KAKAO_BLOCK_USER_PROMOTION,
                    'extra': {
                        KAKAO_PARAM_STORE_ID: menu.store.store_id,
                        KAKAO_PARAM_MENU_ID: menu.menu_id,
                        KAKAO_PARAM_ORDER_ID: order.order_id,
                        KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_PROMOTION
                    }
                },
                {
                    'action': 'webLink',
                    'label': '위치보기',
                    'webLinkUrl': kakaoMapUrl
                },
            ]

            kakaoForm.BasicCard_Push(
                '{}'.format(menu.name), 
                '{}'.format(menu.description), 
                thumbnail, 
                buttons
            )
            
        kakaoForm.BasicCard_Add()
    
    else:
        kakaoForm = KakaoForm()

        kakaoForm.SimpleText_Add('판매중인 메뉴가 없어요...')

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_PROMOTION
            }
        },
    ]

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)       

    return JsonResponse(kakaoForm.GetForm())

def kakaoView_OrderPayment(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_PROMOTION):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    # User's Eatple Pass Validation
    eatplePassStatus = PromotionEatplePassValidation(user)
    if(eatplePassStatus != None):
        return eatplePassStatus

    store = storeValidation(kakaoPayload)
    menu = menuValidation(kakaoPayload)

    if(menu.name.count('점심')):
        pickup_time = '12:00'
    elif(menu.name.count('후식')):
        pickup_time = '14:00'
    else:
        pickup_time = None
    
    if(store == None or menu == None or pickup_time == None):
        return errorView('Invalid Store Paratmer', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    discount = DISCOUNT_FOR_PROMOTION
    if(discount != None):
        discountPrice = menu.price - discount
    else:
        discountPrice = menu.price

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('Invalid Store Paratmer', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')
    else:
        order.user = user
        order.menu = menu
        order.store = store
        
        pickup_time = [x.strip() for x in pickup_time.split(':')]
        currentTime = dateByTimeZone(timezone.now())
        datetime_pickup_time = currentTime.replace(
                                    day=int(menu.name[0:2]),
                                    hour=int(pickup_time[0]), 
                                    minute=int(pickup_time[1]),
                                    second=0,
                                    microsecond=0
                                )

        order.pickup_time = datetime_pickup_time
        order.totalPrice = discountPrice
        order.count = 1
        order.type = ORDER_TYPE_PROMOTION
        order.save()

    # Order Record
    try:
        orderRecordSheet = OrderRecordSheet.objects.latest('update_date')
    except OrderRecordSheet.DoesNotExist:
        orderRecordSheet = OrderRecordSheet()

    if (orderRecordSheet.timeoutValidation()):
        return kakaoView_TimeOut(KAKAO_BLOCK_USER_PROMOTION)

    orderRecordSheet.user = user
    orderRecordSheet.menu = menu
    orderRecordSheet.recordUpdate(ORDER_RECORD_ORDERSHEET_CHECK)

    dataActionExtra = kakaoPayload.dataActionExtra
    dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
    dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_USER_PROMOTION

    kakaoForm = KakaoForm()

    # Menu Carousel Card Add
    thumbnails = [
        {
            'imageUrl': '{}{}'.format(HOST_URL, menu.imgURL()),
            'fixedRatio': 'true',
            'width': 800,
            'height': 800,
        }
    ]

    profile = {
        'nickname': '{name}'.format(name=menu.name),
        'imageUrl': '{}{}'.format(HOST_URL, store.logoImgURL()),
    }

    kakaoMapUrl = 'https://map.kakao.com/link/map/{},{}'.format(
        store.name, menu.store.place)

    buttons = [
        {
            'action': 'webLink',
            'label': '결제하러 가기',
            'messageText': '로딩중..',
            'extra': dataActionExtra,

            'webLinkUrl': 'http://eatple.com/payment?merchant_uid={merchant_uid}&storeName={storeName}&menuName={menuName}&menuPrice={menuPrice}&buyer_name={buyer_name}&buyer_tel={buyer_tel}&buyer_email={buyer_email}'.format(
                merchant_uid=order.order_id,
                storeName=store.name,
                menuName=menu.name,
                menuPrice=order.totalPrice,
                buyer_name=user.app_user_id,
                buyer_tel=str(user.phone_number)[3:13],
                buyer_email=user.email,
            )
        },
    ]

    kakaoForm.ComerceCard_Push(
        '',
        menu.price,
        discount,
        thumbnails,
        profile,
        buttons
    )

    kakaoForm.ComerceCard_Add()

    buttons = [
        {
            'action': 'block',
            'label': '잇플패스 발급',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_PROMOTION,
            'extra': dataActionExtra,
        },
    ]

    kakaoForm.BasicCard_Push(
        ' - 안내사항 -', 
        '메뉴 선택은 픽업 시점에 가능합니다. 특정메뉴가 조기소진될 시 메뉴 선택이 불가할 수 있습니다.\n\n하나/외환/NH는 현재 결제가 불가능합니다. 양해부탁드립니다.',
        {}, []
    )
    kakaoForm.BasicCard_Add()
    
    kakaoForm.BasicCard_Push(
        '결제가 완료되었다면 아래 잇플패스 발급하기 버튼을 눌러주세요.', '', {}, buttons
    )
    kakaoForm.BasicCard_Add()

    GET_PICKUP_TIME_QUICKREPLIES_MAP = [
        {
            'action': 'message', 'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {}
        },
    ]

    kakaoForm.QuickReplies_AddWithMap(GET_PICKUP_TIME_QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())

def kakaoView_OrderPaymentCheck(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_PROMOTION):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    store = storeValidation(kakaoPayload)
    menu = menuValidation(kakaoPayload)
    order = orderValidation(kakaoPayload)
        
    if(order.store != store or order.menu != menu):
        return kakaoView_OrderPayment(kakaoPayload)
    
    if(store == None or menu == None or order == None):
        return errorView('Invalid Store Paratmer', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # Order Record
    try:
        orderRecordSheet = OrderRecordSheet.objects.latest('update_date')
    except OrderRecordSheet.DoesNotExist:
        orderRecordSheet = OrderRecordSheet()

    if (orderRecordSheet.timeoutValidation()):
        return kakaoView_TimeOut(KAKAO_BLOCK_USER_PROMOTION)

    orderRecordSheet.user = user
    orderRecordSheet.menu = menu
    orderRecordSheet.recordUpdate(ORDER_RECORD_PAYMENT)

    dataActionExtra = kakaoPayload.dataActionExtra
    dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
    dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_USER_PROMOTION

    order.orderStatusUpdate()

    if(order.payment_status == IAMPORT_ORDER_STATUS_PAID):
        return kakaoView_EatplePassIssuance(kakaoPayload)
    else:
        kakaoForm = KakaoForm()

        BTN_MAP = [
            {
                'action': 'webLink',
                'label': '결제하러 가기',
                'messageText': '로딩중..',
                'extra': dataActionExtra,

                'webLinkUrl': 'http://eatple.com/payment?merchant_uid={merchant_uid}&storeName={storeName}&menuName={menuName}&menuPrice={menuPrice}&buyer_name={buyer_name}&buyer_tel={buyer_tel}&buyer_email={buyer_email}'.format(
                    merchant_uid=order.order_id,
                    storeName=store.name,
                    menuName=menu.name,
                    menuPrice=order.totalPrice,
                    buyer_name=user.app_user_id,
                    buyer_tel=str(user.phone_number)[3:13],
                    buyer_email=user.email,
                )
            },
            {
                'action': 'block',
                'label': '잇플패스 발급',
                'messageText': '로딩중..',
                'blockId': KAKAO_BLOCK_USER_PROMOTION,
                'extra': dataActionExtra,
            },
        ]

        QUICKREPLIES_MAP = [
            {
                'action': 'message', 'label': '홈으로 돌아가기',
                'messageText': '로딩중..',
                'blockId': KAKAO_BLOCK_USER_HOME,
                'extra': {}
            },
        ]

        thumbnail = {'imageUrl': ''}

        buttons = BTN_MAP

        kakaoForm.BasicCard_Push(
            '아직 결제가 완료되지 않았어요!',
            '{menu} - {price}원'.format(menu=menu.name, price=order.totalPrice),
            thumbnail,
            buttons
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

def kakaoView_EatplePassIssuance(kakaoPayload):
    try:
        # Block Validation
        prev_block_id = prevBlockValidation(kakaoPayload)
        if(prev_block_id != KAKAO_BLOCK_USER_PROMOTION):
            return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 오류가 발생했습니다.')

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

        store = storeValidation(kakaoPayload)
        menu = menuValidation(kakaoPayload)
        order = orderValidation(kakaoPayload)

        order.orderStatusUpdate()

        if(order == None):
            return errorView('Invalid Store Paratmer', '정상적이지 않은 경로거나 이미 발급이 완료되었어요!')

        # Order Record
        try:
            orderRecordSheet = OrderRecordSheet.objects.latest('update_date')
        except OrderRecordSheet.DoesNotExist:
            orderRecordSheet = OrderRecordSheet()

        if (orderRecordSheet.timeoutValidation()):
            return kakaoView_TimeOut(KAKAO_BLOCK_USER_PROMOTION)

        orderRecordSheet.user = user
        orderRecordSheet.menu = menu
        orderRecordSheet.paid = True
        orderRecordSheet.recordUpdate(ORDER_RECORD_PAYMENT_COMPLETED)

        dataActionExtra = kakaoPayload.dataActionExtra
        dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
        dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_USER_PROMOTION

        kakaoForm = KakaoForm()

        thumbnail = {'imageUrl': ''}

        kakaoMapUrl = 'https://map.kakao.com/link/map/{},{}'.format(
            store.name, menu.store.place)

        buttons = []

        kakaoForm.BasicCard_Push(
            '잇플패스가 발급되었습니다.',
                '주문번호: {}\n- - - - - - - - - - - - - - - - -\n - 주문자: {}\n\n - 매장: {}\n - 주소: {}\n - 메뉴: {}\n\n - 결제 금액: {}원\n\n - 픽업 시간: {}\n- - - - - - - - - - - - - - - - -'.format(
                    order.order_id,
                    str(order.ordersheet.user.phone_number)[9:13],
                    order.store.name,
                    order.store.addr,
                    order.menu.name,
                    order.totalPrice,
                    dateByTimeZone(order.pickup_time).strftime('%H:%M'),
            ),
            thumbnail, buttons
        )
        kakaoForm.BasicCard_Add()

        QUICKREPLIES_MAP = [
            {
                'action': 'block',
                'label': '홈으로 돌아가기',
                'messageText': '로딩중..',
                'blockId': KAKAO_BLOCK_USER_HOME,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_PROMOTION
                }
            },
        ]

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))

def kakaoView_TimeOut(blockId):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: blockId
            }
        },
    ]

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    kakaoForm.SimpleText_Add(
        '주문시간이 초과되었습니다.'
    )

    return JsonResponse(kakaoForm.GetForm())


# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
@csrf_exempt
def GET_ProMotionHome(request):
    EatplusSkillLog('GET_ProMotionHome')


    kakaoPayload = KakaoPayLoad(request)
    
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    store = storeValidation(kakaoPayload)
    menu = menuValidation(kakaoPayload)
    order = orderValidation(kakaoPayload)

    #GET MENU
    if(store == None and menu == None and order == None):
        return kakaoView_MenuListup(kakaoPayload)
    
    #ORDER SHEET & CHECK
    elif(store != None and menu != None):
        if(order.store == None or order.menu == None):
            return kakaoView_OrderPayment(kakaoPayload)
        elif(order != None):
            return kakaoView_OrderPaymentCheck(kakaoPayload)
        
    else:
        return kakaoView_MenuListup(kakaoPayload)
    

