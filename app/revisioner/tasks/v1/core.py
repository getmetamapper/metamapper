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


def dedupe_by_keys(data, dedupe_by):
    """Helper function for deduplicating a list of dicts by a set of keys.
    """
    output = {}

    for d in data:
        output["".join([str(v) for k, v in d.items() if k in dedupe_by])] = d

    return list(output.values())


def upsert_schemas(schemas, on_conflict=None):
    """Perform an upsert of a single schema object.
    """
    if not on_conflict:
        on_conflict = ['datastore_id', 'object_id']

    if len(schemas) == 0:
        return

    Schema.objects \
          .on_conflict(on_conflict, ConflictAction.UPDATE) \
          .bulk_insert(dedupe_by_keys(schemas, on_conflict))


def delete_schemas(ids):
    """Perform deletion based on provided IDs.
    """
    Schema.all_objects.filter(id__in=ids).hard_delete()


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
         .on_conflict(on_conflict, ConflictAction.UPDATE) \
         .bulk_insert(dedupe_by_keys(data, on_conflict))


def delete_tables(ids):
    """Perform deletion based on provided IDs.
    """
    Table.all_objects.filter(id__in=ids).hard_delete()


def upsert_columns(columns, run_id, on_conflict=None):
    """Perform an upsert of a batch of column objects.
    """
    if not on_conflict:
        on_conflict = ['table_id', 'object_id']

    if len(columns) == 0:
        return

    Column.objects \
          .on_conflict(on_conflict, ConflictAction.UPDATE) \
          .bulk_insert(dedupe_by_keys(columns, on_conflict))

    Column.objects.filter(table_id=columns[0]['table_id']).exclude(run_id=run_id).delete()


def delete_columns(ids):
    """Perform deletion based on provided IDs.
    """
    Column.all_objects.filter(id__in=ids).hard_delete()


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


def apply_corrections_to_schema(run):
    """Apply the corrections for Tables. This is done primarily when an asset is renamed.
    """
    items = Schema.objects.raw("""
    SELECT
        t2.id as recent_id,
        t2.object_id AS recent_object_id,
        t2.name AS recent_name,
        t1.*
    FROM definitions_schema t1
    JOIN definitions_schema t2
      ON t1.id <> t2.id
     AND t1.object_ref = t2.object_ref
   WHERE t1.deleted_at IS NOT NULL
     AND t2.deleted_at IS NULL
     AND t1.datastore_id = %s
    """, [run.datastore_id])

    results = []
    columns = [
        'object_id',
        'name',
        'deleted_at',
    ]

    deleted = []
    exclude = columns.copy()
    exclude += [
        'recent_%s' % f for f in exclude
    ]

    for item in items:
        data = model_to_dict(item, exclude=exclude)
        data['run_id'] = run.id

        for f in columns:
            data[f] = getattr(item, 'recent_%s' % f, None)

        deleted.append(item.recent_id)
        results.append(data)

    with transaction.atomic():
        delete_schemas(deleted)
        upsert_schemas(results, on_conflict=['id'])


