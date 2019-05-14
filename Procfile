web: gunicorn accurate_replica.wsgi:application
worker: celery worker --beat --app accurate_replica --loglevel info
