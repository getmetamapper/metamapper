"""
Django settings for metamapper project.
"""
import datetime as dt
import logging
import os
import sys

from corsheaders.defaults import default_headers
from distutils.util import strtobool
from django.core.management.utils import get_random_secret_key


def envtobool(name, default):
    value = os.getenv(name, default)
    if isinstance(value, (bool,)):
        return value
    try:
        return bool(strtobool(value))
    except ValueError:
        try:
            return bool(int(value))
        except ValueError:
            pass
    return default


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REACT_APP_DIR = os.path.join(BASE_DIR, 'www')

# Testing

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

if TESTING:
    logging.disable(logging.CRITICAL)

FIXTURE_DIRS = [
    os.path.join(BASE_DIR, 'testutils', 'fixtures'),
    os.path.join(BASE_DIR, 'www', 'cypress', 'fixtures'),
    os.path.join(BASE_DIR, 'app', 'revisioner', 'tests', 'fixtures'),
]

ENV = os.getenv('ENVIRONMENT', 'development')

DJANGO_ENV = ENV

CI = envtobool('CI', False)

SECRET_KEY = os.getenv('METAMAPPER_SECRET_KEY', default=get_random_secret_key())

DEBUG = DJANGO_ENV not in ('staging', 'production')

WEBSERVER_ORIGIN = os.getenv('METAMAPPER_WEBSERVER_ORIGIN', 'http://localhost:5000')

GRAPHQL_ORIGIN = os.getenv('METAMAPPER_GRAPHQL_ORIGIN', 'http://localhost:5000')

ALLOWED_HOSTS = ['*']

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True

CORS_ORIGIN_WHITELIST = (
    WEBSERVER_ORIGIN,
    GRAPHQL_ORIGIN,
)

CORS_ALLOW_HEADERS = default_headers + (
    'X-Workspace-Id',
)

# Application definition
VENDOR_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'graphene_django',
    'guardian',
    'ordered_model',
]

METAMAPPER_APPS = [
    'app.authentication.apps.Config',
    'app.authorization.apps.Config',
    'app.definitions.apps.Config',
    'app.comments.apps.Config',
    'app.customfields.apps.Config',
    'app.inspector.apps.Config',
    'app.healthchecks.apps.Config',
    'app.notifications.apps.Config',
    'app.omnisearch.apps.Config',
    'app.revisioner.apps.Config',
    'app.sso.apps.Config',
    'app.votes.apps.Config',
    'app.audit.apps.Config',
]

INSTALLED_APPS = VENDOR_APPS + METAMAPPER_APPS

AUTHENTICATION_MIDDLEWARE = os.getenv(
    'METAMAPPER_AUTHENTICATION_MIDDLEWARE',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    AUTHENTICATION_MIDDLEWARE,
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'metamapper.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'contrib', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'metamapper.wsgi.application'
#
# Beacon
#
# Collects aggregated (and anyonymous) usage data so we can improve the project. You can
# disable this globally or on a per-workspace basis.

METAMAPPER_BEACON_ACTIVATED = envtobool('METAMAPPER_BEACON', True)
#
# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('METAMAPPER_DB_NAME', 'metamapper'),
        'USER': os.getenv('METAMAPPER_DB_USER', 'postgres'),
        'PASSWORD': os.getenv('METAMAPPER_DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('METAMAPPER_DB_HOST', 'database'),
        'PORT': os.getenv('METAMAPPER_DB_PORT', 5432),
    }
}

INCLUDE_EXAMPLE_DATASTORES = envtobool('METAMAPPER_INCLUDE_EXAMPLE_DATASTORES', False)

# Used when hard resets on migrations during development.
DB_RESET = os.getenv('DB_RESET') or os.getenv('DB_SETUP')
#
# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_USER_MODEL = 'authentication.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'graphql_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
]
#
# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
#
# GraphQL / Graphene
# https://github.com/graphql-python/graphene-django

GRAPHENE = {
    'SCHEMA': 'metamapper.graphql.schema',
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
        'app.authentication.middleware.CurrentWorkspaceMiddleware',
    ],
    'RELAY_CONNECTION_MAX_LIMIT': 2000,
}

