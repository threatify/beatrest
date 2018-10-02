from datetime import datetime
from pyramid_celery import celery_app


@celery_app.task(name='beatrest.debug.debug_print', queue='tr')
def debug_print(msg):
    print(msg)
    return msg


@celery_app.task(name='beatrest.debug.file_debug', queue='tr')
def file_debug(filename, msg, include_timestamp=True):
    if include_timestamp:
        timestamp = datetime.now().isoformat()
        open(filename, 'a').write(timestamp + ' ' + msg + '\n')
    else:
        open(filename, 'a').write(msg + '\n')
