# -*- coding: utf-8 -*-
import psycopg2

import app.revisioner.revisioners as revisioners

import utils.blob as blob
import utils.logging as logging

from metamapper.celery import app

from app.revisioner import actions, definition
from app.revisioner.collectors import DefinitionCollector
from app.revisioner.models import Run, RunTask, RevisionerError
from app.revisioner.tasks.version import check_for_version_update


__all__ = [
    'start_revisioner_run',
    'revise_schema_definition',
    'commit_revisions',
]


def on_start_revisioner_run_failure(self, exc, task_id, args, kwargs, einfo):
    """Callback function for when the `start_revisioner_run` task fails.
    """
    self._run.mark_as_finished()

    RevisionerError.objects.create(
        run_id=self._run.id,
        task_id=None,
        task_fcn='start_revisioner_run',
        exc_type=type(exc).__name__,
        exc_message=str(exc),
        exc_stacktrace=einfo,
    )


@app.task(bind=True, on_failure=on_start_revisioner_run_failure)
@logging.task_logger(__name__)
def start_revisioner_run(self, run_id, *arg, **kwargs):
    """This task triggers a Revisioner run based on the provided ID. It is the
    primary entrypoint for crawling schemas and populating the Metamapper database.
    """
    self.log.with_fields(run=run_id)
    self.log.info('Starting revisioner run.')

    self._run = Run.objects.get(pk=run_id)
    self._run.mark_as_started()

    check_for_version_update.apply_async(args=[self._run.datastore_id])

    self.log.with_fields(run=run_id, datastore=self._run.datastore.slug)

    collector = DefinitionCollector(self._run.datastore)
    run_tasks = []

    for schema, schema_definition in definition.make(collector, logger=self.log):
        storage_path = f'revisioner/{self._run.datastore_id}/run_id={self._run.id}/{schema}.json.gz'
        blob.put_object(storage_path, schema_definition)
        run_tasks.append(
            RunTask(run=self._run, storage_path=storage_path, status=RunTask.PENDING),
        )
        self.log.info(f'Finished processing: {schema}')

    RunTask.objects.bulk_create(run_tasks, ignore_conflicts=True)

    revisions = []
    for content_type, content_objects in collector.unassigned.items():
        self.log.info(
            f'Processing {len(content_objects)} dropped {content_type} resources'
        )
        for content_object in content_objects:
            revisioner = revisioners.get_revisioner(
                instance=content_object,
                parent_resource=content_object.parent_resource,
            )
            revisions += revisioner.make_dropped()

    if len(revisions):
        self._run.upsert_staged_revisions(revisions)

    run_tasks = RunTask.objects.filter(run_id=self._run.id)
    for run_task in run_tasks:
        self.log.info(
            f'(task: {run_task.pk}) {run_task.storage_path}'
        )
        revise_schema_definition.apply_async(args=[run_task.id])

    # If nothing is to be done, we should force mark this run as complete.
    if not len(run_tasks) and not len(revisions):
        self._run.mark_as_finished()


def on_revise_schema_definition_success(self, retval, task_id, args, kwargs):
    """Callback function for when the `revise_schema_definition` task succeeds.
    """
    pending_task_count = (
        RunTask.objects
               .filter(run_id=self._run_task.run_id)
               .exclude(status=RunTask.SUCCESS)
               .count()
    )

    # If we have no pending tasks, then we move to commit.
    if pending_task_count < 1:
        commit_revisions.apply_async(args=[self._run_task.run_id])


def on_revise_schema_definition_failure(self, exc, task_id, args, kwargs, einfo):
    """Callback function for when the `revise_schema_definition` task fails.
    """
    self._run_task.run.mark_as_finished()
    self._run_task.mark_as_failure()

    RevisionerError.objects.create(
        run_id=self._run_task.run_id,
        task_id=self._run_task.id,
        task_fcn='revise_schema_definition',
        exc_type=type(exc).__name__,
        exc_message=str(exc),
        exc_stacktrace=einfo,
    )

    unfinished_tasks = (
        RunTask.objects.filter(run_id=self._run_task.run_id, status=RunTask.PENDING)
    )

    for task in unfinished_tasks:
        app.control.revoke(task.meta_task_id)

    unfinished_tasks.update(status=RunTask.REVOKED)


@app.task(
    bind=True,
    autoretry_for=(psycopg2.OperationalError,),
    retry_kwargs={'max_retries': 3, 'countdown': 10},
    on_success=on_revise_schema_definition_success,
    on_failure=on_revise_schema_definition_failure,
)
@logging.task_logger(__name__)
def revise_schema_definition(self, run_task_id, *args, **kwargs):
    """This processes the definition and creates any create/update Revision records.
    """
    self._run_task = RunTask.objects.get(pk=run_task_id)
    self._run_task.mark_as_started(self.request.id)

    self.log.with_fields(run=self._run_task.run_id, task=self._run_task.id)
    self.log.info(f'Processing {self._run_task.storage_path}')

    schema_definition = blob.get_object(self._run_task.storage_path)
    revisions = revisioners.extract_revisions(self._run_task.run.datastore, schema_definition)

    self.log.info(f'Resulted in {len(revisions)} revisions')

    self._run_task.run.upsert_staged_revisions(revisions)
    self._run_task.mark_as_success()


def on_commit_revisions_failure(self, exc, task_id, args, kwargs, einfo):
    """Callback function for when the `commit_revisions` task fails.
    """
    self._run.mark_as_finished()

    RevisionerError.objects.create(
        run_id=self._run.id,
        task_id=None,
        task_fcn='commit_revisions',
        exc_type=type(exc).__name__,
        exc_message=str(exc),
        exc_stacktrace=einfo,
    )


@app.task(bind=True, on_failure=on_commit_revisions_failure)
@logging.task_logger(__name__)
def commit_revisions(self, run_id, *args, **kwargs):
    """Commit the most recent batch of revisions. datastore.most_recent_run.revisions.
    should update revision.applied_on
    """
    self.log.with_fields(run=run_id)
    self._run = Run.objects.get(pk=run_id)

    actions.commit_revisions(self._run.datastore, self._run, self.log)
