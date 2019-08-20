#!/bin/bash
python manage.py makemigrations store_app
python manage.py migrate