def apply_corrections_to_table(run):
    """Apply the corrections for Tables. This is done primarily when an asset is renamed.
    """
    items = Table.objects.raw("""
    SELECT
        t2.id AS recent_id,
        t2.object_id AS recent_object_id,
        t2.schema_id AS recent_schema_id,
        t2.name as recent_name,
        t2.kind as recent_kind,
        t2.db_comment as recent_db_comment,
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
    columns = [
        'object_id',
        'name',
        'schema_id',
        'deleted_at',
    ]

    columns += [
        'kind',
        'db_comment',
    ]

    deleted = []
    exclude = columns.copy()
    exclude += [
        'recent_%s' % f for f in exclude
    ]

    for item in items:
        data = model_to_dict(item, exclude=exclude)
        data['run_id'] = run.id

        # Replace old fields with recent fields.
        for f in columns:
            data[f] = getattr(item, 'recent_%s' % f, None)

        deleted.append(item.recent_id)
        results.append(data)

    with transaction.atomic():
        delete_tables(deleted)
        upsert_tables(results, on_conflict=['id'])


def apply_corrections_to_columns(run):
    """Apply the corrections for Columns. This is done primarily when an asset is renamed.
    """
    items = Column.objects.raw("""
    SELECT
        t2.id as recent_id,
        t2.object_id AS recent_object_id,
        t2.table_id AS recent_table_id,
        t2.name as recent_name,
        t2.ordinal_position as recent_ordinal_position,
        t2.max_length as recent_max_length,
        t2.numeric_scale as recent_numeric_scale,
        t2.is_primary as recent_is_primary,
        t2.is_nullable as recent_is_nullable,
        t2.default_value as recent_default_value,
        t2.db_comment as recent_db_comment,
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
    columns = [
        'object_id',
        'name',
        'table_id',
        'deleted_at',
    ]

    columns += [
        'ordinal_position',
        'is_primary',
        'is_nullable',
        'max_length',
        'numeric_scale',
        'default_value',
        'db_comment',
    ]

    deleted = []
    exclude = columns.copy()
    exclude += [
        'recent_%s' % f for f in exclude
    ]

    for item in items:
        data = model_to_dict(item, exclude=exclude)
        data['run_id'] = run.id

        for f in columns:
            data[f] = getattr(item, 'recent_%s' % f, None)

        deleted.append(item.recent_id)
        results.append(data)

    with transaction.atomic():
        delete_columns(deleted)
        upsert_columns(results, run.id, on_conflict=['id'])


@app.task(bind=True)
@logging.task_logger(__name__)
def start_run(self, run_id):
    """This task triggers a Revisioner run based on the provided ID.
    """
    run = Run.objects.get(id=run_id)
    run.mark_as_started()

    task = run.tasks.create(path=f"start_run/{run.id}", status=RunTask.PENDING)
    data = []

    collector = SchemaDefinitionCollector(run.datastore)

    with task.task_context(self.request.id, lambda e: run.mark_as_finished()):
        for schema, definition in collector.execute(run):
            path = f"revisioner/{run.datastore_id}/run_id={run.id}/{schema}.json.gz"

            self.log.info(
                'Uploading schema definition: {0}'.format(schema)
            )

            blob.put_object(path, definition)
            data.append(
                RunTask(run=run, path=path, status=RunTask.PENDING)
            )

        RunTask.objects.bulk_create(data, ignore_conflicts=True)

        tasks = [
            process_schema.s(t.id) for t in RunTask.objects.filter(run_id=run.id, path__startswith="revisioner")
        ]

        self.log.info(
            'Submitted {0} tasks'.format(len(tasks))
        )

        chord(tasks)(complete_run.si(run_id))

    check_version.apply_async(args=[run.datastore_id])


@app.task(bind=True)
@logging.task_logger(__name__)
def process_schema(self, run_task_id):
    """Process schema-level data based on the provided run task.
    """
    task = RunTask.objects.get(id=run_task_id)

    with task.task_context(self.request.id):
        definition = blob.get_object(task.path)

        self.log.info(
            'Processing schema definition: {0}'.format(definition['schema'])
        )

        with transaction.atomic():
            upsert_schemas([definition['schema']])
            upsert_tables(definition['tables'])

            for table in definition['tables']:
                upsert_columns(table['columns'], task.run_id)

            Table.objects \
                 .filter(schema_id=definition['schema']['object_id']) \
                 .exclude(run_id=task.run_id) \
                 .delete()


@app.task(bind=True)
@logging.task_logger(__name__)
def complete_run(self, run_id, **kwargs):
    """Apply bulk operations to data assets for this run.
    """
    run = Run.objects.get(id=run_id)

    task = run.tasks.create(path=f"complete_run/{run.id}", status=RunTask.PENDING)

    steps = (
        delete_objects_from_past_runs,
        apply_corrections_to_columns,
        apply_corrections_to_table,
        apply_corrections_to_schema,
    )

    with task.task_context(self.request.id):
        for step in steps:
            step(run)

    self.log.info('Run has completed')
    run.mark_as_finished()
