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

# STATIC CONFIG
MENU_LIST_LENGTH = 10

#DISCOUNT_FOR_DEBUG = 5900
DISCOUNT_FOR_DEBUG = None

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
# @PROMOTION
def eventLock():
    kakaoForm = KakaoForm()

    kakaoForm.BasicCard_Push('프로모션 코드를 대화창에 입력해주세요.',
                             '일반 메뉴의 경우 12월 10일부터 주문하실 수 있어요. 지금은 프로모션 메뉴만 이용해주세요',
                             {},
                             []
                             )

    kakaoForm.BasicCard_Add()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
            }
        },
    ]

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())

def sellingTimeCheck():
    currentDate = dateNowByTimeZone()
    currentDateWithoutTime = currentDate.replace(hour=0, minute=0, second=0, microsecond=0)

    # Time QA DEBUG
    # currentDate = currentDate.replace(hour=16, minute=31, second=0, microsecond=0)
    # currentDateWithoutTime = currentDate.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Prev Lunch Order Time 16:30 ~ 10:30
    prevlunchOrderTimeStart = currentDateWithoutTime + datetime.timedelta(hours=16, minutes=30, days=-1)
    prevlunchOrderTimeEnd = currentDateWithoutTime + datetime.timedelta(hours=10, minutes=30)

    # Dinner Order Time 10:30 ~ 16:30
    dinnerOrderTimeStart = currentDateWithoutTime + datetime.timedelta(hours=10, minutes=30)
    dinnerOrderTimeEnd = currentDateWithoutTime + datetime.timedelta(hours=16, minutes=30)

    # Next Lunch Order Time 16:30 ~ 10:30
    nextlunchOrderTimeStart = currentDateWithoutTime + datetime.timedelta(hours=16, minutes=30)
    nextlunchOrderTimeEnd = currentDateWithoutTime + datetime.timedelta(hours=10, minutes=30, days=1)

    if(dinnerOrderTimeStart <= currentDate) and (currentDate <= dinnerOrderTimeEnd):
        return SELLING_TIME_DINNER
    elif(prevlunchOrderTimeStart < currentDate) and (currentDate < prevlunchOrderTimeEnd):
        return SELLING_TIME_LUNCH
    elif(nextlunchOrderTimeStart < currentDate) and (currentDate < nextlunchOrderTimeEnd):
        return SELLING_TIME_LUNCH
    else:
        return None

def kakaoView_MenuListup(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_HOME and 
       prev_block_id != KAKAO_BLOCK_USER_EATPLE_PASS and
       prev_block_id != KAKAO_BLOCK_USER_ORDER_DETAILS):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    # User's Eatple Pass Validation
    eatplePassStatus = eatplePassValidation(user)
    if(eatplePassStatus != None):
        return eatplePassStatus

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
            type=ORDER_TYPE_NORMAL
        )
    else:
        order.pickup_time = order.pickupTimeToDateTime(pickup_time)
        order.totalPrice = discountPrice
        order.save()

    # currentSellingTime = sellingTimeCheck()
    currentSellingTime = SELLING_TIME_LUNCH

    menuList = Menu.objects.annotate(
        distance=Distance(F('store__place__point'), user.location.point) * 100 * 1000
    ).filter(
        sellingTime=currentSellingTime, 
        store__type=STORE_TYPE_NORMAL,
        
        status=OC_OPEN,
        store__status=OC_OPEN,
        
        distance__lte=700
    ).order_by(F'distance')

    kakaoForm = KakaoForm()

    #@PROMOTION
    kakaoForm.BasicCard_Push('# 프로모션에 참가하실 분들은 발급된 코드를 대화창에 입력해주세요.', 
                            '일반 메뉴는 6000원에 구매하실수 있습니다.',
                            {}, 
                            []
                        )
    
    kakaoForm.BasicCard_Add()
    
    if menuList:
    
        # Menu Carousel Card Add
        for menu in menuList:
            imageUrl = '{}{}'.format(HOST_URL, menu.imgURL())
                
            distance = menu.distance
            walkTime = round((distance / 100) * 1.9)
            
            if(walkTime <= 3):
                walkTime = 3
            
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
                    'blockId': KAKAO_BLOCK_USER_SET_PICKUP_TIME,
                    'extra': {
                        KAKAO_PARAM_STORE_ID: menu.store.store_id,
                        KAKAO_PARAM_MENU_ID: menu.menu_id,
                        KAKAO_PARAM_ORDER_ID: order.order_id,
                        KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
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
                '{} - 약 도보 {} 분\n{}'.format(menu.store.name, walkTime, menu.description, ), 
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
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
            }
        },
    ]

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)       

    return JsonResponse(kakaoForm.GetForm())

