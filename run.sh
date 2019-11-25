#!/bin/bash
cd /home/eatplus/eatple.chatbot

sudo sh /home/eatplus/eatple.chatbot/migrate.sh
sudo python /home/eatplus/eatple.chatbot/manage.py runserver 0.0.0.0:8000
