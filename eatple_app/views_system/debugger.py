# View-System
from eatple_app.views_system.include import *
from django.conf import settings

# SKill Log


def EatplusSkillLog(flow='some flow'):
    print('- - - - - - LOG  - - - - - - - -')
    print('- [ {} ]'.format(flow))
    print('-  func() => {}   '.format(sys._getframe(1).f_code.co_name + '()'))
    print('- - - - - - MODE - - - - - - - - -')
    print('-  ORDER TIME CHECK   DEBUG[{}]'.format(ORDER_TIME_CHECK_DEBUG_MODE))
    print('-  VALIDATION         DEBUG[{}]'.format(VALIDATION_DEBUG_MODE))
    print('-  USER ID            DEBUG[{}]'.format(USER_ID_DEBUG_MODE))
    if(USER_ID_DEBUG_MODE):
        print('-       ID : {}'.format(DEBUG_USER_ID))
    print('-  PAYMENT TIME CHECK DEBUG[{}]'.format(PAYMENT_TIME_CHECK_DEBUG_MODE))
    print('- - - - - - DB   - - - - - - - - -')
    print('-  MOUNTED DB - [\'{}\']'.format(settings.DATABASES['default']['NAME']))
    print('- - - - - - - - - - - - - - - - -')
# Error View


def errorView(error_log='error message', view_log='진행하는 도중 문제가생겼어요.', view_sub_log='죄송하지만 처음부터 다시 진행해주세요.'):
    print('- - - - - - - - - - - - - - - - -')
    print('- [ ERROR! ]')
    print('-  func() => {}   '.format(sys._getframe(1).f_code.co_name + '()'))
    print('-  error  => {}   '.format(error_log))
    print('- - - - - - - - - - - - - - - - -')

    kakaoForm = KakaoForm()

    ERROR_QUICKREPLIES_MAP = [
        {
            'action': 'message',
            'label': '🏠  홈',
            'messageText': '🏠  홈',
            'blockId': 'none',
            'extra': {}
        },
    ]

    kakaoForm.BasicCard_Push(
        '⛑ {}'.format(view_log),
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
