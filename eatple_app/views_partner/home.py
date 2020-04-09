# View-System
from eatple_app.views_system.include import *
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

    buttons = [
        {
            'action': 'block',
            'label': '가입을 시작해볼까요?',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_PARTNER_SIGNUP,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_PARTNER_HOME
            }
        },
    ]

    return KakaoInstantForm().Message(
        '아직 잇플에 가입되지 않은 파트너 카카오 계정입니다.',
        '',
        buttons=buttons,
    )


def kakaoView_StoreRegistration():
    EatplusSkillLog('Store Registration')

    kakaoForm = KakaoForm()

    buttons = [
        {
            'action': 'block',
            'label': '가게 연동',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_PARTNER_STORE_REGISTRATION,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_PARTNER_HOME
            }
        },
    ]

    return KakaoInstantForm().Message(
        '가게를 계정에 연동해주세요.',
        '',
        buttons=buttons,
    )


def kakaoView_Home(partner):
    EatplusSkillLog('Home')

    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = []

    if(partner.is_staff):
        QUICKREPLIES_MAP.append(            
            {
                'action': 'block',
                'label': '영업 홈',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_PARTNER_DEMO_HOME,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_PARTNER_HOME
                }
            },
        )


    buttons = [
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

    thumbnail = {
        'imageUrl': '{}{}'.format(HOST_URL, partner.store.logoImgURL()),
        'fixedRatio': 'true',
        'width': 800,
        'height': 800,
    }

    kakaoForm.BasicCard_Push(
        '{store} 매장용 카드'.format(store=partner.store.name),
        '조회 시간 : {}'.format(datetime.datetime.now().strftime(
            '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')),
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

                    storeList = Store.objects.filter(crn__CRN_id=CRN)
                    storeListCount = storeList.count()

                    if(storeListCount == 1):
                        partner.storeRegistration(storeList.first())
                    elif(storeListCount > 1):
                        for store in storeList:
                            print(store.name)
                        partner.storeRegistration(storeList.first())
                    else:
                        return errorView('잘못된 사업자 등록번호', '잇플에 등록되지 않은 사업자 번호입니다.')

                    return GET_PartnerHome(request)

            except (RuntimeError, TypeError, NameError, KeyError):
                if(partner == None):
                    return kakaoView_SignUp()
                else:
                    return kakaoView_StoreRegistration()
        else:
            return kakaoView_Home(partner)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))
