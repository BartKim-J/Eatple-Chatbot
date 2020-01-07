#!/bin/bash
cd /home/ubuntu/eatple-chatbot

sh /home/ubuntu/eatple-chatbot/migrate.sh

uwsgi --http :8001 --home /home/ubuntu/.pyenv/versions/deploy_eatple --chdir /home/ubuntu/eatple-chatbot -w config.wsgi.debug


