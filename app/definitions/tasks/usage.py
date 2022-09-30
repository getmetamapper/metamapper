# -*- coding: utf-8 -*-
import datetime as dt
import hashlib
import random

from django.db import connection
from django.db.models import Q
from django.utils import timezone

from metamapper.celery import app

from app.inspector import service as inspector
from app.definitions.models import Datastore, TableUsageExists

from utils import logging
from utils.shortcuts import dedupe_by_keys
from utils.sqlparser import Parser, Session


__all__ = [
    'delete_table_usage_older_than_90_days',
    'queue_table_usage_jobs',
    'get_query_history_results',
    'set_usage_from_query_text',
]


def perform_upsert(rows, idempotency_id):
    """Perform an increasing upsert on the query count field.
    """
    statement = '''
        INSERT INTO definitions_table_usage as t
            (datastore_id, execution_date, db_schema, db_table, db_user, query_count)
        VALUES
            (%(datastore_id)s, %(execution_date)s, %(db_schema)s, %(db_table)s, %(db_user)s, %(query_count)s)
        ON CONFLICT
            (datastore_id, execution_date, db_schema, db_table, db_user)
        DO UPDATE SET
            query_count = (t.query_count + EXCLUDED.query_count);
    '''

    with connection.cursor() as cursor:
        cursor.executemany(statement, rows)

    TableUsageExists.objects.create(id=idempotency_id)


@app.task(bind=True)
@logging.task_logger(__name__)
def queue_table_usage_jobs(self, countdown_in_minutes=0):
    """Schedule job for calculating table usage. Occurs every 4 hours.
    """
    expression = timezone.now() - dt.timedelta(hours=4)
    datastores = (
        Datastore
        .objects
        .filter(engine=Datastore.SNOWFLAKE)
        .filter(is_enabled=True)
        .filter(Q(usage_last_synced_at__lte=expression) | Q(usage_last_synced_at__isnull=True))
    )

    self.log.info(
        'Found {0} datastores(s)'.format(len(datastores))
    )

    if not len(datastores):
        return

    for datastore in datastores.distinct():
        async_kwargs = {
            'args': [
                datastore.datastore_id,
                datastore.usage_sync_start_date.strftime('%Y-%m-%d'),
                expression.strftime('%Y-%m-%d'),
            ],
            'countdown': random.randint(0, (60 * countdown_in_minutes)),
        }
        get_query_history_results.apply_async(**async_kwargs)

    datastores.update(usage_last_synced_at=timezone.now())


@app.task(bind=True)
@logging.task_logger(__name__)
def get_query_history_results(self, datastore_id, start_date, end_date):
    """Hit the datastore for past queries and send them to be processed.
    """
    datastore = Datastore.objects.get(id=datastore_id)
    resultset = inspector.query_history(datastore, start_date, end_date)
    resultcnt = 0

    self.log.with_fields(datastore=datastore.slug)
    self.log.info('Getting query history results.')

    for result in resultset:
        async_kwargs = {
            'args': [
                datastore.datastore_id,
                result['execution_date'].strftime('%Y-%m-%d'),
                result['db_name'],
                result['db_user'],
                result['db_schema'],
                result['query_text'],
                result['query_count'],
            ],
            'countdown': random.randint(0, 30),
        }
        set_usage_from_query_text.apply_async(**async_kwargs)
        resultcnt += 1

    self.log.info(
        'Queued {0} queries to be processed.'.format(resultcnt)
    )

    update_table_usage_metrics.apply_async(args=[datastore.datastore_id], countdown=(60 * 30))


@app.task(bind=True)
@logging.task_logger(__name__)
def set_usage_from_query_text(
    self,
    datastore_id,
    execution_date,
    db_name,
    db_user,
    db_schema,
    query_text,
    query_count,
):
    """Process the database queries and upsert them to our usage schema.
    """
    idempotency_id = hashlib.md5("".join([
        datastore_id,
        execution_date,
        db_name,
        db_user,
        db_schema,
        query_text,
    ]).encode()).hexdigest()

    if TableUsageExists.objects.filter(id=idempotency_id).exists():
        return

    try:
        db_session = Session(database=db_name, schema=db_schema, user=db_user)
        sql_parser = Parser(query_text, db_session=db_session)
        table_data = sql_parser.get_tables()
    except (AttributeError, IndexError, ValueError):
        return

    upsert_data = []
    upsert_cols = ['datastore_id', 'execution_date', 'db_schema', 'db_table', 'db_user']

    for table in table_data:
        if table['db'].upper() != db_name.upper():
            continue

        result_kwargs = {
            'datastore_id': datastore_id,
            'execution_date': execution_date,
            'db_schema': table['db_schema'],
            'db_table': table['db_table'],
            'db_user': db_user,
            'query_count': query_count,
        }

        upsert_data.append(result_kwargs)

    perform_upsert(dedupe_by_keys(upsert_data, upsert_cols), idempotency_id)


@app.task(bind=True)
def delete_table_usage_older_than_90_days(self, *args, **kwargs):
    """Remove usage records that are over 90 days old.
    """
    with connection.cursor() as cursor:
        cursor.execute('''
            DELETE FROM definitions_table_usage
                  WHERE execution_date::timestamp < NOW() - INTERVAL '90 days'
        ''')

        cursor.execute('''
            DELETE FROM definitions_table_usage_exists
                  WHERE created_at::timestamp < NOW() - INTERVAL '90 days'
        ''')


@app.task(bind=True)
@logging.task_logger(__name__)
def update_table_usage_metrics(self, datastore_id):
    """Update metrics on the table based on usage statistics.
    """
    statement = '''
    WITH usage_metrics AS (
        SELECT
            db_schema,
            db_table,
            SUM(query_count) as total_queries,
            COUNT(distinct db_user) as total_users,
            MIN(execution_date) as first_seen,
            RANK() OVER (ORDER BY sum(query_count) asc) as ranking
         FROM definitions_table_usage
        WHERE datastore_id = %(datastore_id)s
     GROUP BY
        db_schema,
        db_table
    )

    UPDATE definitions_table
    SET
      usage_score = GREATEST(COALESCE((u.ranking/(SELECT COUNT(1) FROM usage_metrics)::float)::decimal(6,4)*100,0)-1,0),
      usage_total_users = u.total_users,
      usage_total_queries = u.total_queries,
      usage_window = CURRENT_TIMESTAMP::date - u.first_seen::date
    FROM usage_metrics u
    JOIN definitions_schema s
      ON u.db_schema = s.name
     AND s.datastore_id = %(datastore_id)s
    WHERE definitions_table.name = u.db_table
      AND definitions_table.schema_id = s.object_id
    '''

    with connection.cursor() as cursor:
        cursor.execute(statement, {'datastore_id': datastore_id})
