# -*- coding: utf-8 -*-
import random

from django.db.models import Q, F, Max
from django.db.models import DateTimeField, ExpressionWrapper
from django.db.models.functions import Now

from metamapper.celery import app
from utils import logging, shortcuts

from app.checks.models import Check, CheckExecution
from app.checks.tasks import core


__all__ = ['create_executions']


@app.task(bind=True)
@logging.task_logger(__name__)
def create_executions(self, countdown_in_minutes=0):
    """Find the checks that need to be scheduled. Runs every 10 minutes.
    """
    expression = ExpressionWrapper(Now() - F('interval'), output_field=DateTimeField())

    checks = (
        Check
        .objects
        .annotate(last_run_ts=Max('executions__created_at'))
        .filter(Q(last_run_ts__lte=expression) | Q(last_run_ts__isnull=True))
        .filter(is_enabled=True)
    )

    if not len(checks):
        return

    self.log.info(
        'Found {0} checks(s)'.format(len(checks))
    )

    executions_cache = []
    executions_epoch = shortcuts.epoch_now()

    for check in checks.distinct():
        executions_cache.append(
            CheckExecution(
                job_id=check.id,
                workspace_id=check.workspace_id,
                query_id=check.query_id,
                epoch=executions_epoch))

    executions = CheckExecution.objects.bulk_create(executions_cache, ignore_conflicts=True)

    self.log.info(
        'Created {0} check execution(s)'.format(len(executions))
    )

    for execution in executions:
        async_kwargs = {
            'args': [
                execution.job_id,
                execution.epoch,
            ],
            'countdown': random.randint(0, (60 * countdown_in_minutes)),
        }
        core.execute_check.apply_async(**async_kwargs)
