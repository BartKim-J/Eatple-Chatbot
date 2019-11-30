#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import requests
import json

#Models
from eatple_app.define import *

#View
from eatple_app.views_system.debugger import EatplusSkillLog, errorView

#Static Defube 


def getLatLng(addr):
    try:
        url = 'https://dapi.kakao.com/v2/local/search/address.json?query='+addr
        headers = {"Authorization": "KakaoAK {}".format(KAKAO_API_KEY)}
        result = json.loads(str(requests.get(url,headers=headers).text))

        match_first = result['documents'][0]['road_address']

        return "{},{}".format(float(match_first['y']),float(match_first['x']))
    except (RuntimeError, TypeError, NameError, KeyError, IndexError) as ex:
        return errorView("Get Address Error\n- {} ".format(ex))


class KakaoPayLoad():
    def __init__(self, request):
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


