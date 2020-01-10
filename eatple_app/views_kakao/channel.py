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

from eatple_app.views import *

@csrf_exempt
def POST_KAKAO_ChannelLog(request):
    json_str           = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)
    
    event = received_json_data['event']
    
    if(event == 'added'):
        SlackLogFollow(received_json_data['id'])
    else:
        SlackLogUnfollow(received_json_data['id'])
    
    
    return JsonResponse({'event': 'Eatple Channel Follow'}, status=201)
