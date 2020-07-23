# flake8: noqa
from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
raise_import_exception = False

try:
    from .celery import app
except ImportError:
    raise_import_exception = True
    # If we can't import Django settings, then we aren't trying
    # to run the actual application. Which means we are just grabbing
    # the version.
    try:
        from django.conf import settings
    except ImportError:
        raise_import_exception = False

    if raise_import_exception:
        raise

__version__ = '0.1.1'
