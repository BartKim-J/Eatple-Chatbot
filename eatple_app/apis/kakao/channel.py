# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.views import *


@csrf_exempt
def POST_KAKAO_ChannelLog(request):
    try:
        json_str = ((request.body).decode('utf-8'))
        received_json_data = json.loads(json_str)
    except json.decoder.JSONDecodeError:
        pass

    event = received_json_data['event']

    if(event == 'added'):
        SlackLogFollow(received_json_data['id'])
    else:
        SlackLogUnfollow(received_json_data['id'])

    return JsonResponse({'event': 'Eatple Channel Follow'}, status=201)
