# Define
from eatple_app.define import *

# Models
from eatple_app.models import *

from eatple_app.views_slack.slack_define import * 

def eatple_total_status():
    res = client.chat_postMessage(
        channel=SLACK_CHANNEL_EATPLE_LOG,
        text="전체 가입자수 : {userCount}명, 전체 주문수: {orderCount}개".format(
            userCount=User.objects.all().count(), 
            orderCount=Order.objects.all().filter(
                Q(status=ORDER_STATUS_PICKUP_WAIT) |
                Q(status=ORDER_STATUS_PICKUP_PREPARE) |
                Q(status=ORDER_STATUS_PICKUP_COMPLETED) |
                Q(status=ORDER_STATUS_ORDER_CONFIRM_WAIT) |
                Q(status=ORDER_STATUS_ORDER_CONFIRMED)
            ).count()
        )
    )

    return Response(status=status.HTTP_200_OK)


def eatple_daily_status():
    currentDate = dateNowByTimeZone()
    currentDateWithoutTime = currentDate.replace(
        hour=0, minute=0, second=0, microsecond=0)

    YESTERDAY = currentDateWithoutTime + datetime.timedelta(days=-1)  # Yesterday start
    TODAY = currentDateWithoutTime
    TOMORROW = currentDateWithoutTime + datetime.timedelta(days=1)  # Tommorrow start

    res = client.chat_postMessage(
        channel=SLACK_CHANNEL_EATPLE_LOG,
        text="일일 가입자수 : {userCount}명, 일일 주문수: {orderCount}개".format(
            userCount=User.objects.all().filter(
                Q(create_date__gte=TODAY) &
                Q(create_date__lte=TOMORROW)
            ).count(),
            orderCount=Order.objects.all().filter(
                Q(status=ORDER_STATUS_PICKUP_WAIT) |
                Q(status=ORDER_STATUS_PICKUP_PREPARE) |
                Q(status=ORDER_STATUS_ORDER_CONFIRM_WAIT) |
                Q(status=ORDER_STATUS_ORDER_CONFIRMED)
            ).filter(
                Q(order_date__gte=TODAY) &
                Q(order_date__lte=TOMORROW)
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

            if SLACK_COMMAND_DAILY_STATUS in text.lower():
                return eatple_daily_status()
                
            if SLACK_COMMAND_TOTAL_STATUS in text.lower():
                return eatple_total_status()

        return Response(status=status.HTTP_200_OK)