def kakaoView_PickupTime(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_GET_MENU and prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # @DEBUG
    #return eventLock()

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    
    order = orderValidation(kakaoPayload)
    if(order.menu != None or order.store != None):
        orderManager = UserOrderManager(user)
        orderManager.orderPaidCheck()
        
        order = orderValidation(kakaoPayload)
        
        if(order.payment_status == IAMPORT_ORDER_STATUS_PAID):
            return errorView('Invalid Block Access', '이미 주문이 완료되었습니다!\n픽업시간 변경을 원하시면 잇플패스 내역에서\n 픽업시간을 변경해주세요.')
    
    else:
        # User's Eatple Pass Validation
        eatplePassStatus = eatplePassValidation(user)
        if(eatplePassStatus != None):
            return eatplePassStatus

    store = storeValidation(kakaoPayload)
    menu = menuValidation(kakaoPayload)
    
    if(store == None or menu == None):
        return errorView('Invalid Store Paratmer', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')



    currentSellingTime = sellingTimeCheck()
    
    if (currentSellingTime == None):
        return errorView('Get Invalid Selling Time', '잘못된 주문 시간입니다.')
    elif currentSellingTime == SELLING_TIME_DINNER:
        '''
            @NOTE Dinner Time Close In Alpha 
        '''
        
        return errorView('Get Invalid Selling Time', '오늘 점심은 이미 마감되었어요.\n내일 점심을 기대해주세요.')


    # Order Record
    try:
        orderRecordSheet = OrderRecordSheet.objects.latest('update_date')
    except OrderRecordSheet.DoesNotExist:
        orderRecordSheet = OrderRecordSheet()

    if (orderRecordSheet.timeoutValidation()):
        return kakaoView_TimeOut(KAKAO_BLOCK_USER_SET_PICKUP_TIME)

    orderRecordSheet.user = user
    orderRecordSheet.menu = menu
    orderRecordSheet.recordUpdate(ORDER_RECORD_SET_PICKUP_TIEM)

    kakaoForm = KakaoForm()
    
    kakaoForm.BasicCard_Push('픽업시간을 설정해주세요.', 
                             '{} - {}'.format(menu.store.name, menu.name), 
                             {}, 
                             []
                             )
    
    kakaoForm.BasicCard_Add()

    PICKUP_TIME_QUICKREPLIES_MAP = []

    pickupTimes = menu.pickupTime.filter(sellingTime=currentSellingTime)

    order = orderValidation(kakaoPayload)
        
    for pickupTime in pickupTimes:
        dataActionExtra = {
            KAKAO_PARAM_STORE_ID: menu.store.store_id,
            KAKAO_PARAM_MENU_ID: menu.menu_id,
            KAKAO_PARAM_ORDER_ID: order.order_id,
            KAKAO_PARAM_PICKUP_TIME: pickupTime.time.strftime('%H:%M'),
            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_SET_PICKUP_TIME
        }
        
        if(order != None):
            dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
        
        kakaoForm.QuickReplies_Add(
            'block',
            pickupTime.time.strftime('%H:%M'),
            '로딩중..',
            KAKAO_BLOCK_USER_SET_ORDER_SHEET,
            dataActionExtra
        )

    return JsonResponse(kakaoForm.GetForm())

def kakaoView_OrderPayment(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_SET_PICKUP_TIME and prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')
    
    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 잘못된 계정입니다.')
    
    # User's Eatple Pass Validation
    eatplePassStatus = eatplePassValidation(user)
    if(eatplePassStatus != None):
        return eatplePassStatus

    store = storeValidation(kakaoPayload)
    menu = menuValidation(kakaoPayload)
    pickup_time = pickupTimeValidation(kakaoPayload)
    
    if(store == None or menu == None or pickup_time == None ):
        return errorView('Invalid Store Paratmer', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    discount = DISCOUNT_FOR_DEBUG
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
        order.pickup_time = order.pickupTimeToDateTime(pickup_time)
        order.totalPrice = discountPrice
        order.count = 1
        order.type = ORDER_TYPE_NORMAL
        order.save()

    # Order Record
    try:
        orderRecordSheet = OrderRecordSheet.objects.latest('update_date')
    except OrderRecordSheet.DoesNotExist:
        orderRecordSheet = OrderRecordSheet()

    if (orderRecordSheet.timeoutValidation()):
        return kakaoView_TimeOut(KAKAO_BLOCK_USER_SET_ORDER_SHEET)

    orderRecordSheet.user = user
    orderRecordSheet.menu = menu
    orderRecordSheet.recordUpdate(ORDER_RECORD_ORDERSHEET_CHECK)
    
    dataActionExtra = kakaoPayload.dataActionExtra
    dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
    dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_USER_SET_ORDER_SHEET

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
        'nickname': '{name} - [ 픽업 : {pickup_time} ]'.format(name=menu.name, pickup_time=pickup_time),
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
            'blockId': KAKAO_BLOCK_USER_SET_ORDER_SHEET,
            'extra': dataActionExtra,
        },
    ]
    kakaoForm.BasicCard_Push('결제가 완료되었다면 아래 잇플패스 발급하기 버튼을 눌러주세요.', '', {}, buttons)
    kakaoForm.BasicCard_Add()
    
    GET_PICKUP_TIME_QUICKREPLIES_MAP = [
        {
            'action': 'block', 'label': '픽업시간 변경하기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_SET_PICKUP_TIME,
            'extra': dataActionExtra
        },
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
    if(prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
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
        
    if(store == None or menu == None or order == None ):
        return errorView('Invalid Store Paratmer', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # Order Record
    try:
        orderRecordSheet = OrderRecordSheet.objects.latest('update_date')
    except OrderRecordSheet.DoesNotExist:
        orderRecordSheet = OrderRecordSheet()
        
    if (orderRecordSheet.timeoutValidation()):
        return kakaoView_TimeOut(KAKAO_BLOCK_USER_SET_ORDER_SHEET)

    orderRecordSheet.user = user
    orderRecordSheet.menu = menu
    orderRecordSheet.recordUpdate(ORDER_RECORD_PAYMENT)
    
    dataActionExtra = kakaoPayload.dataActionExtra
    dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
    dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_USER_SET_ORDER_SHEET

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
                'blockId': KAKAO_BLOCK_USER_SET_ORDER_SHEET,
                'extra': dataActionExtra,
            },
        ]
        
        QUICKREPLIES_MAP = [
            {
                'action': 'block', 'label': '픽업시간 변경하기',
                'messageText': '로딩중..',
                'blockId': KAKAO_BLOCK_USER_SET_PICKUP_TIME,
                'extra': dataActionExtra
            },
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
        if(prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
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
            return kakaoView_TimeOut(KAKAO_BLOCK_USER_SET_ORDER_SHEET)

        orderRecordSheet.user = user
        orderRecordSheet.menu = menu
        orderRecordSheet.paid = True
        orderRecordSheet.recordUpdate(ORDER_RECORD_PAYMENT_COMPLETED)

        dataActionExtra = kakaoPayload.dataActionExtra
        dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
        dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_USER_SET_ORDER_SHEET

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
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_SET_ORDER_SHEET
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
def GET_Menu(request):
    EatplusSkillLog('Get Menu')

    kakaoPayload = KakaoPayLoad(request)
    
    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)
    
    return kakaoView_MenuListup(kakaoPayload)



@csrf_exempt
def SET_PickupTime(request):
    EatplusSkillLog('Get PickupTime')

    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        return kakaoView_PickupTime(kakaoPayload)
    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))

@csrf_exempt
def SET_OrderSheet(request):
    EatplusSkillLog('Order Sheet Check')
    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)
        
        # Block Validation
        prev_block_id = prevBlockValidation(kakaoPayload)
        if(prev_block_id != KAKAO_BLOCK_USER_SET_PICKUP_TIME and prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
            return errorView('Invalid Store Paratmer', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

        if(prev_block_id == KAKAO_BLOCK_USER_SET_PICKUP_TIME):
            return kakaoView_OrderPayment(kakaoPayload)
        elif(prev_block_id == KAKAO_BLOCK_USER_SET_ORDER_SHEET):
            return kakaoView_OrderPaymentCheck(kakaoPayload)
        
    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))

