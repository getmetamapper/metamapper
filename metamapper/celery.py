# -*- coding: utf-8 -*-
from __future__ import absolute_import

from celery import Celery
from celery.schedules import crontab
from os import environ, getenv

from django.apps import apps

# set the default Django settings module for the 'celery' program.
environ.setdefault('DJANGO_SETTINGS_MODULE', 'metamapper.settings')
environ.setdefault('METAMAPPER_CELERY_CONFIG_MODULE', 'metamapper.conf.celery')

app = Celery('metamapper')
app.config_from_envvar('METAMAPPER_CELERY_CONFIG_MODULE')
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

app.conf.beat_schedule = {
    'beat-scheduler-healthcheck': {
        'task': 'app.healthchecks.tasks.heartbeat',
        'schedule': crontab(),
    },
    'create-revisioner-runs': {
        'task': 'app.revisioner.tasks.scheduler.create_runs',
        'schedule': crontab(hour='*/1'),
    },
    'queue-revisioner-runs': {
        'task': 'app.revisioner.tasks.scheduler.queue_runs',
        'schedule': crontab(minute='*/20'),
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
