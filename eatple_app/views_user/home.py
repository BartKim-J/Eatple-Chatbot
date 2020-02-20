# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# Modules
from eatple_app.module_kakao.reponseForm import *
from eatple_app.module_kakao.requestForm import *
from eatple_app.module_kakao.kakaoPay import *
from eatple_app.module_kakao.kakao import *
from eatple_app.module_kakao.form import *
from eatple_app.module_kakao.validation import *

# View-System
from eatple_app.views_system.debugger import *

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


def isLocationParam(kakaoPayload):
    try:
        param = kakaoPayload.dataActionParams['location']['origin']
        return True
    except (TypeError, AttributeError, KeyError):
        return False


def userLocationRegistration(user, locationData):

    try:
        user.location.lat = locationData['latitude']
        user.location.long = locationData['longitude']
        user.location.address = locationData['address']

        # @TODO will update kakao location api
        # user.location.address = locationData['road_address']['address_name']
        user.location.point = Point(
            y=float(locationData['latitude']),
            x=float(locationData['longitude']),
        )
        user.location.save()

    except User.location.RelatedObjectDoesNotExist:
        location = Location(
            user=user,
            lat=locationData['latitude'],
            long=locationData['longitude'],
            address=locationData['address'],
            point=Point(float(locationData['latitude']), float(
                locationData['longitude'])),
        )
        location.save()

        user.location = location
        user.save()

    return user


