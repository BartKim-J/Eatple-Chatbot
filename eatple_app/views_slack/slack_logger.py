from eatple_app.views_slack.slack_define import * 

def SlackLogFollow(nickname):
    res = client.chat_postMessage(
        channel=SLACK_CHANNEL_EATPLE_LOG,
        text="{name}님이 잇플 채널을 팔로우햇쥐:mouse:".format(
            name=nickname
        )
    )
    
    return res

def SlackLogUnfollow(nickname):
    res = client.chat_postMessage(
        channel=SLACK_CHANNEL_EATPLE_LOG,
        text="{name}님이 잇플 채널을 언...팔로우햇..쥐:mouse:".format(
            name=nickname
        )
    )
    
    return res

def SlackLogSignUp(user):    
    res = client.chat_postMessage(
        channel=SLACK_CHANNEL_EATPLE_LOG,
        text="{name}님이 잇플에 들어옴, 흥폭발:face_with_hand_over_mouth:".format(
            name=user.nickname
        )
    )
    
    return res

def SlackLogPaydOrder(order):
    if(settings.SETTING_ID == 'DEPLOY'):
        SERVER_PORT = 8000
        DEV_LOG=''
    else:
        SERVER_PORT = 8001
        DEV_LOG='개발 서버에서 '

    HOST_URL='https://www.eatple.com:{}'.format(SERVER_PORT)
        
    if(order.type == ORDER_TYPE_NORMAL):
        res = client.chat_postMessage(
            channel=SLACK_CHANNEL_EATPLE_LOG,
            blocks=[
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*{dev}{name}님이 B2B 일반 잇플패스를 발급함* :heart:\n```\n{menu} - 픽업시간 {pickup_time}\n > <https://www.eatple.com:{port}/admin/eatple_app/order/{order_id}/change|주문 자세히 보기>\n```".format(
                            dev=DEV_LOG,
                            name=order.ordersheet.user.nickname,
                            menu=order.menu,
                            pickup_time=order.pickup_time.strftime(
                                '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
                            port=SERVER_PORT,
                            order_id=order.id,
                        )
                    },
                    #"accessory": {
                    #    "type": "image",
                    #    "image_url": '{}{}'.format(HOST_URL, order.menu.imgURL()),
                    #    "alt_text": "menu"
                    #}
                },
                {
                    "type": "divider"
                },
            ]
        )
        return res
    
    elif(order.type == ORDER_TYPE_B2B):
        res = client.chat_postMessage(
            channel=SLACK_CHANNEL_EATPLE_LOG,
            blocks= [
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*{dev}{name}님이 B2B 잇플패스를 발급함* :briefcase:\n```\n{menu} : 픽업시간 {pickup_time}\n > <https://www.eatple.com:{port}/admin/eatple_app/order/{order_id}/change|주문 자세히 보기>\n```".format(
                            dev=DEV_LOG,
                            name=order.ordersheet.user.nickname,
                            menu=order.menu,
                            pickup_time=order.pickup_time.strftime(
                                '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
                            port=SERVER_PORT,
                            order_id=order.id,
                        )
                    },
                    #"accessory": {
                    #    "type": "image",
                    #    "image_url": '{}{}'.format(HOST_URL, order.menu.imgURL()),
                    #    "alt_text": "menu"
                    #}
                },
                {
                    "type": "divider"
                },
            ]
        )
        return res 
    
    elif(order.type == ORDER_TYPE_PROMOTION):
        res = client.chat_postMessage(
            channel=SLACK_CHANNEL_EATPLE_LOG,
            blocks=[
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*{dev}{name}님이 프로모션 잇플패스를 발급함* :blue_heart:\n```\n{menu} : 픽업시간 {pickup_time}\n > <https://www.eatple.com:{port}/admin/eatple_app/order/{order_id}/change|주문 자세히 보기>\n```".format(
                            dev=DEV_LOG,
                            name=order.ordersheet.user.nickname,
                            menu=order.menu,
                            pickup_time=order.pickup_time.strftime(
                                '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
                            port=SERVER_PORT,
                            order_id=order.id,
                        )
                    },
                    #"accessory": {
                    #    "type": "image",
                    #    "image_url": '{}{}'.format(HOST_URL, order.menu.imgURL()),
                    #    "alt_text": "menu"
                    #}
                }.
                {
                    "type": "divider"
                },
            ]
        )
        return res
    
    else:
        res = client.chat_postMessage(
            channel=SLACK_CHANNEL_EATPLE_LOG,
            text="{name}님이 이상한 주문을 함"
        )
        return res

def SlackLogCancelOrder(order):
    if(settings.SETTING_ID == 'DEPLOY'):
        SERVER_PORT = 8000
        DEV_LOG=''
    else:
        SERVER_PORT = 8001
        DEV_LOG='개발 서버에서 '
        
    HOST_URL='https://www.eatple.com:{}'.format(SERVER_PORT)
        
    res = client.chat_postMessage(
        channel=SLACK_CHANNEL_EATPLE_LOG,
        blocks=[
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*{dev}{name}님이 잇플패스를 취소함* :thinking_face:\n```\n{menu} - 픽업시간 {pickup_time}\n > <https://www.eatple.com:{port}/admin/eatple_app/order/{order_id}/change|주문 자세히 보기>\n```".format(
                        dev=DEV_LOG,
                        name=order.ordersheet.user.nickname,
                        menu=order.menu,
                        pickup_time=order.pickup_time.strftime(
                            '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
                        port=SERVER_PORT,
                        order_id=order.id,
                    )
                },
                #"accessory": {
                #    "type": "image",
                #    "image_url": '{}{}'.format(HOST_URL, order.menu.imgURL()),
                #    "alt_text": "menu"
                #}
            },
            {
                "type": "divider"
            },
        ]
    )
    return res
