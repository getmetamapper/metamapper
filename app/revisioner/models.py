# -*- coding: utf-8 -*-
import contextlib
import sys
import time

from django.db import models
from django.utils import timezone

from app.authentication.models import Workspace
from app.definitions.models import Datastore

from utils.mixins.models import UUIDModel


class Run(UUIDModel):
    """Represents scan and refresh of a datastore via Revisioner.
    """
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    PENDING = 'PENDING'
    PARTIAL = 'PARTIAL'

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

    tasks_count = models.IntegerField(default=0)
    fails_count = models.IntegerField(default=0)

    @property
    def status(self):
        if self.finished_at is None:
            return Run.PENDING
        elif self.tasks_count == 1:
            return Run.FAILURE
        elif self.fails_count > 0:
            return Run.PARTIAL
        return Run.SUCCESS

    @property
    def epoch(self):
        return int(time.mktime(self.created_at.date().timetuple()) * 1000)

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
        return self.datastore.run_history.order_by('created_at').first() == self

    def mark_as_started(self, save=True):
        """Mark the run as started.
        """
        self.started_at = timezone.now()
        if save:
            self.save()

    def mark_as_finished(self, save=True):
        """Mark the run as finished.
        """
        self.tasks_count = self.tasks.count()
        self.fails_count = self.tasks.filter(status=RunTask.FAILURE).count()
        self.finished_at = timezone.now()

        if save:
            self.save()


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

    error = models.TextField(null=True)

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

    path = models.CharField(max_length=512, unique=True)

    @property
    def finished(self):
        return self.finished_at is not None

    def waiting(self):
        return self.meta_task_id is None

    def mark_as_started(self, meta_task_id=None, save=True):
        """Mark the task as started and provide the meta task ID if relevant.
        """
        self.started_at = timezone.now()
        self.meta_task_id = meta_task_id
        if save:
            self.save()

    def mark_as_succeeded(self):
        """Mark the task as finished.
        """
        self.status = RunTask.SUCCESS
        self.finished_at = timezone.now()
        self.save()

    def mark_as_failed(self, message=None):
        """Mark the task as finished.
        """
        self.status = RunTask.FAILURE
        self.error = message
        self.finished_at = timezone.now()
        self.save()

    @contextlib.contextmanager
    def task_context(self, meta_task_id, on_failure=None):
        """Run some code as a task.
        """
        self.mark_as_started(meta_task_id, save=False)

        try:
            yield self
        except Exception as error:
            self.mark_as_failed(str(error))
            if on_failure and callable(on_failure):
                on_failure(error)
            if len(sys.argv) > 1 and sys.argv[1] == 'test':
                raise
        else:
            self.mark_as_succeeded()
