# -*- coding: utf-8 -*-
import app.notifications.tasks as email


def datastore_sync_failure(to_email, workspace, datastore):
    """Delivered when a datastore fails to sync properly.
    """
    mailer_kwargs = {
        'namespace': 'definitions',
        'template': 'datastore_sync_failure',
        'subject': 'Sync failed for your "%s" datastore in %s' % (datastore.name, workspace.slug),
        'to_email': to_email,
        'template_dict': {
            'datastore_name': datastore.name,
            'datastore_slug': datastore.slug,
            'workspace_slug': workspace.slug,
        }
    }

    email.log.info(
        'Attempting to deliver email({template}) to {to_email}'.format(**mailer_kwargs)
    )

    email.deliver.delay(**mailer_kwargs)
