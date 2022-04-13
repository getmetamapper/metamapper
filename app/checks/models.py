# -*- coding: utf-8 -*-
import os
from datetime import timedelta
from jinja2 import Template

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from app.authentication.models import Workspace, User
from app.definitions.models import Datastore

from utils.delete.models import SoftDeletionModel
from utils.shortcuts import epoch_now, load_class
from utils.mixins.models import StringPrimaryKeyModel, TimestampedModel


class CheckQuery(models.Model):
    """Unique representation of a Query used in a Job.
    """
    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='+',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    datastore = models.ForeignKey(
        to=Datastore,
        on_delete=models.CASCADE,
        related_name='+',
    )

    key = models.CharField(db_index=True, editable=False, max_length=32)

    sql_text = models.TextField()

    columns = ArrayField(models.CharField(max_length=255, blank=False), default=list)

    class Meta:
        db_table = 'checks_query'
        unique_together = [
            ('key', 'workspace'),
        ]

    def to_template(self):
        """Return query text as Jinja2 template.
        """
        return Template(self.sql_text)


class Check(StringPrimaryKeyModel, TimestampedModel):
    """Data quality check defined by the user.
    """
    INTERVAL_CHOICES = [
        timedelta(minutes=30),
        timedelta(hours=1),
        timedelta(hours=2),
        timedelta(hours=4),
        timedelta(hours=6),
        timedelta(hours=12),
        timedelta(days=1),
        timedelta(days=3),
        timedelta(days=7),
        timedelta(days=30),
    ]

    datastore = models.ForeignKey(
        to=Datastore,
        on_delete=models.CASCADE,
        related_name='checks',
    )

    creator = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='+',
    )

    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='+',
    )

    query = models.ForeignKey(
        to=CheckQuery,
        on_delete=models.CASCADE,
        related_name='+',
    )

    last_execution = models.ForeignKey(
        to='checks.CheckExecution',
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
    )

    name = models.CharField(max_length=255, null=False, blank=False)
    tags = ArrayField(models.CharField(max_length=32, blank=True), default=list)
    is_enabled = models.BooleanField(default=True)
    short_desc = models.CharField(max_length=255, null=True, blank=True)
    interval = models.DurationField(default=timedelta(hours=1))

    class Meta:
        db_table = 'checks'


class CheckExpectation(SoftDeletionModel, TimestampedModel):
    """Specific test to run against the query response.
    """
    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='+',
    )

    job = models.ForeignKey(
        to=Check,
        on_delete=models.CASCADE,
        related_name='expectations',
    )

    handler_class = models.TextField()
    handler_input = models.JSONField(default=dict)

    pass_value_class = models.TextField()
    pass_value_input = models.JSONField(default=dict)

    class Meta:
        db_table = 'checks_expectation'

    @property
    def description(self):
        """str: The description of the expectation.
        """
        pass_value_class = self.get_pass_value_class()
        pass_value_template = Template(pass_value_class.Meta.desc)
        pass_value_rendered = pass_value_template.render(**self.pass_value_input)
        handler_class = self.get_handler_class()
        handler_template = Template(handler_class.Meta.desc)
        handler_rendered = handler_template.render(**self.handler_input)
        description = ' '.join([handler_rendered, pass_value_rendered])
        if not description.endswith('.'):
            description += '.'
        parts = description.split()
        return ' '.join([parts[0].title()] + parts[1:])

    def get_pass_value_class(self):
        """Retrieve the class that manages the `pass_value` logic.
        """
        from app.checks.tasks.pass_values import validator
        return validator.get_class(self.pass_value_class)

    def get_handler_class(self):
        """Retrieve the class that manages expectation logic.
        """
        from app.checks.tasks.expectations import validator
        return validator.get_class(self.handler_class)

    def do_check(self, dataframe):
        """Load handler and evaluate if the expectation is met.
        """
        pass_value_class = self.get_pass_value_class()
        pass_value = pass_value_class(**self.pass_value_input)
        handler_class = self.get_handler_class()
        handler = handler_class(dataframe, pass_value, **self.handler_input)
        handler.do_check()
        return CheckExpectationResult(
            expectation=self,
            passed=handler.passed,
            observed_value=handler.observed_value,
            expected_value=handler.expected_value)


class CheckExecution(models.Model):
    """Specific execution instance of a check.
    """
    FAILURE = 'FAILURE'
    SUCCESS = 'SUCCESS'
    PENDING = 'PENDING'

    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='+',
    )

    job = models.ForeignKey(
        to=Check,
        on_delete=models.CASCADE,
        related_name='executions',
    )

    query = models.ForeignKey(
        to=CheckQuery,
        on_delete=models.CASCADE,
        related_name='+',
    )

    epoch = models.BigIntegerField(default=epoch_now)

    tasks_count = models.IntegerField(default=0)
    fails_count = models.IntegerField(default=0)

    error = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    started_at = models.DateTimeField(
        default=None,
        null=True,
        help_text='Timestamp for when the execution started',
    )

    finished_at = models.DateTimeField(
        default=None,
        null=True,
        help_text='Timestamp for when the execution finished',
    )

    class Meta:
        db_table = 'checks_execution'
        unique_together = [
            ('job', 'epoch'),
        ]

    def __str__(self):
        return '%s/%s' % (self.job_id, self.epoch)

    @property
    def status(self):
        if not self.completed:
            return CheckExecution.PENDING
        elif self.fails_count > 0 or self.error is not None:
            return CheckExecution.FAILURE
        return CheckExecution.SUCCESS

    @property
    def completed(self):
        """bool: Has the check finished yet?
        """
        return self.finished_at is not None

    @property
    def duration(self):
        """int: How many seconds it took to run the check.
        """
        if self.completed:
            return (self.finished_at - self.started_at).total_seconds()

    def mark_as_started(self, save=True):
        """Mark the check as started.
        """
        self.started_at = timezone.now()
        if save:
            self.save()

    def mark_as_finished(self, fails_count):
        """Mark the check as finished.
        """
        self.fails_count = fails_count
        self.tasks_count = self.job.expectations.count()
        self.finished_at = timezone.now()
        self.save()
        self.job.last_execution_id = self.id
        self.job.save()


class CheckExpectationResult(models.Model):
    """The result of an expectation for a specific execution.
    """
    epoch = models.BigIntegerField(default=epoch_now)

    execution = models.ForeignKey(
        to=CheckExecution,
        on_delete=models.CASCADE,
        related_name='expectation_results',
    )

    expectation = models.ForeignKey(
        to=CheckExpectation,
        on_delete=models.CASCADE,
        related_name='+',
    )

    passed = models.BooleanField()

    expected_value = models.BigIntegerField(null=True)
    observed_value = models.BigIntegerField(null=True)

    class Meta:
        db_table = 'checks_expectationresult'


class CheckAlertRule(TimestampedModel):
    """Represents an alert that should be sent upon failure.
    """
    EMAIL = 'EMAIL'

    CHANNEL_CHOICES = (
        (EMAIL, 'Email'),
    )

    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='+',
    )

    job = models.ForeignKey(
        to=Check,
        on_delete=models.CASCADE,
        related_name='alert_rules',
    )

    name = models.CharField(max_length=255, null=False, blank=False)
    interval = models.DurationField(default=timedelta(hours=1))
    channel = models.CharField(max_length=15, choices=CHANNEL_CHOICES)
    channel_config = models.JSONField(default=dict)

    last_failure = models.ForeignKey(
        to='checks.CheckExecution',
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
    )

    class Meta:
        db_table = 'checks_alertrule'

    def __str__(self):
        return "%s/%s" % (self.job_id, self.channel)
