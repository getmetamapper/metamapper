# flake8: noqa
from __future__ import absolute_import
from os import environ
from hashlib import sha1

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


def get_install_id():
    # We take an anonymized hash of the Django secret so we can
    # accurately report on the number of production installations of
    # Metamapper for usage purposes.
    return sha1(settings.SECRET_KEY.encode('utf-8')).hexdigest()


def get_version(prefix='v'):
    return "%s%s" % (prefix, __version__)


def is_docker():
    # One of these environment variables are guaranteed to exist
    # from our official docker images.
    return "METAMAPPER_VERSION" in environ or "METAMAPPER_IMAGE" in environ


__version__ = '0.4.0'

__all__ = ('app',)
