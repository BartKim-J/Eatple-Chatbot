#!/bin/bash
cd /home/ubuntu/eatple-chatbot
export DJANGO_SETTINGS_MODULE=config.settings.deploy

echo Status Update Start

/home/ubuntu/.pyenv/versions/deploy_eatple/bin/python /home/ubuntu/eatple-chatbot/manage.py order --update-all
/home/ubuntu/.pyenv/versions/deploy_eatple/bin/python /home/ubuntu/eatple-chatbot/manage.py menu --update-all

echo Status Update Done!!