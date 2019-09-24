'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import requests
import json

#Models
from eatplus_app.define import EP_define

#View
from eatplus_app.views_system.debugger import EatplusSkillLog, errorView

#Static Defube 
KAKAO_API_KEY = "d62991888c78ec58d809bdc591eb62f6"

'''
    @name getLatLng
    @param address
    
    @note
    @bug
    @tood
'''
def getLatLng(addr):
    try:
        url = 'https://dapi.kakao.com/v2/local/search/address.json?query='+addr
        headers = {"Authorization": "KakaoAK {}".format(KAKAO_API_KEY)}
        result = json.loads(str(requests.get(url,headers=headers).text))

        match_first = result['documents'][0]['road_address']

        return "{},{}".format(float(match_first['y']),float(match_first['x']))
    except (RuntimeError, TypeError, NameError, KeyError, IndexError) as ex:
        return errorView("Get Address Error\n- {} ".format(ex))

'''
    @name KakaoPayload
    @param httpRequest

    @note
    @bug
    @tood
'''
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
        
        #ID Parsing
        try:
            self.userID         = self.dataUserRequest['user']['id']
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.userID         = EP_define.NOT_APPLICABLE

        try:
            self.orderID         = self.dataActionExtra[EP_define.KAKAO_PARAM_ORDER_ID]
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.orderID         = EP_define.NOT_APPLICABLE

        try:
            self.storeID         = self.dataActionExtra[EP_define.KAKAO_PARAM_STORE_ID]
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.storeID         = EP_define.NOT_APPLICABLE

        try:
            self.menuID          = self.dataActionExtra[EP_define.KAKAO_PARAM_MENU_ID]
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.menuID          = EP_define.NOT_APPLICABLE

        #Menu Category
        try:
            self.menuCategory      = self.dataActionParams[EP_define.KAKAO_PARAM_MENU_CATEGORY]['origin']
            if not self.dataActionExtra is None: 
                self.dataActionExtra[EP_define.KAKAO_PARAM_MENU_CATEGORY] = self.menuCategory
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.menuCategory       = EP_define.NOT_APPLICABLE
            pass
        if not self.dataActionExtra is None:
            try:
                self.menuCategory      = self.dataActionExtra[EP_define.KAKAO_PARAM_MENU_CATEGORY]
            except (RuntimeError, TypeError, NameError, KeyError) as ex:
                pass

        #Selling Time
        try:
            self.sellingTime      = self.dataActionParams[EP_define.KAKAO_PARAM_SELLING_TIME]['origin']
            if not self.dataActionExtra is None: 
                self.dataActionExtra[EP_define.KAKAO_PARAM_SELLING_TIME] = self.sellingTime
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.sellingTime       = EP_define.NOT_APPLICABLE
            pass
        if not self.dataActionExtra is None:
            try:
                self.sellingTime      = self.dataActionExtra[EP_define.KAKAO_PARAM_SELLING_TIME]
            except (RuntimeError, TypeError, NameError, KeyError) as ex:
                pass

        #Pickup Time Parsing
        try:
            self.pickupTime       = self.dataActionParams[EP_define.KAKAO_PARAM_PICKUP_TIME]['origin'][:5]
            if not self.dataActionExtra is None:
                self.dataActionExtra[EP_define.KAKAO_PARAM_PICKUP_TIME] = self.pickupTime
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.pickupTime       = EP_define.NOT_APPLICABLE
            pass
        if not self.dataActionExtra is None:
            try:
                self.pickupTime      = self.dataActionExtra[EP_define.KAKAO_PARAM_PICKUP_TIME]
            except (RuntimeError, TypeError, NameError, KeyError) as ex:
                pass

        #Location Parsing
        try:
            self.location        = EP_define.NOT_APPLICABLE
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.location        = EP_define.NOT_APPLICABLE 
            pass
