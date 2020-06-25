# -*- coding: utf-8 -*-
from django.db import models, transaction
from django.utils import timezone


HEALTHY = "healthy"
UNHEALTHY = "unhealthy"
NOT_CONFIGURED = "not_configured"


class HeartbeatManager(models.Manager):
    """Django manager for the healthchecks.Heartbeat model.
    """
    def beat(self):
        """Deletes the heartbeat and re-inserts a new one.
        """
        with transaction.atomic():
            self.get_queryset().delete()
            self.create(ts=timezone.now())
        return self.first()


class Heartbeat(models.Model):
    """Record the latest heartbeat of the beat scheduler.
    """
    ts = models.DateTimeField(primary_key=True, null=False)

    objects = HeartbeatManager()

    @property
    def status(self):
        if (timezone.now() - self.ts).total_seconds() < (60 * 3):
            return HEALTHY
        return UNHEALTHY

    def __str__(self):
        return 'Heartbeat<%s>' % self.ts
