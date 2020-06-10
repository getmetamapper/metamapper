# -*- coding: utf-8 -*-
import utils.email as email


def domain_verification_succeeded(to_email, domain):
    """TBD
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

    email.deliver.delay(**mailer_kwargs)


def domain_verification_failed(to_email, domain):
    """TBD
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

    email.deliver.delay(**mailer_kwargs)
