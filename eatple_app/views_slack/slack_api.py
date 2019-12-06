# Define
from eatple_app.define import *

# Models
from eatple_app.models import *
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import slack 

SLACK_CLIENT_ID = '808658240627.862280783904'
SLACK_CLIENT_SECRET = 'cd6bb7935acaf9451c1bf326f21b80bd'

SLACK_VERIFICATION_TOKEN = 'qM7JgIwtYjTnMZ6KP9KbNo5o'
SLACK_BOT_USER_TOKEN = 'xoxb-808658240627-864289607191-jQUdG2eS12XZLNZ3Xz53gz8a'

client = slack.WebClient(token=SLACK_BOT_USER_TOKEN)


SLACK_COMMAND_STATUS = 'status'
SLACK_COMMAND_PROMOTION_STATUS ='p_status'

def eatple_status():
    res = client.chat_postMessage(
        channel=SLACK_CHANNEL_EATPLE_LOG,
        text="전체 가입자수 : {userCount}명, 주문수: {orderCount}개".format(
            userCount=User.objects.all().count(), 
            orderCount=Order.objects.all().filter(
                Q(status=ORDER_STATUS_PICKUP_WAIT) |
                Q(status=ORDER_STATUS_PICKUP_PREPARE) |
                Q(status=ORDER_STATUS_ORDER_CONFIRM_WAIT) |
                Q(status=ORDER_STATUS_ORDER_CONFIRMED)
            ).count()
        )
    )

    return Response(status=status.HTTP_200_OK)


class Events(APIView):
    def post(self, request, *args, **kwargs):
        slack_message = request.data

        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # verification challenge
        if slack_message.get('type') == 'url_verification':
            return Response(data=slack_message,
                            status=status.HTTP_200_OK)
        if 'event' in slack_message:
            event_message = slack_message.get('event')

            # ignore bot's own message
            if event_message.get('subtype') == 'bot_message':
                return Response(status=status.HTTP_200_OK)

            # process user's message
            user = event_message.get('user')
            text = event_message.get('text')
            channel = event_message.get('channel')

            if SLACK_COMMAND_STATUS in text.lower():
                return eatple_status()
                


        return Response(status=status.HTTP_200_OK)
