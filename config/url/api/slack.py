from django.conf.urls import url

from eatple_app import api

SLACK_API_URLS = [
    url('slack/api/events', api.Events.as_view()),
]
