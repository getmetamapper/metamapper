# -*- coding: utf-8 -*-
import random

from datetime import timedelta
from django.db.models import F, Max
from django.utils import timezone

from metamapper.celery import app
from utils import logging

from app.definitions.models import Datastore

from app.revisioner.models import Run
from app.revisioner.tasks.v1 import core


__all__ = ['create_runs', 'queue_runs']


@app.task(bind=True)
@logging.task_logger(__name__)
def create_runs(self, datastore_slug=None, hours=1, *args, **kwargs):
    """Scheduled task to create a record for each new run. Runs every 30 minutes.
    """
    date_from = timezone.now() - timedelta(hours=hours)

    runs_cache = []
    datastores = (
        Datastore.objects.annotate(last_run_ts=Max('run_history__created_at'))
                         .filter(run_history__created_at=F('last_run_ts'))
                         .filter(last_run_ts__lte=date_from)
                         .filter(is_enabled=True)
    )

    if datastore_slug:
        datastores = datastores.filter(slug__iexact=datastore_slug)

    self.log.info(
        'Found {0} datastore(s)'.format(len(datastores))
    )

    processed_datastores = []

    for datastore in datastores.distinct():
        if datastore.pk in processed_datastores:
            continue
        runs_cache.append(
            Run(datastore=datastore, workspace_id=datastore.workspace_id)
        )
        self.log.info(
            'Preparing {0} for Revisioner run'.format(datastore)
        )
        processed_datastores.append(datastore.pk)

    runs = Run.objects.bulk_create(runs_cache, ignore_conflicts=True)

    self.log.info(
        'Created {0} run(s)'.format(len(runs))
    )

    return runs


@app.task(bind=True)
@logging.task_logger(__name__)
def queue_runs(self, datastore_slug=None, countdown_in_minutes=15, *args, **kwargs):
    """Scheduled task to queue an unprocessed run. Runs every 10 minutes.
    """
    runs = Run.objects.filter(started_at=None, finished_at=None)

    if datastore_slug:
        runs = runs.filter(datastore__slug__iexact=datastore_slug)

    self.log.info(f'Found {len(runs)} run(s)')

    for run in runs:
        self.log.info(
            f'(run: {run.id}) Kicking off the run'
        )
        # Revisioner run starts within 15 minutes of this task call. We introduce randomness
        # so that we don't have a thundering herd...
        core.start_run.apply_async(args=[run.id], countdown=random.randint(0, (60 * countdown_in_minutes)))
