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
        nickname=nickname,
        phone_number=phone_number,
        email=email,
        birthyear=birthyear,
        birthday=birthday,
        gender=gender,
        ci=ci,
        ci_authenticated_at=ci_ci_authenticated_at,
        app_user_id=app_user_id,
    )

    return user

def userLocationRegistration(user, locationData):
    try:
        user.location.lat = locationData['latitude']
        user.location.long = locationData['longitude']
        user.location.address = locationData['address']
        user.location.point = Point(
            y=float(locationData['latitude']), 
            x=float(locationData['longitude']),
        )
        user.location.save()
        
    except User.location.RelatedObjectDoesNotExist:
        location = Location(
            user = user,
            lat = locationData['latitude'],
            long = locationData['longitude'],
            address = locationData['address'],
            point = Point(float(locationData['latitude']), float(locationData['longitude'])),
        )
        location.save()
        
        user.location = location
        user.save()        

    return user
    
def kakaoView_SignUp():
    EatplusSkillLog('Sign Up')

    kakaoForm = KakaoForm()

    BTN_MAP = [
        {
            'action': 'block',
            'label': '연동하러 가기',
            'messageText': '로딩중..',
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

def kakaoView_LocationRegistration():
    EatplusSkillLog('Location Registration')

    kakaoForm = KakaoForm()

    BTN_MAP = [
        {
            'action': 'block',
            'label': '등록하러 가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_EDIT_LOCATION,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    thumbnail = {'imageUrl': ''}

    buttons = BTN_MAP

    kakaoForm.BasicCard_Push(
        '보다 정확한 메뉴를 불러오기 위해 사용자의 위치 정보가 필요해요!',
        '현재 위치를 등록하러 가볼까요?',
        thumbnail,
        buttons
    )
    kakaoForm.BasicCard_Add()

    return JsonResponse(kakaoForm.GetForm())

def kakaoView_Home(user):
    EatplusSkillLog('Home')

    kakaoForm = KakaoForm()

    orderManager = UserOrderManager(user)
    orderManager.orderPanddingCleanUp()
    orderManager.availableOrderStatusUpdate()

    #@PROMOTION
    try:
        address = user.location.address
    except User.location.RelatedObjectDoesNotExist:
        location = Location(
            user=user,
            lat=37.497907,
            long=127.027635,
            address="강남 사거리",
            point=Point(y=37.497907, x=127.027635),
        )
        location.save()

        user.location = location
        user.save()
        
        address = user.location.address
    
    thumbnail = {
        'imageUrl': 'https://maps.googleapis.com/maps/api/staticmap?center={lat},{long}&zoom={zoom}&size=800x400&key={apiKey}'.format(
            zoom=18,
            lat=user.location.lat,
            long=user.location.long,
            apiKey='AIzaSyDRhnn4peSzEfKzQ_WjwDqDF9pzDiuVRhM',
        ),
    }
    
    kakaoForm.BasicCard_Push(
        '등록된 주소',
        '{}'.format(address),
        thumbnail,
        []
    )
    kakaoForm.BasicCard_Add()
    
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

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '최근 주문내역',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_ORDER_DETAILS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
        {
            'action': 'block', 
            'label': '위치 변경',
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
        location = userLocationValidation(user)
        
        if(user == None):
            try:
                otpURL = kakaoPayload.dataActionParams['user_profile']['origin']

                kakaoResponse = requests.get('{url}?rest_api_key={rest_api_key}'.format(
                    url=otpURL, rest_api_key=KAKAO_REST_API_KEY))

                if(kakaoResponse.status_code == 200):
                    user = userSignUp(kakaoResponse.json())
                    
                    #@SLACK LOGGER
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
