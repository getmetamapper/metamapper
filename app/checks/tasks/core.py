# -*- coding: utf-8 -*-
from django.db.models import Q, F
from django.db.models import DateTimeField, ExpressionWrapper
from django.db.models.functions import Now

from app.checks.emails import EmailAlert
from app.checks.models import Check, CheckAlertRule
from app.checks.models import CheckExecution
from app.checks.tasks.context import CheckContext
from app.checks.tasks.executor import CheckExecutor

from metamapper.celery import app
from utils import logging


__all__ = ['execute_check']


@app.task(bind=True)
@logging.task_logger(__name__)
def execute_check(self, check_id, epoch):
    """Execute check query and check it against expectations.
    """
    check = Check.objects.get(id=check_id)

    check_execution = check.executions.get(epoch=epoch)
    check_execution.mark_as_started()

    self.log.info(
        'Executing check: %s/%s' % (check.id, check_execution.epoch)
    )

    executor = CheckExecutor(check_execution)
    executor.execute(context=CheckContext(epoch, check.interval))

    dispatch_alerts.apply_async(args=[check.id, check_execution.epoch])


@app.task(bind=True)
@logging.task_logger(__name__)
def dispatch_alerts(self, check_id, epoch):
    """Handle alerts for an executed check if necessary.
    """
    check_execution = CheckExecution.objects.get(job_id=check_id, epoch=epoch)

    expectation_results = check_execution.expectation_results.order_by('epoch')
    failed_expectations = [a for a in expectation_results if not a.passed]

    # If no errors exist, then we do not need to send alerts.
    if not check_execution.error and not len(failed_expectations):
        return

    self.log.info(
        'Check has failed: %s/%s' % (check_id, epoch)
    )

    expressions = ExpressionWrapper(Now() - F('interval'), output_field=DateTimeField())
    alert_rules = (
        CheckAlertRule
        .objects
        .filter(job_id=check_id)
        .filter(Q(last_failure__isnull=True) | Q(last_failure__created_at__lte=expressions))
    )

    # If no alert rules are found, then we do not need to send alerts.
    if not len(alert_rules):
        return

    self.log.info(
        'Alerting on check: %s/%s' % (check_id, epoch)
    )

    check = Check.objects.get(id=check_id)
    check_alert_kwargs = {
        'check': check,
        'datastore': check.datastore,
        'workspace': check.workspace,
    }

    for alert_rule in alert_rules:
        alert = EmailAlert(alert_rule, **check_alert_kwargs)
        alert.deliver()

    check.alert_rules.update(last_failure=check_execution)
