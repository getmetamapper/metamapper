# -*- coding: utf-8 -*-
from datetime import timedelta
from django.db.models import F, Max
from django.utils import timezone

from metamapper.celery import app
from utils import logging

from app.definitions.models import Datastore

from app.revisioner.models import Run, RunTask, RevisionerError
from app.revisioner.tasks import core as coretasks


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
def queue_runs(self, datastore_slug=None, *args, **kwargs):
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
        coretasks.start_revisioner_run.apply_async(args=[run.id])


@app.task(bind=True)
@logging.task_logger(__name__)
def detect_run_timeout(self, minutes=60, *args, **kwargs):
    """Garbage collection. Clears out runs if they haven't finished running after 60 minutes.
    """
    date_from = timezone.now() - timedelta(minutes=minutes)
    runs = Run.objects.filter(created_at__lte=date_from, finished_at=None)

    for run in runs:
        run.mark_as_finished()

        RevisionerError.objects.create(
            task=None,
            run_id=run.id,
            task_fcn='detect_run_timeout',
            exc_type='RevisionerRunTimeout',
            exc_message='The run timed out.',
            exc_stacktrace=None,
        )

        unfinished_tasks = (
            RunTask.objects.filter(run_id=run.id, status=RunTask.PENDING)
        )

        for task in unfinished_tasks:
            app.control.revoke(task.meta_task_id)

        unfinished_tasks.update(status=RunTask.REVOKED)
