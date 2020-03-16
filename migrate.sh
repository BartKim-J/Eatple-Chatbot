#!/bin/bash
python manage.py makemigrations eatple_app sales_app
python manage.py migrate
