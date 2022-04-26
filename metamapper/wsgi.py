"""
WSGI config for metamapper project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""
import os

from django.core.wsgi import get_wsgi_application
from django.db.models import JSONField
from graphene_django.converter import convert_django_field
from graphene import String


@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return String()


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'metamapper.settings')

application = get_wsgi_application()
