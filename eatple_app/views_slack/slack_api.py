# Define
from eatple_app.define import *

from eatple_app.model.menu import Menu, PickupTime

def eatple_b2b_status():
    menuList = Menu.objects.filter(
        store__type=STORE_TYPE_B2B,         
        status=OC_OPEN,
        store__status=OC_OPEN,
    )
    
    menuStatusBlock = []
    menuStatusBlock += {
        "type": "divider"
    },
    
    total_stock = 0
    
    for menu in menuList:
        if(menu.current_stock == 0):
            pass
        else:
            total_stock += menu.current_stock
            
            menuStatusBlock += {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            "*{name} - {menu}*\n"
                            "```\n"
                            "일일 재고량 : {max_stock}개, "
                            "픽업 대기중 : {current_stock}개"
                            "```"
                            " > <{host_url}/admin/eatple_app/store/{store_index}/change|점포 자세히 보기>\n"
                        ).format(
                                name=menu.store.name,
                                menu=menu.name,
                                current_stock=menu.current_stock,
                                max_stock=menu.max_stock,
                                host_url=HOST_URL,
                                store_index=menu.store.id,
                        )
                    },
                    #"accessory": {
                    #    "type": "image",
                    #    "image_url": '{}{}'.format(HOST_URL, menuList.first().image.url),
                    #    "alt_text": "menu"
                    #}
                },
        
    menuStatusBlock += {
        "type": "divider"
    },
    menuStatusBlock += {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "*총 픽업 대기중인 주문 : {total_stock}개*"
            ).format(
                total_stock=total_stock,
            )
        },
    },
    menuStatusBlock += {
        "type": "divider"
    },
    
    res = client.chat_postMessage(
        channel=SLACK_CHANNEL_EATPLE_LOG,
        blocks=menuStatusBlock
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

            if SLACK_COMMAND_B2B_STATUS in text.lower():
                return eatple_b2b_status()
                

        return Response(status=status.HTTP_200_OK)
