#!/bin/bash
cd /home/ubuntu/eatple-chatbot

sh /home/ubuntu/eatple-chatbot/migrate.sh

#python /home/ubuntu/eatple-chatbot/manage.py runserver 0.0.0.0:8000
uwsgi --http :8000 --home /home/ubuntu/.pyenv/versions/deploy_eatple --chdir /home/ubuntu/eatple-chatbot -w config.wsgi.deploy