# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand


import app.omnisearch.backends.elastic_backend as elastic_backend
import app.definitions.models as definition_models
import app.comments.models as comment_models
import app.omnisearch.constants as omnisearch_constants


es = elastic_backend.ElasticBackend(workspace=None, user=None)


def index_tables():
    tables = definition_models.Table.objects\
        .select_related('schema')\
        .select_related('schema__datastore')\
        .select_related('workspace')\
        .all()

    es.client.indices.delete(index='table', ignore=404)
    es.client.indices.create(index='table', body=omnisearch_constants.TABLE_INDEX_SETTINGS)

    for table in tables:
        doc = table.to_doc()
        es.client.index(index='table', id=doc['pk'], body=doc)


def index_columns():
    columns = definition_models.Column.objects\
        .select_related('table')\
        .select_related('table__workspace')\
        .select_related('table__schema')\
        .select_related('table__schema__datastore')\
        .all()

    es.client.indices.delete(index='column', ignore=404)
    es.client.indices.create(index='column', body=omnisearch_constants.COLUMN_INDEX_SETTINGS)

    for column in columns:
        doc = column.to_doc()
        es.client.index(index='column', id=doc['pk'], body=doc)


def index_comments():
    comments = comment_models.Comment.objects\
        .select_related('workspace')\
        .all()

    es.client.indices.delete(index='comment', ignore=404)
    es.client.indices.create(index='comment', body=omnisearch_constants.COMMENT_INDEX_SETTINGS)

    for comment in comments:
        doc = comment.to_doc()
        es.client.index(index='comment', id=doc['pk'], body=doc)


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
            'column': index_columns,
            'comment': index_comments,
        }

        if options['index']:
            if options['index'] in action_map:
                self.stdout.write(f'Reindexing {options["index"]}.')
                action_map[options['index']]()
            else:
                self.stdout.write(f'Unknown index: {options["index"]}.')
                return
        else:
            for index in action_map:
                self.stdout.write(f'Indexing {index}.')
                action_map[index]()
