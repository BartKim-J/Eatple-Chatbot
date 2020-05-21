# Define
from eatple_app.define import *

import time


def getUserData(user):
    return UserData(
        email=user.email,
        phone=user.phone_number.as_national,
    )


def Pixel_userRegister(user):
    user_data = getUserData(user)

    event = Event(
        event_name='CompleteRegistration',
        event_time=int(time.time()),
        user_data=user_data,
    )

    events = [event]

    event_request = EventRequest(
        events=events,
        pixel_id=PIXEL_ID
    )

    event_response = event_request.execute()
    return event_response


def Pixel_viewStore(user):
    user_data = getUserData(user)

    event = Event(
        event_name='상점보기',
        event_time=int(time.time()),
        user_data=user_data,
    )

    events = [event]

    event_request = EventRequest(
        events=events,
        pixel_id=PIXEL_ID
    )

    event_response = event_request.execute()
    return event_response


def Pixel_viewMenu(user):
    user_data = getUserData(user)

    event = Event(
        event_name='메뉴 선택중',
        event_time=int(time.time()),
        user_data=user_data,
    )

    events = [event]

    event_request = EventRequest(
        events=events,
        pixel_id=PIXEL_ID
    )

    event_response = event_request.execute()
    return event_response


def Pixel_setPickupTime(user):
    user_data = getUserData(user)

    event = Event(
        event_name='픽업시간 설정',
        event_time=int(time.time()),
        user_data=user_data,
    )

    events = [event]

    event_request = EventRequest(
        events=events,
        pixel_id=PIXEL_ID
    )

    event_response = event_request.execute()
    return event_response


def Pixel_orderSheet(user):
    user_data = getUserData(user)

    event = Event(
        event_name='주문내역 확인',
        event_time=int(time.time()),
        user_data=user_data,
    )

    events = [event]

    event_request = EventRequest(
        events=events,
        pixel_id=PIXEL_ID
    )

    event_response = event_request.execute()
    return event_response


def Pixel_eatplePassCheck(user):
    user_data = getUserData(user)

    event = Event(
        event_name='잇플패스 확인',
        event_time=int(time.time()),
        user_data=user_data,
    )

    events = [event]

    event_request = EventRequest(
        events=events,
        pixel_id=PIXEL_ID
    )

    event_response = event_request.execute()
    return event_response


def Pixel_eatplePassUsed(user):
    user_data = getUserData(user)

    event = Event(
        event_name='잇플패스 사용',
        event_time=int(time.time()),
        user_data=user_data,
    )

    events = [event]

    event_request = EventRequest(
        events=events,
        pixel_id=PIXEL_ID
    )

    event_response = event_request.execute()
    return event_response


def Pixel_Purchase(user, order):
    user_data = getUserData(user)

    custom_data = CustomData(
        currency='KRW',
        value=float(order.totalPrice)
    )

    event = Event(
        event_name='결제 완료',
        event_time=int(time.time()),
        user_data=user_data,
        custom_data=custom_data,
    )

    events = [event]

    event_request = EventRequest(
        events=events,
        pixel_id=PIXEL_ID
    )

    event_response = event_request.execute()
    return event_response


def Pixel_PurchaseCancel(user, order):
    user_data = getUserData(user)

    custom_data = CustomData(
        currency='KRW',
        value=float(order.totalPrice)
    )

    event = Event(
        event_name='결제 취소',
        event_time=int(time.time()),
        user_data=user_data,
        custom_data=custom_data,
    )

    events = [event]

    event_request = EventRequest(
        events=events,
        pixel_id=PIXEL_ID
    )

    event_response = event_request.execute()
    return event_response
