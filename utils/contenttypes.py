# -*- coding: utf-8 -*-
from collections import namedtuple

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from app.definitions.models import (
    Datastore, Schema, Table, Column, Index, IndexColumn
)


KLASS_MAP = {
    'Datastore': Datastore,
    'Schema': Schema,
    'Table': Table,
    'Column': Column,
    'Index': Index,
    'IndexColumn': IndexColumn,
}


def get_content_type_for_model(model):
    """If we reset the database, `django_content_types` does not
    exist. So we have to prevent Django from loading the ContentType
    model and throwing an error.
    """
    if settings.DB_RESET:
        return namedtuple(
            'ContentType', ['id'],
        )(id=None)
    return ContentType.objects.get_for_model(model)


def get_content_types():
    """Get content types for the models that can be revised.
    """
    return {
        k: get_content_type_for_model(m)
        for k, m in KLASS_MAP.items()
    }
