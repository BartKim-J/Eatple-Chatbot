# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *


@csrf_exempt
def GET_KAKAO_Oauth(request):
    try:
        json_str = ((request.body).decode('utf-8'))
        received_json_data = json.loads(json_str)
    except json.decoder.JSONDecodeError:
        pass

    data = {
        'status': 200
    }

    return JsonResponse(data, status=200)
