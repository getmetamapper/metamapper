# -*- coding: utf-8 -*-
import app.notifications.tasks as email


def reset_password(to_email, uid, token):
    """Deliver instructions to reset your password.
    """
    mailer_kwargs = {
        'namespace': 'authentication',
        'template': 'reset_password',
        'subject': 'Here\'s a link to reset your password',
        'to_email': to_email,
        'template_dict': {
            'email': to_email,
            'token': token,
            'uid': uid,
        }
    }

    email.log.info(
        'Attempting to deliver email({template}) to {to_email}'.format(**mailer_kwargs)
    )

    email.deliver.delay(**mailer_kwargs)


def password_was_reset(to_email):
    """Alert a user that their password has been reset.
    """
    mailer_kwargs = {
        'namespace': 'authentication',
        'template': 'password_was_reset',
        'subject': 'Your Metamapper password was changed',
        'to_email': to_email,
        'template_dict': {
            'to_address': to_email,
        }
    }

    email.log.info(
        'Attempting to deliver email({template}) to {to_email}'.format(**mailer_kwargs)
    )

    email.deliver.delay(**mailer_kwargs)
