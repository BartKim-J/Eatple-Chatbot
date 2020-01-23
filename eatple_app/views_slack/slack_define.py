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

HOST_URL = 'https://www.eatple.com:8000'

#  TYPE
ORDER_TYPE_NORMAL = 'normal'
ORDER_TYPE_EVENT = 'event'
ORDER_TYPE_PROMOTION = 'promotion'
ORDER_TYPE_B2B = 'B2B'

SLACK_CLIENT_ID = '1.862280783904'
SLACK_CLIENT_SECRET = '2'

SLACK_VERIFICATION_TOKEN = '3'
SLACK_BOT_USER_TOKEN = ''

SLACK_CHANNEL_EATPLE_LOG = '1'

SLACK_COMMAND_DAILY_STATUS = 'ds'
SLACK_COMMAND_TOTAL_STATUS = 'ts'

client = slack.WebClient(token=SLACK_BOT_USER_TOKEN)
