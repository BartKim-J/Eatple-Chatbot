from facebook_business.adobjects.serverside.event import Event
from facebook_business.adobjects.serverside.event_request import EventRequest
from facebook_business.adobjects.serverside.user_data import UserData
from facebook_business.adobjects.serverside.custom_data import CustomData
from facebook_business.api import FacebookAdsApi

ACCESS_TOKEN = 'EAAChRjPidsUBAB0ZCxzjS6ctZCxel7b2EmeZAByWU8i0Wwhnjs5a2IuQKZAhhkxXExpmUUgfPqhLhatDR4cWvgAP8UL9b1N0HNjZB5M2bDE2EZA7PerohwOD8fzvYrZAoTtrmsqf40YRe1iGiqudDwjN52eqSpmjZASZCdMwJj7xs5m9mWs5nhzDJ'
PIXEL_ID = '184112599470114'

FacebookAdsApi.init(access_token=ACCESS_TOKEN)