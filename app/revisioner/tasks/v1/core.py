# -*- coding: utf-8 -*-
import utils.blob as blob
import utils.logging as logging

from app.definitions.models import Schema, Table, Column
from app.revisioner.models import Run, RunTask
from app.revisioner.tasks.v1.collector import SchemaDefinitionCollector
from app.revisioner.tasks.v1.version import check_version

from celery import chord
from django.db import transaction
from metamapper.celery import app

from utils.postgres.types import ConflictAction
from utils.shortcuts import model_to_dict


__all__ = ['start_run']


def upsert_schema(schema, on_conflict=None):
    """Perform an upsert of a single schema object.
    """
    if not on_conflict:
        on_conflict = ['datastore_id', 'object_id']

    Schema.objects \
          .on_conflict(['datastore_id', 'object_id'], ConflictAction.UPDATE) \
          .bulk_insert([schema])


def upsert_tables(tables, on_conflict=None):
    """Perform an upsert of a batch of table objects.
    """
    if not on_conflict:
        on_conflict = ['schema_id', 'object_id']

    if len(tables) == 0:
        return

    data = [
        {k: v for k, v in d.items() if k != 'columns'}
        for d in tables
    ]

    Table.objects \
         .on_conflict(['schema_id', 'object_id'], ConflictAction.UPDATE) \
         .bulk_insert(data)


def upsert_columns(columns, run_id, on_conflict=None):
    """Perform an upsert of a batch of column objects.
    """
    if not on_conflict:
        on_conflict = ['table_id', 'object_id']

    if len(columns) == 0:
        return

    Column.objects \
          .on_conflict(['table_id', 'object_id'], ConflictAction.UPDATE) \
          .bulk_insert(columns)

    Column.objects.filter(table_id=columns[0]['table_id']).exclude(run_id=run_id).delete()


def delete_objects_from_past_runs(run):
    """Soft delete objects that did not show up in this run.
    """
    Schema.objects \
          .filter(datastore_id=run.datastore_id) \
          .exclude(run_id=run.id) \
          .delete()

    Table.objects \
         .filter(schema__datastore_id=run.datastore_id) \
         .exclude(run_id=run.id) \
         .delete()

    Column.objects \
          .filter(table__schema__datastore_id=run.datastore_id) \
          .exclude(run_id=run.id) \
          .delete()


def apply_corrections_to_table(run):
    """
    """
    items = Table.objects.raw("""
    SELECT
        t2.id as recent_id,
        t2.object_id AS recent_object_id,
        t2.schema_id AS recent_schema_id,
        t2.name as recent_name,
        t1.*
    FROM definitions_table t1
    JOIN definitions_table t2
      ON t1.id <> t2.id
     AND t1.object_ref = t2.object_ref
    JOIN definitions_schema s
      ON t1.schema_id = s.object_id
   WHERE t1.deleted_at IS NOT NULL
     AND t2.deleted_at IS NULL
     AND s.datastore_id = %s
    """, [run.datastore_id])

    results = []
    exclude = [
        'id',
        'recent_id',
        'object_id',
        'recent_object_id',
        'name',
        'recent_name',
        'schema_id',
        'recent_schema_id',
        'deleted_at',
    ]

    for item in items:
        data = model_to_dict(item, exclude=exclude)
        data['id'] = item.recent_id
        data['schema_id'] = item.recent_schema_id
        data['object_id'] = item.recent_object_id
        data['name'] = item.recent_name
        results.append(data)

    upsert_tables(results, on_conflict=['id'])


def apply_corrections_to_columns(run):
    """
    """
    items = Column.objects.raw("""
    SELECT
        t2.id as recent_id,
        t2.object_id AS recent_object_id,
        t2.table_id AS recent_table_id,
        t2.name as recent_name,
        t1.*
    FROM definitions_column t1
    JOIN definitions_column t2
      ON t1.id <> t2.id
    JOIN definitions_table t
      ON t1.table_id = t.object_id
    JOIN definitions_schema s
      ON t.schema_id = s.object_id
     AND t1.object_ref = t2.object_ref
   WHERE t1.deleted_at IS NOT NULL
     AND t2.deleted_at IS NULL
     AND s.datastore_id = %s
    """, [run.datastore_id])

    results = []
    exclude = [
        'id',
        'recent_id',
        'object_id',
        'recent_object_id',
        'name',
        'recent_name',
        'table_id',
        'recent_table_id',
        'deleted_at',
    ]

    for item in items:
        data = model_to_dict(item, exclude=exclude)
        data['id'] = item.recent_id
        data['table_id'] = item.recent_table_id
        data['object_id'] = item.recent_object_id
        data['name'] = item.recent_name
        results.append(data)

    upsert_columns(results, run.id, on_conflict=['id'])


@app.task(bind=True)
@logging.task_logger(__name__)
def start_run(self, run_id):
    """This task triggers a Revisioner run based on the provided ID.
    """
    run = Run.objects.get(id=run_id)
    run.mark_as_started()

    check_version.apply_async(args=[run.datastore_id])

    collector = SchemaDefinitionCollector(run.datastore)

    data = []

    for schema, definition in collector.execute(run):
        path = f'revisioner/{run.datastore_id}/run_id={run.id}/{schema}.json.gz'

        blob.put_object(path, definition)
        data.append(
            RunTask(run=run, storage_path=path, status=RunTask.PENDING),
        )

    RunTask.objects.bulk_create(data, ignore_conflicts=True)

    tasks = [
        process_schema.s(t.id) for t in RunTask.objects.filter(run_id=run.id)
    ]

    chord(tasks)(complete_run.si(run_id))


@app.task(bind=True)
@logging.task_logger(__name__)
def process_schema(self, run_task_id):
    """Process schema-level data based on the provided run task.
    """
    task = RunTask.objects.get(id=run_task_id)
    task.mark_as_started(self.request.id)

    try:
        definition = blob.get_object(task.storage_path)

        with transaction.atomic():
            upsert_schema(definition['schema'])
            upsert_tables(definition['tables'])

            for table in definition['tables']:
                upsert_columns(table['columns'], task.run_id)

            Table.objects \
                 .filter(schema_id=definition['schema']['object_id']) \
                 .exclude(run_id=task.run_id) \
                 .delete()
    except Exception as error:
        task.mark_as_failed(str(error))
    else:
        task.mark_as_succeeded()


@app.task(bind=True)
@logging.task_logger(__name__)
def complete_run(self, run_id, **kwargs):
    """
    """
    run = Run.objects.get(id=run_id)

    steps = (
        delete_objects_from_past_runs,
        apply_corrections_to_table,
        apply_corrections_to_columns,
    )

    for step in steps:
        step(run)

    run.mark_as_finished()
