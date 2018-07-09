#!/usr/bin/env bash
#if [[ -d "./assets/bundles" ]]; then
    #rm ./assets/bundles/*
#fi
#npm install
#npm run build

# serve backend processes
cd backend
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput
/usr/local/bin/uwsgi --ini /usr/src/app/deployment/uwsgi/uwsgi.ini
