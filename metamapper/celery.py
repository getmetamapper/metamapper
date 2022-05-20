# -*- coding: utf-8 -*-
from __future__ import absolute_import

from celery import Celery
from celery.schedules import crontab
from os import environ

from django.apps import apps
from kombu import Exchange, Queue

# set the default Django settings module for the 'celery' program.
environ.setdefault('DJANGO_SETTINGS_MODULE', 'metamapper.settings')
environ.setdefault('METAMAPPER_CELERY_CONFIG_MODULE', 'metamapper.conf.celery')

app = Celery('metamapper')
app.config_from_envvar('METAMAPPER_CELERY_CONFIG_MODULE')
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()] + ['metamapper'])

app.conf.task_default_queue = 'default'

app.conf.task_queues = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('checks', Exchange('checks'), routing_key='checks'),
    Queue('revisioner', Exchange('revisioner'), routing_key='revisioner'),
)

app.conf.beat_schedule = {
    'beat-scheduler-healthcheck': {
        'task': 'app.healthchecks.tasks.heartbeat',
        'schedule': crontab(),
    },
    'create-revisioner-runs': {
        'task': 'app.revisioner.tasks.v1.scheduler.create_runs',
        'schedule': crontab(minute='0', hour='*/1'),
    },
    'queue-revisioner-runs': {
        'task': 'app.revisioner.tasks.v1.scheduler.queue_runs',
        'schedule': crontab(minute='15,45'),
    },
    'detect-revisioner-run-timeouts': {
        'task': 'app.revisioner.tasks.v1.scheduler.detect_run_timeouts',
        'schedule': crontab(minute='0', hour='*/1'),
    },
    'create-check-executions': {
        'task': 'app.checks.tasks.scheduler.create_executions',
        'schedule': crontab(minute='*/1'),
    },
    'queue-domain-verification': {
        'task': 'app.sso.tasks.queue_domain_verifications',
        'schedule': crontab(minute='*/20'),
    },
    'deleted-domain-failures': {
        'task': 'app.sso.tasks.delete_failed_domains',
        'schedule': crontab(minute=0, hour='*/4'),
    },
}

app.conf.task_routes = {
    'app.checks.tasks.*': {'queue': 'checks'},
    'app.revisioner.tasks.*': {'queue': 'revisioner'},
}
