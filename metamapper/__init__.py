# flake8: noqa
from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
import_failed = False

try:
    from .celery import app
except ImportError:
    try:
        from django.conf import settings
    except ImportError:
        import_failed = True

    if import_failed:
        raise

__version__ = '0.1.0'
