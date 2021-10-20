# -*- coding: utf-8 -*-
from app.healthchecks.models import Heartbeat
from utils import logging

from metamapper.celery import app


@app.task(bind=True)
@logging.task_logger(__name__)
def heartbeat(self):
    """Update the heartbeat record.
    """
    self.log.info('Heart is beating.')
    Heartbeat.objects.beat()


@app.task()
def add(x, y):
    return x + y
