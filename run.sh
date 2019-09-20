#!/bin/bash
cd /home/eatplus/eatplus.chatbot/eatplus_chatbot/
sudo sh /home/eatplus/eatplus.chatbot/eatplus_chatbot/migrate.sh
sudo python /home/eatplus/eatplus.chatbot/eatplus_chatbot/manage.py runserver 0.0.0.0:8000
