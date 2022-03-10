# -*- coding: utf-8 -*-
import datetime as dt
import factory
import random
import hashlib

from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.hashers import make_password
from django.contrib.contenttypes.models import ContentType

import app.authentication.models as authentication_models
import app.authorization.models as authorization_models
import app.comments.models as comment_models
import app.sso.models as sso_models
import app.customfields.models as customfields_models
import app.definitions.models as definition_models
import app.revisioner.models as revisioner_models
import app.votes.models as vote_models


def x509cert(instance=None):
    return """
-----BEGIN CERTIFICATE-----
MIIDCzCCAfOgAwIBAgIJZC/zKbXIzEkcMA0GCSqGSIb3DQEBCwUAMCMxITAfBgNV
BAMTGG1ldGFtYXBwZXItZGV2LmF1dGgwLmNvbTAeFw0xOTAyMTUwMzUwNDFaFw0z
MjEwMjQwMzUwNDFaMCMxITAfBgNVBAMTGG1ldGFtYXBwZXItZGV2LmF1dGgwLmNv
bTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMOUfc2AWAJN7Fv+wZ+R
+9CLN3ewimd++0TqV2wIo72Ud/PKM03kfODkWxKwqCHw6j2YZWugbjtmvS7pm/93
k3PyyjuOybBawd5IiMw8XAVFvTRmkREl26bwuHFOwWFv7DHpTjbs4cgxm++2Jcx1
7DgrRIJUpOKjwpFs+kGnlWReTNseF7RAhDTe/7BcArYGdrwVE3nafbGluiZBtjti
dD7J1YxnRPep0GaezjRtI6ygxliKDUU3iBwR4k8uCEj3XFjN+UutwgK318SFU2B0
rXb1UmIhtpV7ePxYmEKh9A+H8xFclGfiMd1FFQ4eH1PfAOM1ljIzDsKhNJUNnR0P
X80CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUtszg6c0bozrL
T/cZiqU62gfjwWwwDgYDVR0PAQH/BAQDAgKEMA0GCSqGSIb3DQEBCwUAA4IBAQA0
+l+P419AOY88ZFjXhjXM9S0d+4hIKLAg9Yb7tfPs8l4lIEGQnWxvO3XrrPeKfzwf
mH1H178gs08xsvZvamQVzMMGjwipOosftxPzpm1xmqVP24tXi7YMbSzIjXzuqCIC
XuFYaddZm8A+ToZ7tt91uGoXeR6AvSKgYyt0bncgSCYeTkVUuHji3Jq49TfPYvni
zRUvCAe7TGKcrEyolRTlYN+fVFSRLbyv8PryAun9mkMAxb/PnmesajqyEG82oaRr
bDHfQIPd6BoOTXRyGJD0Ys+SK/GyV4+yykCeAY31kRxnQPZuxVBkgolQxIFa5CSy
8XfmMm8dVx3C2RByNCPJ
-----END CERTIFICATE-----
    """


def allTags(instance=None):
    choices = [
        'accounting',
        'analytics',
        'billing',
        'data',
        'devops',
        'humanresources',
        'marketing',
        'product',
        'sales',
        'success',
        'development',
        'engineering',
        'outbound',
        'inbound',
        'equity',
    ]
    return list({
        random.choice(choices)
        for i in range(random.randint(5, 10))
    })


def allDataTypes(instance):
    choices = [
        'array',
        'bigint',
        'boolean',
        'character varying',
        'date',
        'datetime',
        'double precision',
        'inet',
        'integer',
        'interval',
        'json',
        'real',
        'smallint',
        'text',
        'timestamp',
        'timestamp with time zone',
        'timestamp without time zone',
    ]
    return random.choice(choices)


def underscoreObject(instance):
    """Create an underscore domain_word version.
    """
    return "_".join(factory.Faker('domain_word').generate().split("-")) + str(random.randint(5, 1500))


def domainWord(instance):
    """Create an unique domain name.
    """
    return factory.Faker('domain_word').generate() + str(random.randint(5, 1500))


def domain(instance):
    """Create an unique domain name.
    """
    domain_wrd = domainWord(instance)
    domain_end = random.choice(["com", "org", "gov", "io", "co", "net", "edu"])
    return ".".join([domain_wrd, domain_end])


def randomContentType(instance):
    """Get a random content type object.
    """
    return ContentType.objects.get_for_model(random.choice([
        definition_models.Datastore,
        definition_models.Table,
    ]))


def hash(*args):
    return hashlib.md5(''.join(map(str, args)).encode()).hexdigest()


class UserFactory(factory.django.DjangoModelFactory):
    fname = factory.Faker('first_name')
    lname = factory.Faker('last_name')
    email = factory.Faker('email')
    password = make_password('password1234')

    class Meta:
        model = authentication_models.User


class WorkspaceFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('company')
    slug = factory.LazyAttribute(lambda i: slugify(i.name))
    creator = factory.LazyAttribute(lambda i: UserFactory())

    class Meta:
        model = authentication_models.Workspace


class GroupFactory(factory.django.DjangoModelFactory):
    workspace = factory.LazyAttribute(lambda i: WorkspaceFactory())

    name = factory.Faker('company')
    description = factory.Faker('text', max_nb_chars=25)

    class Meta:
        model = authorization_models.Group


