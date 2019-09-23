#!/bin/bash
python manage.py makemigrations eatplus_app
python manage.py migrate
