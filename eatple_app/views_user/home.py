# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.views_user.b2b.home import kakaoView_B2B_Home
# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


def surveyForm(kakaoForm):
    # HEADER
    surveyImg = '{}{}'.format(HOST_URL, EATPLE_SURVEY_IMG)

    thumbnail = {
        'imageUrl': surveyImg,
        'fixedRatio': 'true',
        'width': 800,
        'height': 800,
    }

    buttons = [
        {
            'action': 'block',
            'label': '잇플 불편사항',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_SURVEY_IMPROVEMENTS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
        {
            'action': 'block',
            'label': '주변식당 추천',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_SURVEY_STORE,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    kakaoForm.BasicCard_Push(
        '사용하시는데 불편함이 있으신가요?',
        '말씀해주시면 반영해드릴게요.',
        thumbnail,
        buttons
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

    if(
        answer.find(KAKAO_EMOJI_LOADING) != -1 or
        answer.find('🍽  주문하기/주문확인') != -1 or
        answer.find('📗  매뉴얼') != -1 or
        answer.find('🗺  위치 설정') != -1 or
        answer.find('📖  공지사항') != -1 or
        answer.find('📜  소개') != -1
    ):
        KakaoInstantForm().Message(
            '불편한 점이 아직 입력되지 않았어요.',
            '홈으로 돌아갈려면 확인을 눌러주세요.',
            buttons=buttons,
            kakaoForm=kakaoForm,
        )
    elif(Survey().apply(user, type, answer)):
        KakaoInstantForm().Message(
            '좋은 의견 감사합니다.',
            '전달된 내용 - 「 {} 」'.format(answer),
            buttons=buttons,
            kakaoForm=kakaoForm,
        )
    else:
        pass

    return JsonResponse(kakaoForm.GetForm())


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


def isSurveyImprovementsParam(kakaoPayload):
    try:
        param = kakaoPayload.dataActionParams['survey_improvements']['origin']
        return True
    except (TypeError, AttributeError, KeyError):
        return False


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
        '자주 사용할 위치를 등록해주세요.\n(패스트파이브 신사점의 경우, 인우빌딩으로 등록해주세요)',
        buttons=buttons,
    )


def isLocationParam(kakaoPayload):
    try:
        param = kakaoPayload.dataActionParams['location']['origin']
        return True
    except (TypeError, AttributeError, KeyError):
        return False


def component_LunchHome(kakaoForm, orderManager, user):
    orderList = orderManager.getAvailableOrders().filter(Q(ordersheet__user=user))
    orderCount = orderList.count()
    order = orderList.first()

    lunchPurchaed = orderManager.getAvailableLunchOrder().filter(
        Q(ordersheet__user=user)).exists()

    if(lunchPurchaed):
        buttons = [
            {
                'action': 'block',
                'label': '주문내역 확인',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
                }
            },
        ]
    else:
        buttons = [
            {
                'action': 'block',
                'label': '🌤️  점심 주문하기',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_GET_STORE,
                'extra': {
                    KAKAO_PARAM_SELLING_TIME: SELLING_TIME_LUNCH,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
                }
            },
        ]

    # LUNCH HEADER
    lunchHomeImg = '{}{}'.format(HOST_URL, EATPLE_HOME_LUNCH_IMG)

    thumbnail = {
        'imageUrl': lunchHomeImg,
        'fixedRatio': 'true',
        'width': 800,
        'height': 800,
    }

    kakaoForm.BasicCard_Push(
        '점심 주문 가능/취소 시간',
        '픽업 전날 오후 9시부터 오전 11시까지',
        thumbnail,
        buttons
    )


def component_DinnerHome(kakaoForm, orderManager, user):
    orderList = orderManager.getAvailableOrders().filter(Q(ordersheet__user=user))
    orderCount = orderList.count()
    order = orderList.first()

    dinnerPurchaced = orderManager.getAvailableDinnerOrder().filter(
        Q(ordersheet__user=user)).exists()

    if(dinnerPurchaced):
        buttons = [
            {
                'action': 'block',
                'label': '주문내역 확인',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
                }
            },
        ]
    else:
        buttons = [
            {
                'action': 'block',
                'label': '🌙  저녁 주문하기',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_GET_STORE,
                'extra': {
                    KAKAO_PARAM_SELLING_TIME: SELLING_TIME_DINNER,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
                }
            },
        ]

    # DINNER HEADER
    dinnerHomeImg = '{}{}'.format(HOST_URL, EATPLE_HOME_DINNER_IMG)

    thumbnail = {
        'imageUrl': dinnerHomeImg,
        'fixedRatio': 'true',
        'width': 800,
        'height': 800,
    }

    kakaoForm.BasicCard_Push(
        '저녁 주문 가능/취소 시간',
        '픽업 당일 오후 2시부터 오후 6시까지',
        thumbnail,
        buttons
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

    # MAP
    addressMap = address.split()

    kakaoForm.BasicCard_Push(
        '🗺️  나의 \'잇플\'레이스',
        '[{} {} {}]  인근'.format(
            addressMap[0], addressMap[1], addressMap[2]),
        {},
        []
    )
    kakaoForm.BasicCard_Add()

    orderManager = UserOrderManager(user)
    orderManager.orderPenddingCleanUp()
    orderManager.availableOrderStatusUpdate()

    component_LunchHome(kakaoForm, orderManager, user)
    component_DinnerHome(kakaoForm, orderManager, user)

    kakaoForm.BasicCard_Add()

    buttons = [
        {
            'action': 'block',
            'label': '친구 초대하기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_FRIEND_INVITE,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    if(settings.SETTING_ID == 'DEBUG'):
        kakaoForm.BasicCard_Push(
            '🙌  잇플에 친구를 초대해보세요',
            '친구를 초대하면 2,000원 할인!',
            {},
            buttons
        )
        kakaoForm.BasicCard_Add()
    else:
        pass

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_FriendCode(user):
    kakaoForm = KakaoForm()

    KakaoInstantForm().Message(
        '모든 가입이 완료되었습니다.',
        kakaoForm=kakaoForm
    )

    buttons = [
        {
            'action': 'block',
            'label': '입력하기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_FRIEND_CODE_SUBMIT,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
        {
            'action': 'block',
            'label': '건너뛰기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_GET_STORE,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    kakaoForm.BasicCard_Push(
        '친구 코드가 있다면 입력하기를 눌러 입력해주세요.',
        '',
        thumbnail,
        buttons
    )

    kakaoForm.BasicCard_Add()

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

                return kakaoView_Route_Home(user)
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
        elif(isSurveyImprovementsParam(kakaoPayload)):
            answer = kakaoPayload.dataActionParams['survey_improvements']['origin']
            return kakaoView_SurveyApply(user, SURVEY_TYPE_IMPROVEMENTS, answer)
        else:
            # Get user profile data from Kakao server
            kakao = Kakao()
            user = kakao.getProfile(user)

            return kakaoView_Route_Home(user)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))
