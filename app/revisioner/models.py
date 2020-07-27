# -*- coding: utf-8 -*-
import hashlib
import json
import time

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

from app.authentication.models import Workspace
from app.definitions.models import Datastore
from app.revisioner.managers import RevisionManager, RunTaskManager

from utils.postgres.types import ConflictAction
from utils.mixins.models import UUIDModel, TimestampedModel
from utils.shortcuts import model_to_dict


class Run(UUIDModel):
    """Represents scan and refresh of a datastore via Revisioner.
    """
    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='run_history',
    )

    datastore = models.ForeignKey(
        to=Datastore,
        on_delete=models.CASCADE,
        related_name='run_history',
    )

    revision_count = models.PositiveIntegerField(default=0)

    created_on = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when the run was created.",
    )

    started_at = models.DateTimeField(
        default=None,
        null=True,
        help_text="Timestamp for when run queued actual processing tasks.",
    )

    finished_at = models.DateTimeField(
        default=None,
        null=True,
        help_text="Timestamp for when run finished calculating all revisions.",
    )

    @property
    def status(self):
        if self.finished:
            # TODO(scruwys) – this needs to be cached.
            if self.errors.count() > 0:
                return RunTask.FAILURE
            return RunTask.SUCCESS
        return RunTask.PENDING

    @property
    def epoch(self):
        return int(time.mktime(self.created_on.timetuple()) * 1000)

    @property
    def started(self):
        return self.started_at is not None

    @property
    def finished(self):
        return self.finished_at is not None

    @property
    def is_datastore_first_run(self):
        """Check is this run is the first run ever for the datastore.
        """
        return self.datastore.run_history.order_by('created_on').first() == self

    def mark_as_started(self, save=True):
        """Mark the run as started.
        """
        self.started_at = timezone.now()
        if save:
            self.save()

    def mark_as_finished(self, save=True):
        """Mark the run as finished.
        """
        self.revision_count = self.revisions.count()
        self.finished_at = timezone.now()
        if save:
            self.save()

    def upsert_staged_revisions(self, revisions):
        """This method performs an UPSERT of revisions
        into the metastore. We dedupe based on a checksum
        created in `Revision.set_checksum`.
        """
        rows = []
        if not len(revisions):
            return rows
        for rev in revisions:
            revision = Revision(
                workspace_id=self.workspace_id,
                run_id=self.id,
                **rev.as_dict(),
            )
            revision.set_checksum()
            revision.set_first_seen_run(self)
            rows.append(model_to_dict(revision))
        return Revision.objects\
                       .on_conflict(['workspace_id', 'checksum'], ConflictAction.UPDATE)\
                       .bulk_insert(rows, only_fields=['run', 'updated_at'])


class RunTask(models.Model):
    """Represents a Celery task that must complete before completing the run.
    """
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    PENDING = 'PENDING'
    REVOKED = 'REVOKED'

    STATUS_CHOICES = (
        (SUCCESS, SUCCESS),
        (FAILURE, FAILURE),
        (PENDING, PENDING),
        (REVOKED, REVOKED),
    )

    run = models.ForeignKey(
        to=Run,
        on_delete=models.CASCADE,
        related_name='tasks',
    )

    meta_task_id = models.CharField(
        max_length=512,
        null=True,
        help_text="Task ID for Celery",
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        null=False,
        blank=False,
        default=PENDING,
    )

    started_at = models.DateTimeField(
        default=None,
        null=True,
        help_text="Timestamp for when the task started",
    )

    finished_at = models.DateTimeField(
        default=None,
        null=True,
        help_text="Timestamp for when the task finished",
    )

    storage_path = models.CharField(max_length=512, unique=True)

    objects = RunTaskManager()

    @property
    def finished(self):
        return self.finished_at is not None

    def waiting(self):
        return self.meta_task_id is None

    def mark_as_started(self, meta_task_id=None):
        """Mark the task as started and provide the meta task ID if relevant.
        """
        self.started_at = timezone.now()
        self.meta_task_id = meta_task_id
        self.save()

    def mark_as_success(self):
        """Mark the task as finished.
        """
        self.status = RunTask.SUCCESS
        self.finished_at = timezone.now()
        self.save()

    def mark_as_failure(self):
        """Mark the task as finished.
        """
        self.status = RunTask.FAILURE
        self.finished_at = timezone.now()
        self.save()


