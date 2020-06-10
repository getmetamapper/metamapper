# -*- coding: utf-8 -*-
import datetime as dt
import dns.resolver as dns

import utils.logging as logging

from django.db.models import Q, ExpressionWrapper, DateTimeField
from django.db.models.expressions import RawSQL
from django.db.models.functions import Now

from metamapper.celery import app

from app.sso.models import SSODomain


@app.task(bind=True)
@logging.task_logger(__name__)
def queue_domain_verifications(self, *arg, **kwargs):
    """Scheduled task to queue domains that need to be verified.
    """
    next_attempt_at = ExpressionWrapper(
        RawSQL("last_attempted_at + INTERVAL '1 hour' * POW(attempts, 1.5)", []),
        output_field=DateTimeField()
    )
    sso_domains = SSODomain.objects.annotate(next_attempt_at=next_attempt_at)
    sso_domains = sso_domains.filter(attempts__lte=SSODomain.MAX_ATTEMPTS)
    sso_domains = sso_domains.filter(
        Q(next_attempt_at__gte=Now()) | Q(last_attempted_at__isnull=True)
    )
    self.log.info(
        'Found {0} domains'.format(len(sso_domains))
    )
    for sso_domain in sso_domains:
        self.log.info(
            'Queueing {0} for verification'.format(sso_domain)
        )
        verify_domain.apply_async(args=(sso_domain.domain,))


@app.task(bind=True)
@logging.task_logger(__name__)
def verify_domain(self, domain, *arg, **kwargs):
    """Check TXT records to verify a domain.
    """
    try:
        instance = SSODomain.objects.get(domain__iexact=domain)
    except SSODomain.DoesNotExist:
        self.log.info(
            'Domain ({0}) could not be found.'.format(domain)
        )
        return None

    txt_records = dns.query(instance.domain, 'TXT')

    self.log.info(
        'Found {0} TXT records for {1}'.format(len(txt_records), domain)
    )

    for txt in txt_records:
        is_verified = instance.verify_TXT_record(txt.to_text())

        if is_verified:
            break

    if is_verified:
        instance.mark_as_verified()
        self.log.info(
            '{0} has been verified.'.format(instance)
        )
    else:
        instance.mark_as_failed()
        self.log.info(
            '{0} could not be verified (attempt: {1}).'.format(instance, instance.attempts)
        )


@app.task(bind=True)
@logging.task_logger(__name__)
def delete_failed_domains(self, *arg, **kwargs):
    """We should remove domains that have been failed for 72 hours.
    """
    sso_domains = (
        SSODomain.objects
                 .filter(attempts__gt=SSODomain.MAX_ATTEMPTS)
                 .filter(last_attempted_at__lt=Now() - dt.timedelta(hours=72))
    )

    self.log.info(
        'Removing {0} failed domains'.format(len(sso_domains))
    )

    sso_domains.delete()
