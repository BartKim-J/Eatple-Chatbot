from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import slack 

SLACK_CLIENT_ID = '808658240627.862280783904'
SLACK_CLIENT_SECRET = 'cd6bb7935acaf9451c1bf326f21b80bd'

SLACK_VERIFICATION_TOKEN = 'qM7JgIwtYjTnMZ6KP9KbNo5o'
SLACK_BOT_USER_TOKEN = 'xoxb-808658240627-864289607191-jQUdG2eS12XZLNZ3Xz53gz8a'

SLACK_CHANNEL_EATPLE_LOG = 'CQZKF5W02'

SLACK_COMMAND_DAILY_STATUS = 'ds'
SLACK_COMMAND_TOTAL_STATUS = 'ts'

client = slack.WebClient(token=SLACK_BOT_USER_TOKEN)
