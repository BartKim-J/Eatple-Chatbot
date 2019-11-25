#!/bin/bash
cd /home/eatplus/eatple.chatbot

sudo rm -rf /home/eatplus/eatple.chatbot/eatple_app/migrations
sudo sh /home/eatplus/eatple.chatbot/migrate.sh
sudo python /home/eatplus/eatple.chatbot/manage.py runserver 0.0.0.0:8000
