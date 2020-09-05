# project/myapp/management/commands/custom_migrate.py
from django.core.management.commands.migrate import Command as MigrateCommand
from django.conf import settings
from django.core.management import call_command


class Command(MigrateCommand):
    """Override the existing migration comment to seed the database, if necessary.
    """
    def handle(self, *args, **options):
        super().handle(*args, **options)

        from app.definitions.models import Datastore

        if not settings.INCLUDE_EXAMPLE_DATASTORES:
            return

        if Datastore.objects.filter(slug='metamapper-example').exists():
            return

        call_command('loaddata', 'example', **{'verbosity': 0})
