from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models  import Store, Menu 

import json

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
    def __init__(self, _outputs=[]):
        super().__init__()
        self.outputs = _outputs

        self.UpdateTemplateForm()

        super().SetTemplateForm(self.template)

    def __new__(cls):
        #print('Kaka form new created.')
        return super().__new__(cls)

    def UpdateTemplateForm(self):
        self.template = {
            "outputs": self.outputs,
            "quickReplies": [ { "action" : "message", "label" : "🏠홈", "messageText" : "다시 메인으로 돌아가줘 " } ],
        }

        super().SetTemplateForm(self.template)

    def SimpleForm_Init(self):
        self.outputs = []
        self.UpdateTemplateForm()

    def SimpleText_Add(self, _text):
        _params = { 
            "text": _text,
        }

        self.outputs += {
            "simpleText": _params
        },

        self.UpdateTemplateForm()

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
    def __init__(self, _type='commerceCard', _items=[]):
        super().__init__()
        self.type     = _type
        self.items    = _items

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
            ]
        }
        
        super().SetTemplateForm(self.template)


    # Comerce Card 
    def ComerceCard_Init(self):
        self.type   = 'commerceCard'
        self.items  = []
        self.UpdateTemplateForm()

    def ComerceCard_AddCard(self, _description, _price, _discount, _currency, _thumbnails, _profile, _buttons):
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
        self.UpdateTemplateForm()

    def BasicCard_AddCard(self, _title, _description, _thumbnail, _buttons):
        self.items += {
            "title": _title,
            "description": _description,
            "thumbnail": _thumbnail,
            "buttons": _buttons
        },

        self.UpdateTemplateForm()

    def GetForm(self):
        return self.baseForm

