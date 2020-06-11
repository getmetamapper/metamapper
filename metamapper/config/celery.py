#
# Celery (https://docs.celeryproject.org/en/stable/userguide/configuration.html)
#
# Metamapper supports a pretty basic Celery setup with an optional
# results backend. We recommend using either Redis or RabbitMQ as your broker.
#
# You can override these default settings by creating your own file and referencing the
# module via the METAMAPPER_CELERY_CONFIG_MODULE environment variable.
#

import os
import sys


broker_url = os.getenv('METAMAPPER_CELERY_BROKER_URL')

accept_content = ['application/json']

result_serializer = 'json'

task_serializer = 'json'

task_always_eager = len(sys.argv) > 1 and sys.argv[1] == 'test'

task_eager_propagates = task_always_eager

result_backend = os.getenv('METAMAPPER_CELERY_RESULT_BACKEND')
