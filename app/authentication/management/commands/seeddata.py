# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management.commands import loaddata

from app.authentication.models import User


class Command(loaddata.Command):
    """Overrides loaddata command to add MM-specific logic.
    """
    help = 'Seed database with sample data'

    def handle(self, *args, **options):
        if not settings.DJANGO_ENV == 'development':
            self.stdout.write('Can only execute command in development environment.')
            return

        super().handle(*args, **options)

        users = User.objects.all()

        for user in users:
            if not user.password == 'password1234':
                continue
            user.set_password("password1234")
            user.save()
            self.stdout.write(self.style.SUCCESS('Successfully updated "%s"' % user.email))
