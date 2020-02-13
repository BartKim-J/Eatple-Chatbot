'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# External Library
import json
import sys

# Models
from eatple_app.define import *

from eatple_app.models import User
from eatple_app.models import Order
from eatple_app.models import Category, Tag
from eatple_app.models import Store, Menu

# View Modules
from eatple_app.module_kakao.reponseForm import *

# SKill Log


def EatplusSkillLog(flow='some flow'):
    print('- - - - - - - - - - - - - - - - -')
    print('- [ {} ]'.format(flow))
    print('-  func() => {}   '.format(sys._getframe(1).f_code.co_name + '()'))
    print('- - - - - - - - - - - - - - - - -')

# Error View


def errorView(error_log='error message', view_log='진행하는 도중 문제가생겼어요..', view_sub_log='죄송하지만 처음부터 다시 진행해주세요!'):
    print('- - - - - - - - - - - - - - - - -')
    print('- [ ERROR! ]')
    print('-  func() => {}   '.format(sys._getframe(1).f_code.co_name + '()'))
    print('-  error  => {}   '.format(error_log))
    print('- - - - - - - - - - - - - - - - -')

    kakaoForm = KakaoForm()

    ERROR_QUICKREPLIES_MAP = [
        {
            'action': 'message',
            'label': '홈으로 돌아가기',
            'messageText': '...',
            'blockId': 'none',
            'extra': {}
        },
    ]

    kakaoForm.BasicCard_Push(
        '{}'.format(view_log),
        '{}\n\n문제 이유 : {}'.format(
            view_sub_log,
            error_log
        ),
        {},
        []
    )
    kakaoForm.BasicCard_Add()

    kakaoForm.QuickReplies_AddWithMap(ERROR_QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())
