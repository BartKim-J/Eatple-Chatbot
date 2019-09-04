#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import requests
import json

#Models
from .models_config import Config

#View
from .views_system import EatplusSkillLog, errorView

def getLatLng(addr):
    try:
        url = 'https://dapi.kakao.com/v2/local/search/address.json?query='+addr
        headers = {"Authorization": "KakaoAK d62991888c78ec58d809bdc591eb62f6"}
        result = json.loads(str(requests.get(url,headers=headers).text))

        match_first = result['documents'][0]['road_address']

    except (RuntimeError, TypeError, NameError, KeyError, IndexError) as ex:
        return errorView("Get Address Error\n- {} ".format(ex))

    return "{},{}".format(float(match_first['y']),float(match_first['x']))