#!/bin/bash
export DJANGO_SETTINGS_MODULE=config.settings.debug

sh ./migrate.sh

python ./manage.py runserver 0.0.0.0:8001 