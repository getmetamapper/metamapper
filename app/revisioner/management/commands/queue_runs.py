# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from app.revisioner.tasks import scheduler


class Command(BaseCommand):
    help = 'Queue run(s) to update datastore metadata'

    def add_arguments(self, parser):
        parser.add_argument(
            '--datastore_slug',
            help='Datastore slug (if applicable)',
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Hours since the last run',
        )

    def handle(self, *args, **options):
        """Execute the command.
        """
        runs = scheduler.create_runs(**options)

        if len(runs):
            scheduler.queue_runs(options['datastore_slug'])
