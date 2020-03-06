# Define
from eatple_app.define import *

# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Modules
from eatple_app.module_kakao.reponseForm import *
from eatple_app.module_kakao.requestForm import *
from eatple_app.module_kakao.kakaoPay import *
from eatple_app.module_kakao.form import *
from eatple_app.module_kakao.validation import *


class Kakao():
    def getProfile(self, user):
        headers = {
            'Authorization': 'KakaoAK {app_key}'.format(app_key=KAKAO_ADMIN_KEY),
        }

        apiURL = '{shcme}{host}{url}'.format(
            shcme='https://', host='kapi.kakao.com', url='/v2/user/me')

        data = {
            'target_id_type': 'user_id',
            'target_id': user.app_user_id
        }

        try:
            kakaoResponse = requests.post(apiURL, data=data, headers=headers)

        except kakaoResponse.HttpError as http_error:
            print(http_error.code)
            print(http_error.reason)

        try:
            user.nickname = kakaoResponse.json(
            )['kakao_account']['profile']['nickname']
            user.email = kakaoResponse.json(
            )['kakao_account']['email']
            user.phone_number = kakaoResponse.json(
            )['kakao_account']['phone_number']
            user.save()
        except:
            pass

        return user


def getPFriendList(self, user):
    headers = {
        'Authorization': 'KakaoAK {app_key}'.format(app_key=KAKAO_ADMIN_KEY),
    }

    apiURL = '{shcme}{host}{url}'.format(
        shcme='https://', host='kapi.kakao.com', url='/v2/user/me')

    data = {
        'target_id_type': 'user_id',
        'target_id': user.app_user_id
    }

    try:
        kakaoResponse = requests.post(apiURL, data=data, headers=headers)

    except kakaoResponse.HttpError as http_error:
        print(http_error.code)
        print(http_error.reason)

    #print('Header : ', kakaoResponse.headers)
    #print('URL : ', kakaoResponse.url)
    #print('STATUS : ', kakaoResponse.status_code)
    #print('TEXT : ', kakaoResponse.json()['kakao_account'])

    user.nickname = kakaoResponse.json(
    )['kakao_account']['profile']['nickname']
    user.email = kakaoResponse.json(
    )['kakao_account']['email']
    user.phone_number = kakaoResponse.json(
    )['kakao_account']['phone_number']
    user.save()

    return user
