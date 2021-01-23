# -*- coding: utf-8 -*-
import collections
import time

from django.conf import settings

import app.omnisearch.backends.base_search_backend as base

from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk

from elasticsearch_dsl import Search, A

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

    ALLOWED_FACET_MAP = {
        'datastores': 'datastore_id',
        'engines': 'datastore_engine',
        'schemas': 'schema.keyword',
        'tags': 'tags.keyword',
    }

    client = None

    @classmethod
    def create_client(cls, *args, **kwargs):
        return Elasticsearch(
            settings.ELASTIC_URL.split(','),
            **settings.ELASTIC_CLIENT_KWARGS,
        )

    def __new__(cls, *args, **kwargs):
        if cls.client is None:
            cls.client = cls.create_client()
        instance = super().__new__(cls)
        return instance

    def to_dict(self):
        return {
            'elapsed': self.elapsed,
            'results': self.results,
            'facets': self.facets,
        }

    @property
    def possible_indexes(self):
        return list(self.INDEX_MODEL_MAP.keys())

    def user_permission_ids(self):
        """Returns workspace_id and datastore_ids that a user can view.
        """
        datastores = definition_models.Datastore.objects.filter(workspace=self.workspace)

        if not self.user.is_owner(self.workspace.id):
            datastores = definition_permissions.get_datastores_for_user(datastores, self.user)

        return self.workspace.id, [datastore.id for datastore in datastores]

    def bulk_insert(self, actions, as_list=True, **kwargs):
        response = parallel_bulk(self.client, actions, **kwargs)
        if as_list:
            return list(response)
        return response

    def execute(self, query, types=None, datastores=None, start=0, size=100, **facets):
        workspace_id, datastore_ids = self.user_permission_ids()

        if not datastore_ids:
            # User has no access to any datastores.
            return []

        # Filter out datastores that the User does not have access to.
        if datastores:
            datastore_ids = [d for d in datastores if d in datastore_ids]

        index = [t for t in (types or []) if t in self.possible_indexes]

        t = time.time()
        s = Search(index=index, using=self.client)
        s = s.query(
            'simple_query_string',
            fields=[
                'exact_name^100',
                'name.raw^30',
                'name^10',
                'table^5',
                'schema^3',
                'description^3',
                'text^1.1',
                'tags',
            ],
            query=query,
        ).filter(
            'term',
            workspace_id=workspace_id,
        ).filter(
            'terms',
            datastore_id=datastore_ids,
        )

        for facet_name, es_field in self.ALLOWED_FACET_MAP.items():
            # Register facet in Elasticsearch query
            s.aggs.bucket(facet_name, A('terms', field=es_field))

            value = facets.get(facet_name)

            if value:
                s = s.filter('terms', **{es_field: value})

        results = s.execute()

        self._results = [
            {
                'pk': hit.pk,
                'model_name': self.INDEX_MODEL_MAP[hit.meta.index],
                'score': hit.meta.score / results.hits.max_score,
                'datastore_id': hit.datastore_id,
            }
            for hit in results.hits[start:start + size]
        ]

        self._facets = results.aggs
        self._elapsed = round(time.time() - t, 3)

    @property
    def results(self):
        return self._results

    @property
    def facets(self):
        return self._facets.to_dict()

    @property
    def elapsed(self):
        return self._elapsed
