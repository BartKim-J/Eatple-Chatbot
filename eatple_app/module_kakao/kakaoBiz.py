# Define
from eatple_app.define import *

# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Modules
from eatple_app.module_kakao.responseForm import *
from eatple_app.module_kakao.requestForm import *
from eatple_app.module_kakao.kakaoPay import *
from eatple_app.module_kakao.kakaoBiz import *
from eatple_app.module_kakao.form import *
from eatple_app.module_kakao.validation import *


KAKAO_BIZ_HOST_URL = 'talkapi.lgcns.com'

LG_CNS_API_KEY = 'HWJAKot/V7GtnRdKxnuqCA=='
LG_CNS_API_ID = 'eatple2020'
LG_CNS_SERVICE_ID = 1910037945


class KakaoBiz():
    def request(self, message, phone_number):
        headers = {
            'authToken': LG_CNS_API_KEY,
            'serverName': LG_CNS_API_ID,
            'paymentType': 'P',
        }

        data = {
            'service': LG_CNS_SERVICE_ID,

            'message': message,
            'mobile': phone_number,

            'template': '10008',
        }

        apiURL = '{shcme}{host}{url}'.format(
            shcme='https://', host=KAKAO_BIZ_HOST_URL, url='/request/kakao.json')

        kakaoResponse = requests.post(
            apiURL, data=json.dumps(data), headers=headers)

        print('Header : ', kakaoResponse.headers)
        print('URL : ', kakaoResponse.url)
        print('STATUS : ', kakaoResponse.status_code)
        print('TEXT : ', kakaoResponse.text)

        return kakaoResponse
