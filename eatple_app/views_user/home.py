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

# Wordings
from eatple_app.views_user.wording import wordings


def userSignUp(userProfile):
    user = User.signUp(
        nickname=userProfile['nickname'],
        profile_image_url=userProfile['profile_image_url'],
        phone_number=userProfile['phone_number'],
        email=userProfile['email'],
        birthyear=userProfile['birthyear'],
        birthday=userProfile['birthday'],
        gender=userProfile['gender'],
        ci=userProfile['ci'],
        ci_authenticated_at=userProfile['ci_authenticated_at'],
        app_user_id=userProfile['app_user_id'],
    )

    return user

def kakaoView_SignUp():
    EatplusSkillLog("Sign Up")

    KakaoForm = Kakao_CarouselForm()
    KakaoForm.BasicCard_Init()

    BTN_MAP = [
        {
            'action': "block",
            'label': "연동하러 가기",
            'messageText': "연동하기",
            'blockId': KAKAO_BLOCK_SIGNUP,
            'extra': {}
        },
    ]
    
    QUICKREPLIES_MAP = []

    thumbnail = {"imageUrl": ""}

    buttons = BTN_MAP

    KakaoForm.BasicCard_Add("아직 잇플에 연동되지 않은 \n카카오 계정입니다.",
                            "함께 연동하러 가볼까요?", thumbnail, buttons)

    for entryPoint in QUICKREPLIES_MAP:
        KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                   entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

    return JsonResponse(KakaoForm.GetForm())


def kakaoView_Home(user):
    EatplusSkillLog("Home")

    KakaoForm = Kakao_CarouselForm()
    KakaoForm.BasicCard_Init()


    BTN_MAP = [
        {
            'action': "block",
            'label': "메뉴보기",
            'messageText': "로딩중..",
            'blockId': KAKAO_BLOCK_GET_MENU,
            'extra': {}
        },
        {
            'action': "block",
            'label': "잇플패스 확인",
            'messageText': "로딩중..",
            'blockId': KAKAO_BLOCK_EATPLE_PASS,
            'extra': {}
        },
        {
            'action': "block",
            'label': "최근 구매내역",
            'messageText': "로딩중..",
            'blockId': KAKAO_BLOCK_RECENT_ORDER,
            'extra': {}
        },
    ]
    
    QUICKREPLIES_MAP = [
        {'action': "message", 'label': wordings.CHANGE_LOCATION_BTN,
            'messageText': wordings.CHANGE_LOCATION_COMMAND,    'blockId': "none", 'extra': {}},

        {'action': "message", 'label': wordings.USER_MANUAL_COMMAND,
            'messageText': wordings.USER_MANUAL_COMMAND,    'blockId': "none", 'extra': {}},
    ]

    thumbnail = {"imageUrl": ""}

    buttons = BTN_MAP

    KakaoForm.BasicCard_Add(wordings.HOME_TITLE_TEXT,
                            wordings.HOME_DESCRIPT_TEXT, thumbnail, buttons)

    for entryPoint in QUICKREPLIES_MAP:
        KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                   entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

    return JsonResponse(KakaoForm.GetForm())


@csrf_exempt
def GET_UserHome(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        user = userValidation(kakaoPayload)

        if(user == None):
            try:
                otpURL = kakaoPayload.dataActionParams['user_profile']['origin']

                kakaoResponse = requests.get("{url}?rest_api_key={rest_api_key}".format(
                    url=otpURL, rest_api_key=KAKAO_REST_API_KEY))

                if(kakaoResponse.status_code == 200):
                    user = userSignUp(kakaoResponse.json())

                    return kakaoView_Home(user)

                return kakaoView_SignUp()

            except (RuntimeError, TypeError, NameError, KeyError):
                return kakaoView_SignUp()
        else:
            return kakaoView_Home(user)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))
