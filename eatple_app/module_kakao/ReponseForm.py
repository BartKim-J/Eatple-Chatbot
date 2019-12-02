# Define
from eatple_app.define import *

# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

class KakaoForm():
    def __init__(self):
        self.version = '2.0'
        self.template = {'outputs': [], 'quickReplies': []}
        self.context = {'values': []}
        self.data = {'Status': 'OK'}
        
        self.items = []
        
    def GetForm(self):
        retForm = {
            'version':  self.version,
            'template': self.template,
            'context':  self.context,
            'data':     self.data,
        }

        return retForm

    def QuickReplies_Add(self, _action, _label, _messageText, _blockId, _extra):
        self.template['quickReplies'] += {'action': _action, 'label': _label,
                                     'messageText': _messageText, 'blockId': _blockId, 'extra': _extra},
        
    def QuickReplies_AddWithMap(self, quickRepliesMap):
        for entryPoint in quickRepliesMap:
            self.QuickReplies_Add(entryPoint['action'],entryPoint['label'], entryPoint['messageText'], entryPoint['blockId'],entryPoint['extra'])

    def SimpleText_Add(self, _text):
        self.template['outputs'] += {
            'simpleText': { 
                'text': _text,
            }
        },

    def SimpleImage_Add(self, _imgUrl, _altText):
        self.template['outputs'] += {
            'simpleImage': { 
                'imageUrl': _imgUrl,
                'altText': _altText,
            }
        },

    def ComerceCard_Add(self):
        self.template['outputs'] += {
            'carousel': {
                'type': 'commerceCard',
                'items': self.items
            }
        },
        
        self.items = []
        
    def ComerceCard_Push(self, _description, _price, _discount,  _thumbnails, _profile, _buttons):
        self.items += {
            'description': _description,
            'price': _price,
            'discount': _discount,
            'discountPrice': None,
            'currency': 'won',
            'thumbnails': _thumbnails,
            'profile': _profile,
            'buttons': _buttons
        },
        
    def BasicCard_Add(self):
        self.template['outputs'] += {
            'carousel': {
                'type': 'basicCard',
                'items': self.items
            }
        },
           
        self.items = []
        
    def BasicCard_Push(self, _title, _description, _thumbnail, _buttons):
        self.items += {
            'title': _title,
            'description': _description,
            'thumbnail': _thumbnail,
            'buttons': _buttons
        },

    def ListCard_Add(self, _header):
        self.template['outputs'] += {
            'listCard': {
                'header': _header,
                'items': self.items
            }
        },

    def ListCard_Push(self, _title, _description, _imageUrl, _link):
        self.items += {
            'title': _title,
            'description': _description,
            'imageUrl': _imageUrl,
            'link': {
                "web": _link
            }
        },
