from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import slack 

SLACK_CLIENT_ID = '808658240627.862280783904'
SLACK_CLIENT_SECRET = 'cd6bb7935acaf9451c1bf326f21b80bd'

SLACK_VERIFICATION_TOKEN = 'qM7JgIwtYjTnMZ6KP9KbNo5o'
SLACK_BOT_USER_TOKEN = 'xoxb-808658240627-864289607191-jQUdG2eS12XZLNZ3Xz53gz8a'

client = slack.WebClient(token=SLACK_BOT_USER_TOKEN)

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

            bot_text = 'Hi <@{}> :wave:'.format(user)
            if 'hi' in text.lower():
                client.chat_postEphemeral(
                    channel=channel, text="Hello", user=user)
                
                return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_200_OK)
