#!/bin/bash
cd /home/eatplus/eatplus.chatbot
sudo sh /home/eatplus/eatplus.chatbot/migrate.sh
sudo python /home/eatplus/eatplus.chatbot/manage.py runserver 0.0.0.0:8000
