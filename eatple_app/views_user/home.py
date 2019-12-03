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


def userSignUp(userProfile):
    user = User.signUp(
        nickname=userProfile['nickname'],
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
    EatplusSkillLog('Sign Up')

    kakaoForm = KakaoForm()

    BTN_MAP = [
        {
            'action': 'block',
            'label': '연동하러 가기',
            'messageText': '연동하기',
            'blockId': KAKAO_BLOCK_USER_SIGNUP,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    thumbnail = {'imageUrl': ''}

    buttons = BTN_MAP

    kakaoForm.BasicCard_Push(
        '아직 잇플에 연동되지 않은 \n카카오 계정입니다.',
        '함께 연동하러 가볼까요?', 
        thumbnail, 
        buttons
    )
    kakaoForm.BasicCard_Add()
    
    return JsonResponse(kakaoForm.GetForm())


def kakaoView_Home(user):
    EatplusSkillLog('Home')

    kakaoForm = KakaoForm()
    
    orderManager = UserOrderManager(user)
    orderManager.orderPaidCheck()
    orderManager.availableOrderStatusUpdate()        
  
    BTN_MAP = [
        {
            'action': 'block',
            'label': '메뉴보기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_GET_MENU,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
        {
            'action': 'block',
            'label': '잇플패스 확인',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]
    
    """
    {
        'action': 'block',
        'label': '최근 주문내역',
        'messageText': '로딩중..',
        'blockId': KAKAO_BLOCK_USER_ORDER_DETAILS,
        'extra': {
            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
        }
    },
    """
    QUICKREPLIES_MAP = [
    
        {
            'action': 'block', 
            'label': '위치변경',
            'messageText': '로딩중..',    
            'blockId': KAKAO_BLOCK_USER_EDIT_LOCATION,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },

        {
            'action': 'block', 
            'label': '사용 메뉴얼',
            'messageText': '로딩중..',    
            'blockId': KAKAO_BLOCK_USER_MANUAL,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    thumbnail = {
            'imageUrl': '',
            'fixedRatio': 'true',
            'width': 800,
            'height': 800,
        }

    buttons = BTN_MAP

    kakaoForm.BasicCard_Push(
        '잇플 홈 화면입니다.', 
        '아래 명령어 중에 골라주세요!', 
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

        if(user == None):
            try:
                otpURL = kakaoPayload.dataActionParams['user_profile']['origin']

                kakaoResponse = requests.get('{url}?rest_api_key={rest_api_key}'.format(
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
        return errorView('{}'.format(ex))
