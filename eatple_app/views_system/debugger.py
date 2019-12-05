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
from eatple_app.module_kakao.ReponseForm import *

# SKill Log
def EatplusSkillLog(flow='some flow'):
    print('- - - - - - - - - - - - - - - - -')
    print('- [ {} ]'.format(flow))
    print('-  func() => {}   '.format(sys._getframe(1).f_code.co_name + '()'))
    print('- - - - - - - - - - - - - - - - -')

# Error View


def errorView(error_log='error message', view_log='진행하는 도중 문제가생겼어요ㅠㅜ'):
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
            'messageText': '로딩중..',
            'blockId': 'none', 
            'extra': {}
        },
    ]

    kakaoForm.QuickReplies_AddWithMap(ERROR_QUICKREPLIES_MAP)

    kakaoForm.SimpleText_Add(view_log)
    
    return JsonResponse(kakaoForm.GetForm())
