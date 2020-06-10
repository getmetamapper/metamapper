# -*- coding: utf-8 -*-
from django.db.models import Manager

from utils.postgres.querysets import PostgresQuerySet


class PostgresManager(Manager.from_queryset(PostgresQuerySet)):
    """Adds support for PostgreSQL specifics.
    """
    use_in_migrations = True