class DatastoreFactory(factory.django.DjangoModelFactory):
    workspace = factory.LazyAttribute(lambda i: WorkspaceFactory())

    name = factory.Faker('company')
    tags = factory.LazyAttribute(allTags)

    version = '9.6.11'

    engine = factory.LazyAttribute(lambda i: random.choice(definition_models.Datastore.ENGINE_CHOICES)[0])
    host = factory.Faker('hostname')
    username = factory.Faker('user_name')
    password = factory.Faker('sha1')
    port = factory.LazyAttribute(lambda i: random.randint(1, 65535))
    database = factory.Faker('domain_word')

    object_permissions_enabled = False

    class Meta:
        model = definition_models.Datastore


class SchemaFactory(factory.django.DjangoModelFactory):
    datastore = factory.LazyAttribute(lambda i: DatastoreFactory())
    workspace = factory.LazyAttribute(lambda i: i.datastore.workspace)

    name = factory.LazyAttribute(underscoreObject)
    tags = factory.LazyAttribute(allTags)

    object_id = factory.LazyAttribute(lambda i: hash(i.datastore.id, i.name))

    class Meta:
        model = definition_models.Schema


class TableFactory(factory.django.DjangoModelFactory):
    schema = factory.LazyAttribute(lambda i: SchemaFactory())
    workspace = factory.LazyAttribute(lambda i: i.schema.workspace)
    kind = 'TABLE'
    custom_properties = {}

    name = factory.LazyAttribute(underscoreObject)
    tags = factory.LazyAttribute(allTags)
    object_id = factory.LazyAttribute(lambda i: hash(i.schema.object_id, i.name))

    class Meta:
        model = definition_models.Table


class ColumnFactory(factory.django.DjangoModelFactory):
    table = factory.LazyAttribute(lambda i: TableFactory())
    workspace = factory.LazyAttribute(lambda i: i.table.workspace)

    name = factory.LazyAttribute(underscoreObject)
    ordinal_position = random.randint(1, 10)
    data_type = factory.LazyAttribute(allDataTypes)
    max_length = None
    numeric_scale = None
    is_nullable = factory.Faker('pybool')
    is_primary = False
    default_value = ''
    db_comment = factory.Faker('sentence')

    object_id = factory.LazyAttribute(lambda i: hash(i.table.object_id, i.name))

    class Meta:
        model = definition_models.Column


class RevisionerRunFactory(factory.django.DjangoModelFactory):
    datastore = factory.LazyAttribute(lambda i: DatastoreFactory())
    workspace = factory.LazyAttribute(lambda i: i.datastore.workspace)

    started_at = factory.LazyAttribute(lambda i: timezone.now())
    created_at = factory.LazyAttribute(lambda i: (
        i.started_at - dt.timedelta(days=i.datastore.run_history.count())
    ))

    finished_at = factory.LazyAttribute(
        lambda i: i.started_at + dt.timedelta(seconds=random.randint(60, (60 * 60 * 30)))
    )

    class Meta:
        model = revisioner_models.Run


class CustomFieldFactory(factory.django.DjangoModelFactory):
    workspace = factory.LazyAttribute(lambda i: WorkspaceFactory())
    content_type = factory.LazyAttribute(randomContentType)

    field_name = factory.LazyAttribute(domainWord)
    field_type = factory.LazyAttribute(lambda i: random.choice(customfields_models.CustomField.FIELD_TYPE_CHOICES)[0])
    short_desc = factory.Faker('sentence', nb_words=3)

    class Meta:
        model = customfields_models.CustomField


class CommentFactory(factory.django.DjangoModelFactory):
    content_object = factory.LazyAttribute(lambda i: TableFactory())
    workspace_id = factory.LazyAttribute(lambda i: i.content_object.workspace_id)
    parent_id = None

    html = factory.Faker('sentence', nb_words=3)
    author = factory.LazyAttribute(lambda i: UserFactory())

    class Meta:
        model = comment_models.Comment


class VoteFactory(factory.django.DjangoModelFactory):
    content_object = factory.LazyAttribute(lambda i: CommentFactory())
    workspace_id = factory.LazyAttribute(lambda i: i.content_object.workspace_id)
    action = vote_models.Vote.UP
    user = factory.LazyAttribute(lambda i: UserFactory())

    class Meta:
        model = vote_models.Vote


class SSOConnectionFactory(factory.django.DjangoModelFactory):
    provider = sso_models.SSOConnection.GENERIC
    workspace = factory.LazyAttribute(lambda i: WorkspaceFactory())
    entity_id = 'urn:auth0:metamapper'
    sso_url = factory.Faker('uri')
    x509cert = factory.LazyAttribute(x509cert)
    extras = {
        'mappings': {
            'user_id': 'identifier',
            'user_email': 'user_email',
            'fname': 'first_name',
            'lname': 'last_name',
        },
    }

    class Meta:
        model = sso_models.SSOConnection


class SSODomainFactory(factory.django.DjangoModelFactory):
    workspace = factory.LazyAttribute(lambda i: WorkspaceFactory())
    domain = factory.LazyAttribute(domain)

    class Meta:
        model = sso_models.SSODomain
