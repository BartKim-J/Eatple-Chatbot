# Define
from eatple_app.define import *

# Models
from eatple_app.models import *

from eatple_app.views_slack.slack_define import * 

def SlackLogSignUp(user):    
    res = client.chat_postMessage(
        channel=SLACK_CHANNEL_EATPLE_LOG,
        text="{name}님이 잇플에 들어옴, 흥폭발:face_with_hand_over_mouth:".format(
            name=user.nickname
        )
    )
    
    return res


def SlackLogPayPromotionOrder(order):
    res = client.chat_postMessage(
        channel=SLACK_CHANNEL_EATPLE_LOG,
        text="{name}님이 프로모션 잇플패스를 발급함, 마니머겅:blue_heart:".format(
            name=order.ordersheet.user.nickname, 
        )
    )
    
    return res

def SlackLogPaydOrder(order):
    res = client.chat_postMessage(
        channel=SLACK_CHANNEL_EATPLE_LOG,
        text="{name}님이 무려 일반 잇플패스를 발급함, 마니머겅:heart:".format(
            name=order.ordersheet.user.nickname, 
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
