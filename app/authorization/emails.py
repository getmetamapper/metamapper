# -*- coding: utf-8 -*-
import app.authentication.models as models
import app.notifications.tasks as email


def membership_granted(to_email, workspace, permissions):
    """Alert a user that they have been added/promoted to a workspace.
    """
    permissions = permissions.lower().capitalize()
    user_exists = models.User.objects.filter(email__iexact=to_email).exists()

    mailer_kwargs = {
        'namespace': 'authorization',
        'template': 'membership_granted',
        'subject': 'You have granted the {0} role to the {1} workspace'.format(permissions, workspace.name),
        'to_email': to_email,
        'template_dict': {
            'to_address': to_email,
            'workspace_name': workspace.name,
            'user_exists': user_exists,
            'permissions': permissions,
        }
    }

    email.log.info(
        'Attempting to deliver email({template}) to {to_email}'.format(**mailer_kwargs)
    )

    email.deliver.delay(**mailer_kwargs)


def membership_revoked(to_email, workspace):
    """Alert a user that they have been removed/demoted from a workspace.
    """
    mailer_kwargs = {
        'namespace': 'authorization',
        'template': 'membership_revoked',
        'subject': 'You have been removed from the {0} workspace'.format(workspace.name),
        'to_email': to_email,
        'template_dict': {
            'to_address': to_email,
            'workspace_name': workspace.name,
        }
    }

    email.log.info(
        'Attempting to deliver email({template}) to {to_email}'.format(**mailer_kwargs)
    )

    email.deliver.delay(**mailer_kwargs)
