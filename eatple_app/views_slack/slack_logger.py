# Define
from eatple_app.define import *

# Models
from eatple_app.models import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import slack 

SLACK_CLIENT_ID = '808658240627.862280783904'
SLACK_CLIENT_SECRET = 'cd6bb7935acaf9451c1bf326f21b80bd'

SLACK_VERIFICATION_TOKEN = 'qM7JgIwtYjTnMZ6KP9KbNo5o'
SLACK_BOT_USER_TOKEN = 'xoxb-808658240627-864289607191-jQUdG2eS12XZLNZ3Xz53gz8a'

SLACK_CHANNEL_EATPLE_LOG = 'CQZKF5W02'

client = slack.WebClient(token=SLACK_BOT_USER_TOKEN)

def SlackLogSignUp(user):    
    res = client.chat_postMessage(
        channel=SLACK_CHANNEL_EATPLE_LOG,
        text="{name}님이 잇플에 들어옴, 흥폭발:face_with_hand_over_mouth:".format(name=user.nickname)
    )
    
    return res


def SlackLogPayOrder(order):
    res = client.chat_postMessage(
        channel=SLACK_CHANNEL_EATPLE_LOG,
        text="{name}님이 잇플패스를 발급함, 마니머겅:blue_heart:".format(
            name=order.ordersheet.user.nickname, 
            menu=order.menu.name
        )
    )
    
    return res
    
def SlackLogCancelOrder(order):
    res = client.chat_postMessage(
        channel=SLACK_CHANNEL_EATPLE_LOG,
        text="{name}님이 잇플을 취소함, 에라이:bart:".format(
            name=order.ordersheet.user.nickname, 
            menu=order.menu.name
        )
    )
    
    return res
