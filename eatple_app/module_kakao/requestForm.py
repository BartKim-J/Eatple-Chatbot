# Define
from eatple_app.define import *

# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

#View
from eatple_app.views_system.debugger import EatplusSkillLog, errorView

class KakaoPayLoad():
    def __init__(self, request):
        self.request = request
        #HTTP Request Parsing to Json Type
        self.json_str           = ((request.body).decode('utf-8'))
        self.received_json_data = json.loads(self.json_str)

        #Kakao Payload Parsing
        self.dataUserRequest    = self.received_json_data['userRequest']
        self.dataBot            = self.received_json_data['bot']
        
        self.dataAction         = self.received_json_data['action']
        self.dataActionExtra    = self.dataAction['clientExtra']
        self.dataActionParams   = self.dataAction['detailParams']
        
        # User Properties
        try:
            self.user_properties         = self.dataUserRequest['user']['properties']
 
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.user_properties         = NOT_APPLICABLE


