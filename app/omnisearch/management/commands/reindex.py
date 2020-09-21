# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator

import app.omnisearch.backends.elastic_backend as elastic_backend
import app.definitions.models as definition_models
import app.comments.models as comment_models
import app.omnisearch.constants as omnisearch_constants

import utils.logging as logging


es = elastic_backend.ElasticBackend(workspace=None, user=None)

default_batch_size = 5000

logger = logging.getLogger(__name__)


def index_tables():
    queryset = definition_models.Table.objects\
        .select_related('schema')\
        .select_related('schema__datastore')\
        .select_related('workspace')\
        .all() \
        .order_by('id')

    paginator = Paginator(queryset, default_batch_size)

    es.client.indices.delete(index='table', ignore=404)
    es.client.indices.create(index='table', body=omnisearch_constants.TABLE_INDEX_SETTINGS)

    for page_num in paginator.page_range:
        page = paginator.get_page(page_num)
        actions = []

        for table in page.object_list:
            doc = table.to_doc()
            action = {
                "_index": "table",
                "_id": doc["pk"],
                "_source": doc,
            }
            actions.append(action)

        es.bulk_insert(actions, thread_count=5, chunk_size=1000)
        logger.info('[Table] Indexed {0} of {1} objects.'.format(page.end_index(), paginator.count))


def index_columns():
    queryset = definition_models.Column.objects\
        .select_related('table')\
        .select_related('table__workspace')\
        .select_related('table__schema')\
        .select_related('table__schema__datastore')\
        .all() \
        .order_by('id')

    paginator = Paginator(queryset, default_batch_size)

    es.client.indices.delete(index='column', ignore=404)
    es.client.indices.create(index='column', body=omnisearch_constants.COLUMN_INDEX_SETTINGS)

    for page_num in paginator.page_range:
        page = paginator.get_page(page_num)
        actions = []

        for column in page.object_list:
            doc = column.to_doc()
            action = {
                "_index": "column",
                "_id": doc["pk"],
                "_source": doc,
            }
            actions.append(action)

        es.bulk_insert(actions, thread_count=5, chunk_size=1000)
        logger.info('[Column] Indexed {0} of {1} objects.'.format(page.end_index(), paginator.count))


def index_comments():
    queryset = comment_models.Comment.objects\
        .select_related('workspace')\
        .all() \
        .order_by('id')

    paginator = Paginator(queryset, default_batch_size)

    es.client.indices.delete(index='comment', ignore=404)
    es.client.indices.create(index='comment', body=omnisearch_constants.COMMENT_INDEX_SETTINGS)

    for page_num in paginator.page_range:
        page = paginator.get_page(page_num)
        actions = []

        for comment in page.object_list:
            doc = comment.to_doc()
            action = {
                "_index": "comment",
                "_id": doc["pk"],
                "_source": doc,
            }
            actions.append(action)

        es.bulk_insert(actions, thread_count=5, chunk_size=1000)
        logger.info('[Comment] Indexed {0} of {1} objects.'.format(page.end_index(), paginator.count))


class Command(BaseCommand):
    help = 'Drops old index and reindexes all documents.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--index',
            help='Which index to reindex. Default is all',
        )

    def handle(self, *args, **options):
        action_map = {
            'table': index_tables,
            # 'column': index_columns,
            'comment': index_comments,
        }

        if options['index']:
            if options['index'] in action_map:
                logger.info(f'Reindexing {options["index"]} objects.')
                action_map[options['index']]()
            else:
                logger.info(f'Unknown index: {options["index"]}.')
                return
        else:
            for index in action_map:
                logger.info(f'Indexing {index} objects.')
                action_map[index]()
