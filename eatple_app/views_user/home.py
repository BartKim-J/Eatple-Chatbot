# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

from eatple_app.views_slack.slack_logger import SlackLogSignUp

# Modules
from eatple_app.module_kakao.reponseForm import *
from eatple_app.module_kakao.requestForm import *
from eatple_app.module_kakao.kakaoPay import *
from eatple_app.module_kakao.form import *
from eatple_app.module_kakao.validation import *

# View-System
from eatple_app.views_system.debugger import *


def isLocationParam(kakaoPayload):
    try:
        param = kakaoPayload.dataActionParams['location']['origin']
        return True
    except (TypeError, AttributeError, KeyError):
        return False


def userSignUp(userProfile):
    nickname = userProfile['nickname']
    phone_number = userProfile['phone_number']
    email = userProfile['email']
    birthyear = userProfile['birthyear']
    birthday = userProfile['birthday']
    gender = userProfile['gender']
    ci = userProfile['ci']
    ci_ci_authenticated_at = userProfile['ci_authenticated_at']
    app_user_id = userProfile['app_user_id']

    if(nickname == None):
        nickname = "N/A"

    if(phone_number == None):
        phone_number = "N/A"

    if(email == None):
        email = "N/A"

    if(birthyear == None):
        birthyear = "N/A"

    if(birthday == None):
        birthday = "N/A"

    if(gender == None):
        gender = "N/A"

    if(ci == None):
        ci = "N/A"

    if(ci_ci_authenticated_at == None):
        ci_ci_authenticated_at = "N/A"

    if(app_user_id == None):
        app_user_id = "N/A"

    user = User.signUp(
        app_user_id=app_user_id,
        nickname=nickname,
        phone_number=phone_number,
        email=email,
        birthyear=birthyear,
        birthday=birthday,
        gender=gender,
        ci=ci,
        ci_authenticated_at=ci_ci_authenticated_at,
    )

    return user


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
            'label': '가입하러 가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_SIGNUP,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    return KakaoInstantForm().Message(
        '아직 잇플 서비스에 가입되지 않은 카카오 계정입니다.',
        '잇플 서비스에 가입하러 가볼까요?',
        buttons=buttons,
    )


def kakaoView_LocationRegistration():
    EatplusSkillLog('Location Registration')

    kakaoForm = KakaoForm()

    buttons = [
        {
            'action': 'block',
            'label': '등록하러 가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_EDIT_LOCATION,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    return KakaoInstantForm().Message(
        '보다 정확한 메뉴를 불러오기 위해 사용자의 위치 정보가 필요해요!',
        '현재 위치를 등록하러 가볼까요?',
        buttons=buttons,
    )


def kakaoView_Home(user):
    EatplusSkillLog('Home')

    kakaoForm = KakaoForm()

    orderManager = UserOrderManager(user)
    orderManager.orderPenddingCleanUp()
    orderManager.availableOrderStatusUpdate()

    orderList = orderManager.getAvailableOrders().filter(Q(ordersheet__user=user))
    orderCount = orderList.count()
    order = orderList.first()

    isOrderEnable = (orderCount != 0)

    # @PROMOTION
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
        {
            'action': 'block',
            'label': '잇플 소개',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_INTRO,
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
    if(isB2BUser(user)):
        KakaoInstantForm().Message(
            '「{}」 v{}.{}.{}({})'.format(
                VERSION_CODE,
                MAJOR_VERSION,
                MINOR_VERSION,
                BUILD_VERSION,
                VERSION_LEVEL,),
            '\'길찾기(카카오 맵)\' 기능이 추가되었습니다.',
            {},
            [],
            kakaoForm
        )
    else:
        # NOT DISPLAY
        pass

    # HEADER
    if(isOrderEnable):
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
    else:
        if(isB2BUser(user)):

            if(settings.SETTING_ID == 'DEPLOY'):
                logoImg = '{}{}'.format(HOST_URL, user.company.logoImgURL())
            else:
                logoImg = '{}{}'.format(HOST_URL, user.company.logoImgURL())
                #logoImg = '{}{}'.format(HOST_URL, HOME_HEAD_BLACK_IMG_URL)

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
        else:
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
    if(isOrderEnable):
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

        kakaoForm.BasicCard_Push(
            '{}'.format(order.store.name),
            '{}'.format(order.store.addr),
            thumbnail,
            buttons
        )
    else:
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


@csrf_exempt
def GET_UserHome(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        user = userValidation(kakaoPayload)
        location = userLocationValidation(user)

        #kakaoPay = KakaoPay()
        # kakaoPay.PushOrderSheet()

        if(user == None):
            try:
                otpURL = kakaoPayload.dataActionParams['user_profile']['origin']
                kakaoResponse = requests.get('{url}?rest_api_key={rest_api_key}'.format(
                    url=otpURL, rest_api_key=KAKAO_REST_API_KEY))

                if(kakaoResponse.status_code == 200):
                    user = userSignUp(kakaoResponse.json())

                    # @SLACK LOGGER
                    SlackLogSignUp(user)

                    return kakaoView_LocationRegistration()

                return kakaoView_SignUp()

            except (RuntimeError, TypeError, NameError, KeyError):
                return kakaoView_SignUp()
        elif(isLocationParam(kakaoPayload)):
            try:
                otpURL = kakaoPayload.dataActionParams['location']['origin']

                kakaoResponse = requests.get('{url}?rest_api_key={rest_api_key}'.format(
                    url=otpURL, rest_api_key=KAKAO_REST_API_KEY))

                if(kakaoResponse.status_code == 200):
                    user = userLocationRegistration(user, kakaoResponse.json())

                    return kakaoView_Home(user)

                return kakaoView_LocationRegistration()
            except (RuntimeError, TypeError, NameError, KeyError):
                return kakaoView_LocationRegistration()
        else:
            return kakaoView_Home(user)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))
