#!/bin/bash
cd /home/ubuntu/eatple-chatbot
export DJANGO_SETTINGS_MODULE=config.settings.deploy

sh /home/ubuntu/eatple-chatbot/migrate.sh

python /home/ubuntu/eatple-chatbot/manage.py runserver 0.0.0.0:8001