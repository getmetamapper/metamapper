# -*- coding: utf-8 -*-
import random

from django.db.models import Q, F, Max
from django.db.models import DateTimeField, ExpressionWrapper
from django.db.models.functions import Now

from metamapper.celery import app
from utils import logging

from app.definitions.models import Datastore

from app.revisioner.models import Run
from app.revisioner.tasks.v1 import core


__all__ = ['create_runs', 'queue_runs']


@app.task(bind=True)
@logging.task_logger(__name__)
def create_runs(self, datastore_slug=None, *args, **kwargs):
    """Scheduled task to create a record for each new run. Runs every 30 minutes.
    """
    expression = ExpressionWrapper(Now() - F('interval'), output_field=DateTimeField())
    runs_cache = []
    datastores = (
        Datastore
        .objects
        .annotate(last_run_ts=Max('run_history__created_at'))
        .filter(is_enabled=True)
    )

    # If we are singling out a datastore, then we do not care about run history.
    if datastore_slug:
        datastores = datastores.filter(slug__iexact=datastore_slug)
    else:
        datastores = datastores.filter(Q(last_run_ts__lte=expression) | Q(last_run_ts__isnull=True))

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
