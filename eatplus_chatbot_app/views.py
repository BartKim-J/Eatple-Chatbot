from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import json

def responseTest(request):
  json_str           = ((request.body).decode('utf-8'))
  received_json_data = json.loads(json_str)

  dataIntent        = received_json_data['intent']
  dataUserRequest   = received_json_data['userRequest']
  dataBot           = received_json_data['bot'] 
  dataAction        = received_json_data['action'] 


  print(dataIntent)
  print(dataUserRequest)
  print(dataBot)
  print(dataAction)

  return JsonResponse({
    "version": "2.0",
    "template": {
      "outputs": [{
        "carousel": {
          "type": "commerceCard",
          "header": {
            "title": "커머스 카드\n케로셀 헤드 예제",
            "thumbnail": {
              "imageUrl": "http://k.kakaocdn.net/dn/83BvP/bl20duRC1Q1/lj3JUcmrzC53YIjNDkqbWK/i_6piz1p.jpg"
            }
          },
          "items": [
            {
              "description": "따끈따끈한 보물 상자 팝니다",
              "price": 10000,
              "discount": 1000,
              "currency": "won",
              "thumbnails": [
                {
                  "imageUrl": "http://k.kakaocdn.net/dn/83BvP/bl20duRC1Q1/lj3JUcmrzC53YIjNDkqbWK/i_6piz1p.jpg",
                  "link": {
                    "web": "https://store.kakaofriends.com/kr/products/1542"
                  }
                }
              ],
              "profile": {
                "imageUrl": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT4BJ9LU4Ikr_EvZLmijfcjzQKMRCJ2bO3A8SVKNuQ78zu2KOqM",
                "nickname": "보물상자 팝니다"
              },
              "buttons": [
                {
                  "label": "구매하기",
                  "action": "webLink",
                  "webLinkUrl": "https://store.kakaofriends.com/kr/products/1542"
                },
                {
                  "label": "전화하기",
                  "action": "phone",
                  "phoneNumber": "354-86-00070"
                },
                {
                  "label": "공유하기",
                  "action": "share"
                }
              ]
            },
            {
              "description": "따끈따끈한 보물 상자 팝니다",
              "price": 10000,
              "discount": 1000,
              "currency": "won",
              "thumbnails": [
                {
                  "imageUrl": "http://k.kakaocdn.net/dn/83BvP/bl20duRC1Q1/lj3JUcmrzC53YIjNDkqbWK/i_6piz1p.jpg",
                  "link": {
                    "web": "https://store.kakaofriends.com/kr/products/1542"
                  }
                }
              ],
              "profile": {
                "imageUrl": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT4BJ9LU4Ikr_EvZLmijfcjzQKMRCJ2bO3A8SVKNuQ78zu2KOqM",
                "nickname": "보물상자 팝니다"
              },
              "buttons": [
                {
                  "label": "구매하기",
                  "action": "webLink",
                  "webLinkUrl": "https://store.kakaofriends.com/kr/products/1542"
                },
                {
                  "label": "전화하기",
                  "action": "phone",
                  "phoneNumber": "354-86-00070"
                },
                {
                  "label": "공유하기",
                  "action": "share"
                }
              ]
            }
          ]
        }
      }]
    },
    "context": {
      "values": [
        {
          "name": "abc",
          "lifeSpan": 10,
          "params": {
            "key1": "val1",
            "key2": "val2"
          }
        },
        {
          "name": "def",
          "lifeSpan": 5,
          "params": {
            "key3": "1",
            "key4": "true",
            "key5": "{\"jsonKey\": \"jsonVal\"}"
          }
        },
        {
          "name": "ghi",
          "lifeSpan": 0
        }
      ]
    },
    "data": {
      "msg": "Hello Wolrd!",
    }
  })
 
def answer(request):
 
    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)
    datacontent = received_json_data['content']
 
    if datacontent == '버튼1':
        button1 = "버튼1을 누르셨습니다."
 
        return JsonResponse({
                'message': {
                    'text': button1
                },
                'keyboard': {
                    'type':'buttons',
                    'buttons':['버튼1','버튼2']
                }
 
            })
 
    elif datacontent == '버튼2':
        button2 = "버튼2을 누르셨습니다."
 
        return JsonResponse({
                'message': {
                    'text': button2
                },
                'keyboard': {
                    'type':'buttons',
                    'buttons':['버튼1','버튼2']
                }
 
            })
