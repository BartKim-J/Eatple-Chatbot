# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from eatple_app.views_slack.slack_logger import SlackLogFollow, SlackLogUnfollow, SlackLogSignUp

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# Modules
from eatple_app.module_kakao.reponseForm import *
from eatple_app.module_kakao.requestForm import *
from eatple_app.module_kakao.kakaoPay import *
from eatple_app.module_kakao.form import *
from eatple_app.module_kakao.validation import *

# View-System
from eatple_app.views_system.debugger import *

from eatple_app.views import *


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


def isSignUpDone(app_user_id):
    try:
        user = User.objects.get(app_user_id=app_user_id)
        return user
    except User.DoesNotExist:
        return None


@csrf_exempt
def GET_KAKAO_Signup(request):
    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)

    print(received_json_data)

    if(isSignUpDone(int(received_json_data['app_user_id'])) != None):
        terms_groups = None
    else:
        terms_groups = [{
            'company': '아스테라',
            'required_terms_list': [
                {
                    'id': '1',
                    'title': '잇플 이용약관',
                    'url': 'http://www.eatple.com/tos',
                    'order': 1
                },
                {
                    'id': '2',
                    'title': '잇플 개인정보 수집 및 이용동의 약관',
                    'url': ' http://www.eatple.com/privacy',
                    'order': 2
                },
                {
                    'id': '3',
                    'title': '잇플 위치기반 서비스 이용약관',
                    'url': 'http://www.eatple.com/loc',
                    'order': 3
                },
            ],
        }]

    data = {
        'status': 200,
        'message': '불러오기에 실패했습니다.',
        'service': '잇플',
        'terms_groups': terms_groups

    }

    return JsonResponse(data)


@csrf_exempt
def GET_KAKAO_SignupSetup(request):
    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)
    print(received_json_data)

    otpURL = received_json_data['otp']
    kakaoResponse = requests.get('{url}?rest_api_key={rest_api_key}'.format(
        url=otpURL, rest_api_key=KAKAO_REST_API_KEY))

    user = userSignUp(kakaoResponse.json())

    # @SLACK LOGGER
    SlackLogSignUp(user)

    data = {
        'status': 200,
        'message': '가입에 실패하였습니다.',
        'result_data': {
            'saved': True
        }
    }

    return JsonResponse(data)
