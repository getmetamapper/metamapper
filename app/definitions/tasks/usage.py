# -*- coding: utf-8 -*-
import datetime as dt
import random

from django.db import connection
from django.db.models import Q
from django.utils import timezone

from metamapper.celery import app

from app.inspector import service as inspector
from app.definitions.models import Datastore

from utils import logging
from utils.shortcuts import dedupe_by_keys
from utils.sqlparser import Parser, Session


__all__ = [
    'delete_table_usage_older_than_90_days',
    'queue_table_usage_jobs',
    'get_query_history_results',
    'set_usage_from_query_text',
]


def perform_upsert(rows):
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
    try:
        db_session = Session(database=db_name, schema=db_schema, user=db_user)
        sql_parser = Parser(query_text, db_session=db_session)
        table_data = sql_parser.get_tables()
    except (AttributeError, IndexError, ValueError):
        return

    upsert_data = []
    upsert_cols = ['execution_date', 'datastore_id', 'db_user', 'db_schema', 'db_table']

    for table in table_data:
        if table['db'].upper() != db_name.upper():
            continue

        result_kwargs = {
            'datastore_id': datastore_id,
            'db_schema': table['db_schema'],
            'db_table': table['db_table'],
            'db_user': db_user,
            'execution_date': execution_date,
            'query_count': query_count,
        }

        upsert_data.append(result_kwargs)

    perform_upsert(dedupe_by_keys(upsert_data, upsert_cols))


@app.task(bind=True)
def delete_table_usage_older_than_90_days(self, *args, **kwargs):
    """Remove usage records that are over 90 days old.
    """
    with connection.cursor() as cursor:
        cursor.execute('''
            DELETE FROM definitions_table_usage
                  WHERE to_timestamp(execution_date) < NOW() - INTERVAL '90 days'
        ''')
