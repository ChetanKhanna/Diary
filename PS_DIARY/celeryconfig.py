from __future__ import absolute_import
CELERY_IMPORTS=("sm.tasks")
BROKER_URL = "amqp://guest:guest@localhost:5672//"
CELERY_RESULT_BACKEND = "localhost:5672//"
CELERY_ROUTES = {'sm.tasks.add_sub': {'queue': 'add_sub'},
        'sm.tasks.multiply':{'queue':'multiply'}
        }
CELERY_CREATE_MISSING_QUEUES = True
CELERY_MESSAGE_COMPRESSION = 'bzip2'
CELERYD_PREFETCH_MULTIPLIER = 1
CELERY_DEFAULT_QUEUE = 'sm_celery'