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

from eatple_app.views import *
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static Functions
#
# # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
DEFAULT_QUICKREPLIES_MAP = [
    {
        'action': "message", 
        'label': wordings.RETURN_HOME_QUICK_REPLISE, 
        'messageText': wordings.RETURN_HOME_QUICK_REPLISE, 
        'blockId': "none",
        'extra': {}
    },
]

@csrf_exempt
def GET_UserManual(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        EatplusSkillLog("User Manual Flow")

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        buttons = [
            # No Buttons
        ]

        userManuals = UserManual.objects.all()

        for manualPage in userManuals:

            thumbnail = {"imageUrl": "{}{}".format(
                HOST_URL, manualPage.imgURL())}

            KakaoForm.BasicCard_Add(
                manualPage.title, manualPage.description, thumbnail, buttons)

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))



@csrf_exempt
def GET_UserIntro(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        EatplusSkillLog("Partner Manual Flow")

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        buttons = [
            # No Buttons
        ]

        userIntros = UserIntro.objects.all()

        for introPage in userIntros:
            thumbnail = {"imageUrl": "{}{}".format(
                HOST_URL, introPage.imgURL())}

            KakaoForm.BasicCard_Add(
                introPage.title, introPage.description, thumbnail, buttons)

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))
