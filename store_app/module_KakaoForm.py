#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import requests
import json
import datetime

#Models 
from .models_config import Config

from .models_user  import User
from .models_order import Order
from .models_store import Store, Menu, Category, SubCategory

class KakaoPayLoad:
    def __init__(self, request):
        self.json_str           = ((request.body).decode('utf-8'))
        self.received_json_data = json.loads(self.json_str)

        self.dataUserRequest    = self.received_json_data['userRequest']
        self.dataBot            = self.received_json_data['bot']
        
        self.dataAction         = self.received_json_data['action']
        self.dataActionExtra    = self.dataAction['clientExtra']
        self.dataActionParams   = self.dataAction['detailParams']

        # Get paramter
        try:
            self.storeID         = self.dataActionExtra[Config.KAKAO_EXTRA_STORE_ID]
            self.storeName       = self.dataActionExtra[Config.KAKAO_EXTRA_STORE_NAME]
            self.storeAddr       = self.dataActionExtra[Config.KAKAO_EXTRA_STORE_ADDR]

            self.menuID          = self.dataActionExtra[Config.KAKAO_EXTRA_MENU_ID]
            self.menuName        = self.dataActionExtra[Config.KAKAO_EXTRA_MENU_NAME]
            self.menuPrice       = self.dataActionExtra[Config.KAKAO_EXTRA_MENU_PRICE]
            self.menuDescription = self.dataActionExtra[Config.KAKAO_EXTRA_MENU_DESCRIPTION]

        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.storeID         = Config.NOT_APPLICABLE
            self.storeName       = Config.NOT_APPLICABLE
            self.storeAddr       = Config.NOT_APPLICABLE

            self.menuID          = Config.NOT_APPLICABLE
            self.menuName        = Config.NOT_APPLICABLE
            self.menuPrice       = Config.NOT_APPLICABLE
            self.menuDescription = Config.NOT_APPLICABLE
            pass
            
        try:
            self.menuCategory    = self.dataActionExtra[Config.KAKAO_EXTRA_MENU_CATEGORY]
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.menuCategory    = Config.NOT_APPLICABLE
            pass

        try:
            self.sellingTime     = self.dataActionExtra[Config.KAKAO_EXTRA_SELLING_TIME]
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.sellingTime     = Config.NOT_APPLICABLE
            pass

        try:
            self.pickupTime       = self.dataActionParams[Config.KAKAO_EXTRA_PICKUP_TIME][Config.KAKAO_EXTRA_PICKUP_TIME_VALUE][:5]
            self.dataActionExtra  = {**self.dataActionExtra, **{Config.KAKAO_EXTRA_PICKUP_TIME: self.pickupTime}}
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.pickupTime       = Config.NOT_APPLICABLE
            pass
        try:
            self.pickupTime      = self.dataActionExtra[Config.KAKAO_EXTRA_PICKUP_TIME][:5]
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            pass
        try:
            self.location        = Config.NOT_APPLICABLE
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.location        = Config.NOT_APPLICABLE 
            pass


class KakaoBaseForm():
    def __init__(self, _version="2.0", _template={"outputs": []}, _context={"values": []}, _data={"Status": 'OK'}):
        self.version  = _version
        self.template = _template
        self.context  = _context
        self.data     = _data

        self.UpdateForm()

    def __new__(cls):
        #print('Kaka form new created.')
        return super().__new__(cls)

    def UpdateForm(self):
        self.baseForm = {
            "version":  self.version,
            "template": self.template,
            "context":  self.context,
            "data":     self.data,
        }

    def GetForm(self):
        return self.baseForm

    def SetTemplateForm(self, _template):
        self.template = _template
        self.UpdateForm()

    def SetContextForm(self, _context):
        self.context = _context
        self.UpdateForm()

    def SetDataForm(self, _data):
        self.data = _data
        self.UpdateForm()



class Kakao_SimpleForm(KakaoBaseForm):
    def __init__(self, _outputs=[], _quickReplies=[]):
        super().__init__()
        self.outputs = _outputs
        self.quickReplies = _quickReplies
        self.UpdateTemplateForm()

        super().SetTemplateForm(self.template)

    def __new__(cls):
        #print('Kaka form new created.')
        return super().__new__(cls)

    def UpdateTemplateForm(self):
        self.template = {
            "outputs": self.outputs,
            "quickReplies": self.quickReplies,
        }

        super().SetTemplateForm(self.template)

    # Quick Replies
    def QuickReplies_Init(self):
        self.quickReplies = []
        self.UpdateTemplateForm()

    def QuickReplies_Add(self, _action, _label, _messageText, _blockid, _extra):
        self.quickReplies += { "action" : _action, "label" : _label, "messageText" : _messageText, "blockid": _blockid, "extra": _extra },
        
    # SimpleForm Common
    def SimpleForm_Init(self):
        self.outputs = []
        self.quickReplies = []
        self.UpdateTemplateForm()

    # SimpleForm Text
    def SimpleText_Add(self, _text):
        _params = { 
            "text": _text,
        }

        self.outputs += {
            "simpleText": _params
        },

        self.UpdateTemplateForm()

    # SimpleForm Image
    def SimpleImage_Add(self, _imgUrl, _altText):
        _params = { 
            "imageUrl": _imgUrl,
            "altText": _altText,
        }

        self.outputs += {
            "simpleImage": _params
        },

        self.UpdateTemplateForm()

    def GetForm(self):
        return self.baseForm



class Kakao_CarouselForm(KakaoBaseForm):
    def __init__(self, _type='commerceCard', _items=[], _quickReplies=[]):
        super().__init__()
        self.type     = _type
        self.items    = _items
        self.quickReplies = _quickReplies


        self.UpdateTemplateForm()

        super().SetTemplateForm(self.template)

    def __new__(cls):
        #print('Kaka carousel form created.')
        return super().__new__(cls)

    def UpdateTemplateForm(self):
        self.template = {
            "outputs": [
                {
                    "carousel": {
                        "type": self.type,
                        "items": self.items
                    }
                }
            ],
            "quickReplies": self.quickReplies,
        }
        
        super().SetTemplateForm(self.template)

    # Quick Replies
    def QuickReplies_Init(self):
        self.quickReplies = []
        self.UpdateTemplateForm()

    def QuickReplies_Add(self, _action, _label, _messageText, _blockid, _extra):
        self.quickReplies += { "action" : _action, "label" : _label, "messageText" : _messageText, "blockid": _blockid, "extra": _extra },

    # Comerce Card 
    def ComerceCard_Init(self):
        self.type   = 'commerceCard'
        self.items  = []
        self.quickReplies = []
        self.UpdateTemplateForm()

    def ComerceCard_Add(self, _description, _price, _discount, _currency, _thumbnails, _profile, _buttons):
        self.items += {
            "description": _description,
            "price": _price,
            #"discount": _discount,
            "currency": _currency,
            "thumbnails": _thumbnails,
            "profile": _profile,
            "buttons": _buttons
        },

        self.UpdateTemplateForm()

    # Basic Card 
    def BasicCard_Init(self):
        self.type   = 'basicCard'
        self.items  = []
        self.quickReplies = []
        self.UpdateTemplateForm()

    def BasicCard_Add(self, _title, _description, _thumbnail, _buttons):
        self.items += {
            "title": _title,
            "description": _description,
            "thumbnail": _thumbnail,
            "buttons": _buttons
        },

        self.UpdateTemplateForm()

    def GetForm(self):
        return self.baseForm
