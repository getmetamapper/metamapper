# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from app.sso import tasks


class Command(BaseCommand):
    help = 'Queue SSO domains for verification'

    def handle(self, *args, **options):
        """Execute the command.
        """
        tasks.queue_domain_verifications()