class RevisionerError(TimestampedModel, models.Model):
    """Represents an exception thrown during the revision process.
    """
    run = models.ForeignKey(
        to=Run,
        on_delete=models.CASCADE,
        related_name='errors',
    )

    task = models.OneToOneField(
        RunTask,
        null=True,
        default=None,
        on_delete=models.CASCADE,
    )

    task_fcn = models.CharField(max_length=40, null=True, default=None)

    exc_type = models.CharField(max_length=40, null=True, default=None)

    exc_message = models.TextField(null=True, default=None)

    exc_stacktrace = models.TextField(null=True, default=None)

    class Meta:
        db_table = 'revisioner_error'


class Revision(TimestampedModel):
    """Represents a single change within a datastore-related object.
    """
    CREATED = 'created'
    DROPPED = 'dropped'
    MODIFIED = 'modified'

    ACTION_CHOICES = (
        (CREATED, 'Created'),
        (DROPPED, 'Dropped'),
        (MODIFIED, 'Modified'),
    )

    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='+',
    )

    run = models.ForeignKey(
        to=Run,
        on_delete=models.CASCADE,
        related_name='revisions',
    )

    revision_id = models.CharField(
        primary_key=True,
        max_length=40,
        unique=True,
    )

    resource_id = models.CharField(max_length=30, null=True)
    resource_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        related_name='+',
    )
    resource = GenericForeignKey('resource_type', 'resource_id')

    parent_resource_revision = models.ForeignKey(
        to='Revision',
        on_delete=models.CASCADE,
        null=True,
        to_field='revision_id',
        related_name='revisions',
        db_constraint=False,
    )

    parent_resource_id = models.CharField(max_length=30, null=True)
    parent_resource_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
    )
    parent_resource = GenericForeignKey('parent_resource_type', 'parent_resource_id')

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
        null=False,
        blank=False,
    )

    metadata = JSONField(default=dict)
    checksum = models.CharField(max_length=32)

    first_seen_run = models.ForeignKey(
        to=Run,
        on_delete=models.CASCADE,
        related_name='original_revisions',
    )

    first_seen_on = models.DateTimeField(null=False)

    applied_on = models.DateTimeField(default=None, null=True)

    objects = RevisionManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['workspace_id', 'checksum'],
                name='unique_revision_checksum',
            )
        ]

    def __str__(self):
        return '{0}({1})'.format(self.revision_id, self.action)

    @classmethod
    def revisable_types(cls):
        """List the models that are revisable.
        """
        return tuple(
            m for m in apps.get_models()
            if hasattr(m, 'created_revision')
        )

    @property
    def created_resource(self):
        """TODO(scruwys) – N+1 query issue. Fine for now but should be fixed eventually.
        """
        return (
            self.resource_type
                .model_class()
                .objects
                .filter(created_revision=self)
                .first()
        )

    @property
    def parent_instance(self):
        """TODO(scruwys) – N+1 query issue. Fine for now but should be fixed eventually.
        """
        if self.parent_resource_id:
            return self.parent_resource
        if self.parent_resource_revision_id:
            parent_revision = self.parent_resource_revision
            if parent_revision.resource_id:
                return parent_revision.resource
        return parent_revision.created_resource

    def save(self, *args, **kwargs):
        """Override save method to create the checksum.
        """
        if self._state.adding is True and not self.checksum:
            self.set_checksum()
            self.set_first_seen_run(self.run)
        return super().save(*args, **kwargs)

    def set_first_seen_run(self, run):
        """Setter helper for first seen Run.
        """
        self.first_seen_run = run
        self.first_seen_on = timezone.now()

    def set_checksum(self):
        """Create checksum from attributes.
        """
        checksum_dict = {
            'resource_id': self.resource_id,
            'resource_type': self.resource_type_id,
            'parent_resource_id': self.parent_resource_id,
            'parent_resource_type': self.parent_resource_type_id,
            'action': self.action,
            'metadata': self.metadata,
        }
        if self.parent_resource_revision_id:
            checksum_dict['parent_resource_revision_id'] = self.parent_resource_revision_id.hex
        self.checksum = hashlib.md5(
            json.dumps(checksum_dict, sort_keys=True).encode('utf-8'),
        ).hexdigest()
