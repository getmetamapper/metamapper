# -*- coding: utf-8 -*-
from django.db import models, transaction
from django.utils import timezone


class HeartbeatManager(models.Manager):
    """Django manager for the healthchecks.Heartbeat model.
    """
    def beat(self):
        """Deletes the heartbeat and re-inserts a new one.
        """
        with transaction.atomic():
            self.get_queryset().delete()
            self.create(ts=timezone.now())


class Heartbeat(models.Model):
    """Record the latest heartbeat of the beat scheduler.
    """
    ts = models.DateTimeField(primary_key=True, null=False)

    objects = HeartbeatManager()
