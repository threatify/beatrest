Celery Beat scheduler that uses API calls to manage schedules instead of a
persistent data store like relational db, redis, etc.

Running the scheduler with sample pyramid api:

celery beat -A pyramid_celery.celery_app -S beatrest.RestScheduler \
       --ini sample_rest_api/config.ini

Running a worker:

celery worker -A pyramid_celery.celery_app --loglevel DEBUG -Q tr \
       --ini  sample_rest_api/config.ini


Monitoring:

celery flower -A pyramid_celery.celery_app sample_rest_api/config.ini
