# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command
from django.db.models.signals import post_migrate

from app.definitions.models import Datastore


def seed_example_datastore(sender, **kwargs):
    """If requested, we should seed the example data after the migrations have been ran.
    """
    if not settings.INCLUDE_EXAMPLE_DATASTORES or Datastore.objects.filter(slug='metamapper-example').exists():
        return

    call_command('loaddata', 'example', **{'verbosity': 0})


class Config(AppConfig):
    name = 'app.definitions'

    def ready(self):
        post_migrate.connect(seed_example_datastore, sender=self)