def kakaoView_SignUp():
    EatplusSkillLog('Sign Up')

    kakaoForm = KakaoForm()

    buttons = [
        {
            'action': 'block',
            'label': '가입을 시작해볼까요?',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_SIGNUP,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    return KakaoInstantForm().Message(
        '아직 잇플에 가입하지 않은 계정입니다.',
        '',
        buttons=buttons,
    )


def kakaoView_LocationRegistration():
    EatplusSkillLog('Location Registration')

    kakaoForm = KakaoForm()

    buttons = [
        {
            'action': 'block',
            'label': '위치 등록하기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_EDIT_LOCATION,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
        {
            'action': 'block',
            'label': '나중에 하기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    return KakaoInstantForm().Message(
        '잇플은 위치 기반으로 주변 맛집을 추천해드리고 있습니다.',
        '자주 사용할 위치를 한 번만 등록해주세요!',
        buttons=buttons,
    )


def kakaoView_Home(user, address):
    EatplusSkillLog('Home')

    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '최근 주문내역',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_ORDER_DETAILS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    buttons = [
        {
            'action': 'block',
            'label': '주문하러 가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_GET_MENU,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
        {
            'action': 'block',
            'label': '사용 메뉴얼',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_MANUAL,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    # UPDATE NOTIY
    kakaoForm.BasicCard_Push(
        '📌 「{}」 v{}.{}.{}({})'.format(
            VERSION_CODE,
            MAJOR_VERSION,
            MINOR_VERSION,
            BUILD_VERSION,
            VERSION_LEVEL,),
        '🛠️ 업데이트 내역을 확인하세요. ➔',
        {},
        [],
    )
    kakaoForm.BasicCard_Push(
        '🔗 \'길찾기(카카오 맵)\' 기능 추가',
        '복사하지 말고 바로 카카오 맵으로 길찾기!',
        {},
        [],
    )
    kakaoForm.BasicCard_Add()

    # HEADER
    if(settings.SETTING_ID == 'DEPLOY'):
        homeImg = '{}{}'.format(HOST_URL, HOME_HEAD_IMG_URL)
    else:
        homeImg = '{}{}'.format(HOST_URL, HOME_HEAD_BLACK_IMG_URL)

    thumbnail = {
        'imageUrl': homeImg,
        'fixedRatio': 'true',
        'width': 800,
        'height': 800,
    }

    description = '\'주변 맛집에서 갓 만든 도시락, 잇플\' 입니다.'

    kakaoForm.BasicCard_Push(
        '안녕하세요!! {}님'.format(user.nickname),
        '{}'.format(description),
        thumbnail,
        buttons
    )

    # MAP
    thumbnail = {
        'imageUrl': 'https://maps.googleapis.com/maps/api/staticmap?center={lat},{long}&maptype=mobile&zoom={zoom}&markers=size:mid%7C{lat},{long}&size=500x500&key={apiKey}'.format(
            zoom=18,
            lat=user.location.lat,
            long=user.location.long,
            apiKey='AIzaSyDRhnn4peSzEfKzQ_WjwDqDF9pzDiuVRhM',
        ),
        'fixedRatio': 'true',
        'width': 800,
        'height': 800,
    }
    buttons = [
        {
            'action': 'block',
            'label': '자주 사용하는 위치 변경',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_EDIT_LOCATION,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    kakaoForm.BasicCard_Push(
        '등록된 주소',
        '{}'.format(address),
        thumbnail,
        buttons
    )

    kakaoForm.BasicCard_Add()

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_B2B_Home(user, address):
    EatplusSkillLog('Home')

    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '최근 주문내역',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_ORDER_DETAILS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    buttons = [
        {
            'action': 'block',
            'label': '주문하러 가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_GET_MENU,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
        {
            'action': 'block',
            'label': '사용 메뉴얼',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_MANUAL,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    # UPDATE
    kakaoForm.BasicCard_Push(
        '📌 「{}」 v{}.{}.{}({})'.format(
            VERSION_CODE,
            MAJOR_VERSION,
            MINOR_VERSION,
            BUILD_VERSION,
            VERSION_LEVEL,),
        '업데이트 내역을 확인해보세요! ➔',
        {},
        [],
    )
    kakaoForm.BasicCard_Push(
        '🔗 \'주문 완료\' 절차 간소화',
        '픽업시간 선택 후 바로 잇플패스가 발급돼요!',
        {},
        [],
    )
    kakaoForm.BasicCard_Push(
        '🔗 \'길찾기(카카오 맵)\' 기능 추가',
        '복사하지 말고 바로 카카오 맵으로 길찾기!',
        {},
        [],
    )
    kakaoForm.BasicCard_Add()

    # HEADER
    if(settings.SETTING_ID == 'DEPLOY'):
        logoImg = '{}{}'.format(HOST_URL, user.company.logoImgURL())
    else:
        logoImg = '{}{}'.format(HOST_URL, user.company.logoImgURL())
        # logoImg = '{}{}'.format(HOST_URL, HOME_HEAD_BLACK_IMG_URL)

    thumbnail = {
        'imageUrl': logoImg,
        'fixedRatio': 'true',
        'width': 800,
        'height': 800,
    }

    kakaoForm.BasicCard_Push(
        '{} 홈 화면입니다.'.format(user.company.name, user.nickname),
        '반갑습니다. {}님'.format(user.nickname),
        thumbnail,
        buttons
    )

    # MAP
    thumbnail = {
        'imageUrl': 'https://maps.googleapis.com/maps/api/staticmap?center={lat},{long}&maptype=mobile&zoom={zoom}&markers=size:mid%7C{lat},{long}&size=500x500&key={apiKey}'.format(
            zoom=18,
            lat=user.location.lat,
            long=user.location.long,
            apiKey='AIzaSyDRhnn4peSzEfKzQ_WjwDqDF9pzDiuVRhM',
        ),
        'fixedRatio': 'true',
        'width': 800,
        'height': 800,
    }
    buttons = [
        {
            'action': 'block',
            'label': '자주 사용하는 위치 변경',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_EDIT_LOCATION,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    kakaoForm.BasicCard_Push(
        '등록된 주소',
        '{}'.format(address),
        thumbnail,
        buttons
    )

    kakaoForm.BasicCard_Add()

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_order_Home(user, order, address):
    EatplusSkillLog('Home')

    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '최근 주문내역',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_ORDER_DETAILS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    buttons = [
        {
            'action': 'block',
            'label': '주문하러 가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_GET_MENU,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
        {
            'action': 'block',
            'label': '사용 메뉴얼',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_MANUAL,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    # HEADER
    isCafe = order.store.category.filter(name="카페").exists()
    if(isCafe):
        pickupTimeStr = dateByTimeZone(order.pickup_time).strftime(
            '%-m월 %-d일 오전 11시 30분 ~ 오후 4시')
    else:
        pickupTimeStr = dateByTimeZone(order.pickup_time).strftime(
            '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')

    thumbnail = {
        'imageUrl': '{}{}'.format(HOST_URL, order.menu.imgURL()),
        'fixedRatio': 'true',
        'width': 800,
        'height': 800,
    }

    buttons[0] = {
        'action': 'block',
        'label': '잇플패스 확인',
        'messageText': KAKAO_EMOJI_LOADING,
        'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
        'extra': {
            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
        }
    }

    description = '픽업은 {} 입니다'.format(pickupTimeStr,)

    kakaoForm.BasicCard_Push(
        '안녕하세요!! {}님'.format(user.nickname),
        '{}'.format(description),
        thumbnail,
        buttons
    )

    # MAP
    kakaoMapUrl = 'https://map.kakao.com/link/map/{name},{place}'.format(
        name=order.store.name,
        place=order.store.place
    )

    kakaoMapUrlAndriod = 'http://m.map.kakao.com/scheme/route?ep={place}&by=FOOT'.format(
        place=order.store.place
    )

    kakaoMapUrlIOS = 'http://m.map.kakao.com/scheme/route?ep={place}&by=FOOT'.format(
        place=order.store.place
    )

    thumbnail = {
        'imageUrl': 'https://maps.googleapis.com/maps/api/staticmap?center={lat},{long}&maptype=mobile&zoom={zoom}&markers=size:mid%7C{lat},{long}&size=500x500&key={apiKey}'.format(
            zoom=18,
            lat=order.store.place.lat,
            long=order.store.place.long,
            apiKey='AIzaSyDRhnn4peSzEfKzQ_WjwDqDF9pzDiuVRhM',
        ),
        'fixedRatio': 'true',
        'width': 800,
        'height': 800,
    }
    buttons = [
        {
            'action': 'osLink',
            'label': '길찾기',
            'osLink': {
                'android': kakaoMapUrlAndriod,
                'ios': kakaoMapUrlIOS,
                'pc': kakaoMapUrl,
            }
        },
    ]

    KakaoInstantForm().Message(
        '{}'.format(order.store.name),
        '{}'.format(order.store.addr),
        thumbnail=thumbnail,
        buttons=buttons,
        kakaoForm=kakaoForm
    )

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_Route_Home(user):
    try:
        address = user.location.address
    except User.location.RelatedObjectDoesNotExist:
        location = Location(
            user=user,
            lat=LOCATION_DEFAULT_LAT,
            long=LOCATION_DEFAULT_LNG,
            address=LOCATION_DEFAULT_ADDR,
            point=Point(y=LOCATION_DEFAULT_LAT, x=LOCATION_DEFAULT_LNG),
        )
        location.save()

        user.location = location
        user.save()

        address = user.location.address

    orderManager = UserOrderManager(user)
    orderManager.orderPenddingCleanUp()
    orderManager.availableOrderStatusUpdate()

    orderList = orderManager.getAvailableOrders().filter(Q(ordersheet__user=user))
    orderCount = orderList.count()
    order = orderList.first()

    isOrderEnable = (orderCount != 0)

    if(isOrderEnable):
        return kakaoView_order_Home(user, order, address)
    else:
        if(isB2BUser(user)):
            return kakaoView_B2B_Home(user, address)
        else:
            return kakaoView_Home(user, address)

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


@csrf_exempt
def GET_UserHome(request):
    EatplusSkillLog('GET_UserHome')

    try:
        kakaoPayload = KakaoPayLoad(request)

        user = userValidation(kakaoPayload)
        location = userLocationValidation(user)

        #kakaoPay = KakaoPay()
        # return kakaoPay.PushOrderSheet(user)

        # Sign Up
        if(user == None):
            return kakaoView_SignUp()
        # Location Register
        elif(isLocationParam(kakaoPayload)):
            try:
                otpURL = kakaoPayload.dataActionParams['location']['origin']

                kakaoResponse = requests.get('{url}?rest_api_key={rest_api_key}'.format(
                    url=otpURL, rest_api_key=KAKAO_REST_API_KEY))

                if(kakaoResponse.status_code == 200):
                    user = userLocationRegistration(user, kakaoResponse.json())

                    return kakaoView_Route_Home(user)

                return kakaoView_LocationRegistration()
            except (RuntimeError, TypeError, NameError, KeyError):
                return kakaoView_LocationRegistration()
        else:
            # Get user profile data from Kakao server
            kakao = Kakao()
            user = kakao.getProfile(user)

            return kakaoView_Route_Home(user)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))
