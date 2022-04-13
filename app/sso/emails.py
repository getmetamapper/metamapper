# -*- coding: utf-8 -*-
import app.notifications.tasks as email


def domain_verification_succeeded(to_email, domain):
    """Email to be sent when domain verification succeeds.
    """
    mailer_kwargs = {
        'namespace': 'sso',
        'template': 'domain_verification_succeeded',
        'subject': 'tbd',
        'to_email': to_email,
        'template_dict': {
            'domain': domain,
        }
    }

    email.log.info(
        'Attempting to deliver email({template}) to {to_email}'.format(**mailer_kwargs)
    )

    email.deliver.delay(**mailer_kwargs)


def domain_verification_failed(to_email, domain):
    """Email to be sent when domain verification fails.
    """
    mailer_kwargs = {
        'namespace': 'sso',
        'template': 'domain_verification_failed',
        'subject': 'tbd',
        'to_email': to_email,
        'template_dict': {
            'domain': domain,
        }
    }

    email.log.info(
        'Attempting to deliver email({template}) to {to_email}'.format(**mailer_kwargs)
    )

    email.deliver.delay(**mailer_kwargs)
