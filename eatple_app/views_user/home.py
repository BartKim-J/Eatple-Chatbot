# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# Modules
from eatple_app.module_kakao.responseForm import *
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


def surveyForm(kakaoForm):
    # HEADER
    if(settings.SETTING_ID == 'DEPLOY'):
        homeImg = '{}{}'.format(HOST_URL, HOME_HEAD_IMG_URL)
    else:
        homeImg = '{}{}'.format(HOST_URL, HOME_HEAD_BLACK_IMG_URL)

    thumbnail = {
        'imageUrl': homeImg,
        'fixedRatio': 'false',
        'width': 800,
        'height': 800,
    }

    buttons = [
        {
            'action': 'block',
            'label': '원하는 점포가 없어요',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_SURVEY_STORE,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
        {
            'action': 'block',
            'label': '음식 종류가 부족해요',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_SURVEY_CATEGORY,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    kakaoForm.BasicCard_Push(
        '사용하시는데 불편함이 있으신가요?',
        '알려주시면 반영해드릴게요!',
        thumbnail,
        buttons
    )


def isLocationParam(kakaoPayload):
    try:
        param = kakaoPayload.dataActionParams['location']['origin']
        return True
    except (TypeError, AttributeError, KeyError):
        return False


def isSurveyStoreParam(kakaoPayload):
    try:
        param = kakaoPayload.dataActionParams['survey_store']['origin']
        return True
    except (TypeError, AttributeError, KeyError):
        return False


def isSurveyCategoryParam(kakaoPayload):
    try:
        param = kakaoPayload.dataActionParams['survey_category']['origin']
        return True
    except (TypeError, AttributeError, KeyError):
        return False


def userLocationRegistration(user, locationData):

    try:
        user.location.lat = locationData['latitude']
        user.location.long = locationData['longitude']
        user.location.address = locationData['land_address']['address_name']
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
            address=locationData['land_address']['address_name'],
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


def kakaoView_SurveyApply(user, type, answer):
    EatplusSkillLog('Survey Apply')

    kakaoForm = KakaoForm()

    buttons = [
        {
            'action': 'block',
            'label': '확인',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    if(Survey().apply(user, type, answer)):
        KakaoInstantForm().Message(
            '응답해주셔서 감사합니다.\n전달된 내용은 빠른 시일 내에 반영할게요!',
            '전달된 내용 - 「 {} 」'.format(answer),
            buttons=buttons,
            kakaoForm=kakaoForm,
        )
    else:
        pass

    return JsonResponse(kakaoForm.GetForm())


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
            'label': '🍽  주문하기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_GET_MENU,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
        {
            'action': 'block',
            'label': '📗 메뉴얼',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_MANUAL,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    # MAP
    addressMap = address.split()

    kakaoForm.BasicCard_Push(
        '🗺️  나의 \'잇플\'레이스',
        '[{} {} {}]  인근'.format(
            addressMap[0], addressMap[1], addressMap[2]),
        {},
        []
    )
    # UPDATE
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

    surveyForm(kakaoForm)

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
            'label': '🍽  주문하기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_GET_MENU,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
        {
            'action': 'block',
            'label': '📗 메뉴얼',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_MANUAL,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    # MAP
    addressMap = address.split()

    kakaoForm.BasicCard_Push('🗺️  나의 \'잇플\'레이스',
                             '[{} {} {}]  인근'.format(
                                 addressMap[0], addressMap[1], addressMap[2]),
                             {},
                             []
                             )
    # UPDATE
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
        logoImg = '{}{}'.format(HOST_URL, user.company.logoImgURL())
    else:
        logoImg = '{}{}'.format(HOST_URL, user.company.logoImgURL())
        # logoImg = '{}{}'.format(HOST_URL, HO

    thumbnail = {
        'imageUrl': logoImg,
        'fixedRatio': 'true',
        'width': 800,
        'height': 800,
    }

    kakaoForm.BasicCard_Push(
        '🏢  「{}」 전용 카드입니다.'.format(user.company.name, user.nickname),
        '반갑습니다. {}님'.format(user.nickname),
        thumbnail,
        buttons
    )
    kakaoForm.BasicCard_Add()

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_Order_Home(user, order, address):
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
        return kakaoView_Order_Home(user, order, address)
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

        # Sign Up
        if(user == None):
            return kakaoView_SignUp()
        # Location Register
        elif(isLocationParam(kakaoPayload)):
            try:
                otpURL = kakaoPayload.dataActionParams['location']['origin']

                kakaoResponse = requests.get('{url}?rest_api_key={rest_api_key}&version={version}'.format(
                    url=otpURL, rest_api_key=KAKAO_REST_API_KEY, version="v2"))

                if(kakaoResponse.status_code == 200):
                    user = userLocationRegistration(user, kakaoResponse.json())

                    return kakaoView_Route_Home(user)

                return kakaoView_LocationRegistration()
            except (RuntimeError, TypeError, NameError, KeyError) as ex:
                print(ex)
                return kakaoView_LocationRegistration()
        # Survey
        elif(isSurveyStoreParam(kakaoPayload)):
            answer = kakaoPayload.dataActionParams['survey_store']['origin']
            return kakaoView_SurveyApply(user, SURVEY_TYPE_STORE, answer)
        elif(isSurveyCategoryParam(kakaoPayload)):
            answer = kakaoPayload.dataActionParams['survey_category']['origin']
            return kakaoView_SurveyApply(user, SURVEY_TYPE_CATEGORY, answer)
        else:
            # Get user profile data from Kakao server
            kakao = Kakao()
            user = kakao.getProfile(user)

            return kakaoView_Route_Home(user)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))
