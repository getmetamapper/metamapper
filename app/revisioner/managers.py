# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from utils.postgres.managers import PostgresManager


class RunTaskManager(models.Manager):
    """Django manager for the RunTask model.
    """


class RevisionManager(PostgresManager):
    """Django manager for the Revision model.
    """
    def for_model_instance(self, instance, *args, **kwargs):
        """Fetch revisions associated with a specific instance.
        """
        content_type = ContentType.objects.get_for_model(instance)
        queryset = self.get_queryset().filter(
            Q(revision_id=instance.created_revision_id) |  # noqa: W504
            Q(parent_resource_revision_id=instance.created_revision_id) |  # noqa: W504
            Q(resource_id=instance.id, resource_type_id=content_type.id) |  # noqa: W504
            Q(parent_resource_id=instance.id, parent_resource_type=content_type.id)
        )
        return queryset

    def created(self, unapplied_only=True, *args, **kwargs):
        """Retrieve all Revisions marked as CREATED.
        """
        queryset = self.get_queryset().filter(action=self.model.CREATED)
        if unapplied_only:
            queryset = queryset.filter(applied_on__isnull=True)
        return queryset

    def modified(self, unapplied_only=True, *args, **kwargs):
        """Retrieve all Revisions marked as MODIFIED.
        """
        queryset = self.get_queryset().filter(action=self.model.MODIFIED)
        if unapplied_only:
            queryset = queryset.filter(applied_on__isnull=True)
        return queryset

    def dropped(self, unapplied_only=True, *args, **kwargs):
        """Retrieve all Revisions marked as DROPPED.
        """
        queryset = self.get_queryset().filter(action=self.model.DROPPED)
        if unapplied_only:
            queryset = queryset.filter(applied_on__isnull=True)
        return queryset
