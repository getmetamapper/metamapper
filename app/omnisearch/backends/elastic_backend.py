# -*- coding: utf-8 -*-
import collections
from django.conf import settings

import app.omnisearch.backends.base_search_backend as base

from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk

from elasticsearch_dsl import Search

import app.definitions.permissions as definition_permissions
import app.definitions.models as definition_models

from django.utils.functional import cached_property


class ElasticBackend(base.BaseSearchBackend):
    """ Elasticsearch search implementation.
    """
    INDEX_MODEL_MAP = {
        'column': 'Column',
        'table': 'Table',
        'comment': 'Comment',
    }

    client = None

    @classmethod
    def create_client(cls, *args, **kwargs):
        return Elasticsearch(
            [settings.ELASTIC_URL],
            sniff_on_start=True,
            sniff_on_connection_fail=True,
            sniffer_timeout=60,
        )

    def __new__(cls, *args, **kwargs):
        if cls.client is None:
            cls.client = cls.create_client()
        instance = super().__new__(cls)

        return instance

    def user_permission_ids(self):
        """ Returns workspace_id and datastore_ids that a user can view.
        """
        datastores = definition_models.Datastore.objects.filter(workspace=self.workspace)
        datastores = definition_permissions.get_datastores_for_user(datastores, self.user)

        return self.workspace.id, [datastore.id for datastore in datastores]

    def bulk_insert(self, actions, as_list=True, **kwargs):
        response = parallel_bulk(self.client, actions, **kwargs)
        if as_list:
            return list(response)
        return response

    def search(self, search_query_string, datastore_id=None, start=0, size=100, **extra_filters):
        workspace_id, datastore_ids = self.user_permission_ids()

        if not datastore_ids:
            # User has no access to any datastores.
            return []

        if datastore_id and datastore_id not in datastore_ids:
            # User is requesting a datastore they don't have access to.
            return []

        elif datastore_id:
            datastore_ids = [datastore_id]

        s = Search(using=self.client)
        s = s.query(
            'multi_match',
            type='phrase_prefix',
            fields=[
                'schema',
                'table',
                'description',
                'name^1.1',
                'text^1.1'
            ],
            query=search_query_string,
        )
        s = s.filter('term', workspace_id=workspace_id)
        s = s.filter('terms', datastore_id=datastore_ids)

        results = s[start:start + size]

        return [
            {
                'pk': hit.pk,
                'model_name': self.INDEX_MODEL_MAP[hit.meta.index],
                'score': hit.meta.score / results._response.hits.max_score,
                'datastore_id': hit.datastore_id,
            }
            for hit in results
        ]
