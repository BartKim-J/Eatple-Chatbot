#!/bin/bash
cd /home/ubuntu/eatple-chatbot
export DJANGO_SETTINGS_MODULE=config.settings.deploy

echo Status Update Start

echo Order List Updateing...
/home/ubuntu/.pyenv/versions/deploy_eatple/bin/python /home/ubuntu/eatple-chatbot/manage.py order
echo Order List Updated..!

sleep 5s

echo Menu List Updateing...
/home/ubuntu/.pyenv/versions/deploy_eatple/bin/python /home/ubuntu/eatple-chatbot/manage.py menu
echo Menu List Updated..!

sleep 5s

echo Store List Updateing...
/home/ubuntu/.pyenv/versions/deploy_eatple/bin/python /home/ubuntu/eatple-chatbot/manage.py store
echo Store List Updated..!

echo Status Update Done!!
