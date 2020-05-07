# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.apis.rest.api.user.validation import *


@csrf_exempt
def POST_KAKAO_OPTION_OptionChoice(request):
    print(request)
    try:
        json_str = ((request.body).decode('utf-8'))
        received_json_data = json.loads(json_str)
    except Exception as ex:
        print(ex)
        return JsonResponse({'status': 400, 'message': ''})

    print(received_json_data['id'])

    payload = {
        'status': 200,
        'data': received_json_data['id'],
    }

    return JsonResponse(payload, status=200)
