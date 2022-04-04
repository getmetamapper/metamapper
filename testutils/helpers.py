# -*- coding: utf-8 -*-
import jwt

from calendar import timegm
from datetime import datetime
from faker import Faker

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from graphql_relay import to_global_id, from_global_id  # noqa: F401
from rest_framework.test import APIClient


faker = Faker()


def get_jwt(opts):
    jwt_now = timegm(datetime.utcnow().utctimetuple())
    payload = {
        'aud': settings.GRAPHQL_JWT['JWT_AUDIENCE'],
        'origIat': jwt_now,
        'exp': jwt_now + (60 * 15),
    }
    payload.update(opts)
    secret = settings.GRAPHQL_JWT['JWT_SECRET_KEY']
    return jwt.encode(payload, secret, algorithm='HS256').decode()


def graphql_headers(user, uuid=None):
    headers = {
        'HTTP_AUTHORIZATION': 'Bearer ' + get_jwt(opts={'email': user.email}),
    }
    if uuid:
        headers['HTTP_X_WORKSPACE_ID'] = uuid
    return headers


def graphql_client(user, uuid=None, authenticated=True):
    client = APIClient()
    if user and authenticated:
        headers = graphql_headers(user, uuid)
        client.credentials(**headers)
    return client


def api_headers(secret, uuid=None):
    headers = {
        'HTTP_AUTHORIZATION': 'Bearer %s' % secret,
    }
    if uuid:
        headers['HTTP_X_WORKSPACE_ID'] = uuid
    return headers


def api_client(secret, uuid=None, authenticated=True):
    client = APIClient()
    if secret and authenticated:
        headers = api_headers(secret, uuid)
        client.credentials(**headers)
    return client


def only(d, keys):
    return {k: v for k, v in d.items() if k in keys}


def without(d, keys):
    return {k: v for k, v in d.items() if k not in keys}


def get_content_type(model):
    return ContentType.objects.get(model=model)
