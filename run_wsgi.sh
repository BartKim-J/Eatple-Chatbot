sudo -u ubuntu /home/ubuntu/.pyenv/versions/deploy_eatple/bin/uwsgi --http :8000 -i /home/ubuntu/eatple-chatbot/.config_secret/uwsgi/deploy.ini

# uwsgi --http :8000 --home /home/ubuntu/.pyenv/versions/deploy_eatple --chdir /home/ubuntu/eatple-chatbot -w config.wsgi.debug