if DEBUG:
    GRAPHENE['MIDDLEWARE'].append('graphene_django.debug.DjangoDebugMiddleware')

GRAPHQL_JWT = {
    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_ALLOW_REFRESH': True,
    'JWT_AUDIENCE': WEBSERVER_ORIGIN,
    'JWT_LEEWAY': 30,
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_EXPIRATION_DELTA': dt.timedelta(hours=24),
    'JWT_REFRESH_EXPIRATION_DELTA': dt.timedelta(days=3),
}
#
# Static files (CSS, JavaScript, Images)
#
# We turn off all of these settings since Metamapper serves the compiled React assets
# via a custom view.

STATIC_HOST = ''

STATIC_URL = None

STATICFILES_DIRS = []

STATIC_ROOT = None

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
#
# Email
# https://docs.djangoproject.com/en/3.0/topics/email/

EMAIL_BACKEND = os.getenv('METAMAPPER_EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('METAMAPPER_EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('METAMAPPER_EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('METAMAPPER_EMAIL_PASSWORD')
EMAIL_PORT = os.getenv('METAMAPPER_EMAIL_PORT', 25)
EMAIL_USE_TLS = envtobool('METAMAPPER_EMAIL_USE_TLS', False)
EMAIL_USE_SSL = envtobool('METAMAPPER_EMAIL_USE_SSL', False)
EMAIL_DEFAULT_FROM = os.getenv('METAMAPPER_EMAIL_FROM_ADDRESS', 'friends@metamapper.io')
#
# Encryption
#
# Certain metastore fields are encrypted, such as password and SSH keys.

FERNET_KEYS = os.getenv('METAMAPPER_FERNET_KEY', '').split(',')
#
# Logging (https://docs.python.org/3/library/logging.html)

GRAPHQL_REQUEST_LOGGER = os.getenv(
    'METAMAPPER_GRAPHQL_REQUEST_LOGGER',
    'utils.logging.graphql.GraphqlRequestLogger',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[{asctime}] [{process:d}] [{lineno}] [{levelname}] [{name}] {message}',
            'style': '{',
        },
        'metamapper': {
            'format': '[{asctime}] [{process:d}] [{basename}:{linenum}] [{levelname}] [{name}] {message}',
            'style': '{',
        },
        'graphql': {
            'format': '[{asctime}] [{process:d}] [{levelname}] [{name}] {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'graphql_log_filter': {
            '()': 'utils.logging.filters.SuppressGraphqlErrorFilter',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'metamapper': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'metamapper',
        },
        'graphql': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'graphql',
        },
    },
    'loggers': {
        'app': {
            'handlers': ['metamapper'],
            'level': 'INFO',
            'propagate': False,
        },
        'metamapper': {
            'handlers': ['metamapper'],
            'level': 'INFO',
            'propagate': False,
        },
        'metamapper.graphql': {
            'handlers': ['graphql'],
            'level': 'INFO',
            'propagate': False,
        },
        'metamapper.commands': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'graphql.execution.utils': {
            'handlers': ['console'],
            'level': 'WARNING',
            'filters': ['graphql_log_filter'],
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery.beat': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'utils': {
            'handlers': ['metamapper'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}
#
# OAuth2 (optional)
#
# Metamapper supports three types of single sign-on: SAML 2.0 via any IdP
# and OAuth2 via Google and Github.
#
# To enable Google or Github SSO, we need to have the proper client and secret
# setup to communicate with the respective provider API.
#
# If the client and secret are not found, you will not be able to set up a
# SSO connection with that provider.

GITHUB_CLIENT_ID = os.getenv('METAMAPPER_GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('METAMAPPER_GITHUB_CLIENT_SECRET')
GITHUB_ENABLED = GITHUB_CLIENT_SECRET and GITHUB_CLIENT_SECRET

GOOGLE_CLIENT_ID = os.getenv('METAMAPPER_GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('METAMAPPER_GOOGLE_CLIENT_SECRET')
GOOGLE_ENABLED = GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
#
# Caching Layer (optional)
#
# Metmapper offers an optional caching layer using
# django-cacheops (https://github.com/Suor/django-cacheops). It uses redis
# as backend for ORM cache to speed up your queries.
#
CACHEOPS_REDIS = os.getenv('METAMAPPER_CACHEOPS_REDIS_URL')


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_db_cache',
    }
}

# If the CACHEOPS_REDIS variable isn't set, we assume you don't want
# the cache, so we disable it.
if CACHEOPS_REDIS:
    CACHEOPS = {
        'authentication.user': {
            'ops': 'get', 'timeout': 60 * 15,
        },
        'authentication.workspace': {
            'ops': 'get', 'timeout': 60 * 15,
        },
        'definitions.*': {
            'ops': {'fetch', 'get'}, 'timeout': 60 * 30,
        },
        'revisioner.*': {
            'ops': {'fetch', 'get'}, 'timeout': 60 * 15,
        },
        'comments.comment': {
            'ops': {'fetch', 'get'}, 'timeout': 60 * 15,
        },
    }
#
# Search
#
# Metamapper supports searching on some of the database objects it indexes. We default
# to using Elasticsearch, though have plans to roll out Solr as an option at some point.
#
SEARCH_BACKEND = os.getenv(
    'METAMAPPER_SEARCH_BACKEND',
    'app.omnisearch.backends.elastic_backend.ElasticBackend',
)

ELASTIC_URL = os.getenv(
    'METAMAPPER_ELASTIC_URL',
    'http://elastic:9200',
)

# This can be overridden via the settings.py file in your fork.
ELASTIC_CLIENT_KWARGS = {
    'sniff_on_start': True,
    'sniff_on_connection_fail': True,
    'sniffer_timeout': 60,
}

#
# Django Storages (required)
# (https://django-storages.readthedocs.io/en/1.9.1/index.html)
#
# Metamapper stores persists objects (e.g., schema crawls) in blob storage.
#
# Currently, we use the default FileSystemStorage backend for local testing purposes.
#
DEFAULT_FILE_STORAGE = os.getenv(
    'METAMAPPER_FILE_STORAGE_BACKEND',
    'django.core.files.storage.FileSystemStorage',
)

FILE_STORAGE_BUCKET = os.getenv('METAMAPPER_FILE_STORAGE_BUCKET')

MEDIA_ROOT = os.getenv('METAMAPPER_MEDIA_ROOT', 'uploads/')
#
# AWS S3 Configuration
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
#
# We recommend using a service role if possible to access AWS. However,
# we do support IAM key/secret pairs if necessary.
#

AWS_STORAGE_BUCKET_NAME = FILE_STORAGE_BUCKET

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')

AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

AWS_DEFAULT_ACL = os.getenv('METAMAPPER_FILE_STORAGE_BUCKET_ACL', 'private')

AWS_S3_FILE_OVERWRITE = True
#
# Google Cloud Storage Configuration
# https://django-storages.readthedocs.io/en/latest/backends/gcloud.html
#
# You can use GCP instead of S3. We authenticate via service account permissions
# and a key available to your Metamappeer instance via GOOGLE_APPLICATION_CREDENTIALS.
#

GS_BUCKET_NAME = FILE_STORAGE_BUCKET

GS_DEFAULT_ACL = os.getenv('METAMAPPER_FILE_STORAGE_BUCKET_ACL', 'private')

GS_FILE_OVERWRITE = True
#
# Override Metamapper settings.py configuration
# https://code.djangoproject.com/wiki/SplitSettings
#
# You can reference a Python file to override any of the constants in this file. The
# provided file must be discoverable via the PYTHONPATH.
#

OVERRIDE_MODULE_PATH = os.getenv('METAMAPPER_SETTINGS_OVERRIDE_MODULE')

if OVERRIDE_MODULE_PATH:
    config_module = __import__(OVERRIDE_MODULE_PATH, globals(), locals(), 'metamapper')

    for setting in dir(config_module):
        if setting == setting.upper():
            locals()[setting] = getattr(config_module, setting)
