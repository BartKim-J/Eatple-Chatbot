#!/bin/bash
python manage.py makemigrations eatple_app 
python manage.py migrate --fake
