# -*- coding: utf-8 -*-
import app.comments.models as comment_models
import app.definitions.models as definition_models
import app.omnisearch.backends.elastic_backend as elastic_backend

import utils.logging as logging

from metamapper.celery import app


INDEX_MODEL_MAP = {
    'column': definition_models.Column,
    'table': definition_models.Table,
    'comment': comment_models.Comment,
}


@app.task(bind=True)
@logging.task_logger(__name__)
def update_single_es_object(self, index_name, instance_id):
    """Update an object in the provided Elasticsearch index.
    """
    es = elastic_backend.ElasticBackend(workspace=None, user=None)
    ob = INDEX_MODEL_MAP[index_name].objects.filter(id=instance_id).first()

    if ob:
        es.client.update(index=index_name, id=instance_id, body={'doc': ob.to_doc(), 'doc_as_upsert': True})


@app.task(bind=True)
@logging.task_logger(__name__)
def remove_single_es_object(self, index_name, instance_id):
    """Remove an object from the provided Elasticsearch index.
    """
    es = elastic_backend.ElasticBackend(workspace=None, user=None)
    es.client.delete(index=index_name, id=instance_id, ignore=404)
