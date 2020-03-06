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
from eatple_app.module_kakao.validation import *

# View-System
from eatple_app.views_system.debugger import *


def partnerSignUp(partnerProfile):
    partner = Partner.signUp(
        nickname=partnerProfile['nickname'],
        phone_number=partnerProfile['phone_number'],
        email=partnerProfile['email'],
        birthyear=partnerProfile['birthyear'],
        birthday=partnerProfile['birthday'],
        gender=partnerProfile['gender'],
        ci=partnerProfile['ci'],
        ci_authenticated_at=partnerProfile['ci_authenticated_at'],
        app_user_id=partnerProfile['app_user_id'],
    )

    return partner


def kakaoView_SignUp():
    EatplusSkillLog('Sign Up')

    kakaoForm = KakaoForm()

    BTN_MAP = [
        {
            'action': 'block',
            'label': '가입하러 가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_PARTNER_SIGNUP,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_PARTNER_HOME
            }
        },
    ]

    QUICKREPLIES_MAP = []

    thumbnail = {'imageUrl': ''}

    buttons = BTN_MAP

    kakaoForm.BasicCard_Push(
        '아직 잇플에 가입되지 않은 파트너 카카오 계정입니다.',
        '함께 가입하러 가볼까요?',
        thumbnail,
        buttons
    )
    kakaoForm.BasicCard_Add()

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_StoreRegistration():
    EatplusSkillLog('Store Registration')

    kakaoForm = KakaoForm()

    BTN_MAP = [
        {
            'action': 'block',
            'label': '등록하러 가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_PARTNER_STORE_REGISTRATION,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_PARTNER_HOME
            }
        },
    ]

    QUICKREPLIES_MAP = []

    thumbnail = {'imageUrl': ''}

    buttons = BTN_MAP

    kakaoForm.BasicCard_Push(
        '파트너 계정에 가게 등록 절차가 남아있습니다!',
        '등록해보러 가볼까요?',
        thumbnail,
        buttons
    )
    kakaoForm.BasicCard_Add()

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_Home(partner):
    EatplusSkillLog('Home')

    kakaoForm = KakaoForm()

    BTN_MAP = [
        {
            'action': 'block',
            'label': '주문 확인하기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_PARTNER_GET_ORDER_DETAILS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_PARTNER_HOME
            }
        },
        {
            'action': 'block',
            'label': ' 정산일정 조회',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_PARTNER_CALCULATE,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_PARTNER_HOME
            }
        },
    ]

    QUICKREPLIES_MAP = [
    ]

    thumbnail = {
        'imageUrl': '{}{}'.format(HOST_URL, partner.store.logoImgURL()),
        'fixedRatio': 'true',
        'width': 800,
        'height': 800,
    }

    buttons = BTN_MAP

    kakaoForm.BasicCard_Push(
        '안녕하세요. {store}점주님!'.format(store=partner.store.name),
        '아래 명령어 중에 골라주세요!',
        thumbnail,
        buttons
    )
    kakaoForm.BasicCard_Add()

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


@csrf_exempt
def GET_PartnerHome(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        partner = partnerValidation(kakaoPayload)

        if(partner == None or partner.store == None):
            try:
                if(partner == None):
                    otpURL = kakaoPayload.dataActionParams['partner_profile']['origin']

                    kakaoResponse = requests.get('{url}?rest_api_key={rest_api_key}'.format(
                        url=otpURL, rest_api_key=KAKAO_REST_API_KEY))

                    if(kakaoResponse.status_code == 200):
                        partner = partnerSignUp(kakaoResponse.json())

                        return GET_PartnerHome(request)

                    return kakaoView_SignUp()
                else:
                    CRN = kakaoPayload.dataActionParams['CRN']['origin']

                    try:
                        store = Store.objects.get(crn__CRN_id=CRN)
                        partner.storeRegistration(store)

                        return GET_PartnerHome(request)
                    except Store.DoesNotExist as ex:
                        return errorView('잘못된 사업자 등록번호', '잇플에 등록되지 않은 사업자 번호입니다.')

                    return kakaoView_StoreRegistration()

            except (RuntimeError, TypeError, NameError, KeyError):
                if(partner == None):
                    return kakaoView_SignUp()
                else:
                    return kakaoView_StoreRegistration()
        else:
            return kakaoView_Home(partner)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))
