#!/bin/bash
cd /home/ubuntu/eatple-chatbot
export DJANGO_SETTINGS_MODULE=config.settings.deploy

echo Order Status Update Start

/home/ubuntu/.pyenv/versions/deploy_eatple/bin/python /home/ubuntu/eatple-chatbot/manage.py order --update-all

echo Order Status Update Done!!