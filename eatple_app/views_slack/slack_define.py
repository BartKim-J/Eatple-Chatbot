# Models
from eatple_app.models import *

# Define
from eatple_app.define import *
from django.db.models import Q
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import slack 

#  TYPE
ORDER_TYPE_NORMAL = 'normal'
ORDER_TYPE_EVENT = 'event'
ORDER_TYPE_PROMOTION = 'promotion'
ORDER_TYPE_B2B = 'B2B'

SLACK_CLIENT_ID = '808658240627.862280783904'
SLACK_CLIENT_SECRET = 'cd6bb7935acaf9451c1bf326f21b80bd'

SLACK_VERIFICATION_TOKEN = 'qM7JgIwtYjTnMZ6KP9KbNo5o'
SLACK_BOT_USER_TOKEN = 'xoxb-808658240627-864289607191-kT7H9kwCZeK5LEo8YsnrLfFW'

SLACK_CHANNEL_EATPLE_LOG = 'CQZKF5W02'

SLACK_COMMAND_DAILY_STATUS = 'ds'
SLACK_COMMAND_TOTAL_STATUS = 'ts'

client = slack.WebClient(token=SLACK_BOT_USER_TOKEN)
