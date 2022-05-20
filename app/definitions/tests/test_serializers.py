# -*- coding: utf-8 -*-
import copy
import collections
import random
import unittest.mock as mock

import app.definitions.models as models
import app.definitions.serializers as serializers

import app.inspector.service as inspector

import testutils.cases as cases
import testutils.factories as factories
import testutils.helpers as helpers

from guardian.core import ObjectPermissionChecker


GOOGLE_PRIVATE_KEY = """
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDJBZeuYY/snVso
Kkhg3nGz9N5PyDP2qGoa6wECcy3KUYYICZ230pCpN09sWnMtQn//GDFGyxL442SH
kDtZuhrB++b+F1rhrNLWynw8cQGG8FQxlZdIHk+i1h3ajsqGB07f0VqqqErt01X5
nLeczu1iBWG5gC82F+hXQaFqQuyfyy+lVZby6pX+/Vkx9ArYo1tJ/GqpF5VV9zmB
A9i7hR+bf3/tzjWbTHxyVW8kK3pvfRvIg+53/vUr1St+RkoboNczLOv7xkqJuPzw
88UYNrTqw9XhUyj6JV8k51OgHuhOIzKh4XsLJKC80qG5GUKLHXt/VXt63YI4TGoU
SAWrXr8rAgMBAAECggEAINkGGRueHgb0f1KxcwrGP6aysQzA2PxaIj3mc1UI1XeO
1D9mA0SoGM6N7uG00l98dN2qJ6xFVGAr7C74U8giWTJlY33Dfv7zkN+Tf3jjy/33
dAbCqqkxUCV2yWDt3QrSq6YVD6/iVoxjDx+5rSjvB0Zj2qEEle1ALQnva2K2McIC
sa1arcUdD7konF1s8Hz8tfTfL+3QQiY6PAfRFO6djRtMBvEbsKMZvw+L8OX2lCyl
6n1wkV64uelY9j6qa/0ufaGC9YH/b2Cz4PvLkqkYlhZ3wLZ5SS8dIltgQZOBGdkg
w0syv3/t3CviTqyer0A5gpbNh3YxX/+/K2ek/JrCAQKBgQDu06BTABCSxlQy+3wV
A2Jh19JT2iEvoeEhkPDed6M7FBzqiVsg23BmRmHth9vdud9Ks7iMPWBcUtuMWpTq
uL6RTVM+yCcBVTmgimLIyAISnz61O07t8mVe/a/n4pXn6MxPITAThdDswkTcQrvX
fD5nu+fKNA2B9OkO+on/34hcKwKBgQDXegv8Fjx1OpFhLJhL8PxKS2BZrQRmtVd3
AJdiqjQdYcMV2lKOEvV9FFNwAXrSOs93K7YC2iGqpElTCQYNcp94fE8h27M/g7c+
t83DViRZQqyAymUL36bMB1zXdUB1C2EChX+0Ygz7qvSyA58+jMIJxodXASjcO86p
dTtMz/qpAQKBgQCtgzdR1hQ0br8xoyCNK75Ik8KNhUbjEls8Rc+Z8ZW4EG7Jvy1j
+8n3pF71ceU9fBNMdLI5wUXHDbPQjubueXaKnoFCdaxQ/Zg2mRQYB6fp26R1izdX
DOq1Tt6EPEzpBmuZeeUx6eDWgnYBCMLsVaoJN625bIP7zPGeHkwwiDjLrQKBgGId
zutA7NKskppfBhI+b4MdA4iSAhkKpgMoH8brncNrSrveqAzNkT8dTEkKQ3ULFoE7
RCvUS9Q57rGCwGDLOtZQNHBEbECVp5FFfMpfpTmH5KjYgF6Bvp/VEm+BkpI5Vjkh
tN7cbvECDV4pzA9dZNWystnpS0PNb/M10ITPh2IBAoGAS8l+aUYNWrLZCWr57jpp
1hUbqf3bN6Bkb/w8rpzaw8xkFf2/QKcxbYS0xeU3wiB13Gc7yI5TorB270AVztq0
38OOH58OBastUF3j1iz56EZTXDvb5jt6akbsldFvhoK3/kGtDqNMEZ2Ot7Nb425R
cGP0wsmwCkfybKi2a+C5h0g=
-----END PRIVATE KEY-----
"""

GOOGLE_SERVICE_ACCOUNT_INFO = {
    'type': 'service_account',
    'project_id': 'metamapper',
    'private_key_id': '4111c3e576f24cc5ab4fcfa5c96c2d32',
    'private_key': GOOGLE_PRIVATE_KEY,
    'client_email': 'metamapper@metamapper.iam.gserviceaccount.com',
    'client_id': '7c74ff6d3a454cd4bc60108d35177d62',
    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
    'token_uri': 'https://oauth2.googleapis.com/token',
    'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
    'client_x509_cert_url': (
        'https://www.googleapis.com/robot/v1/metadata/x509/metamapper@metamapper.iam.gserviceaccount.com'
    ),
}


class DatastoreSerializerCreateTests(cases.SerializerTestCase):
    """Test cases for the Datastore serializer class.
    """
    factory = factories.DatastoreFactory

    serializer_class = serializers.DatastoreSerializer

    serializer_resource_name = 'Datastore'

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.user = factories.UserFactory()
        cls.workspace.grant_membership(cls.user, 'MEMBER')

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'name': 'Product Database',
            'engine': random.choice(['sqlserver', 'oracle', 'mysql']),
            'username': 'admin',
            'password': 'password1234',
            'database': 'product_db',
            'host': 'web-86.cortez.net',
            'port': 5439,
        }
        attributes.update(**overrides)
        return attributes

    @mock.patch('app.revisioner.tasks.v1.core.start_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_when_valid_hostname(self, verify_connection, mock_run):
        """It should be able to create the resource.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        instance = serializer.save(workspace=self.workspace, creator=self.user)
        self.assertTrue(self.user.has_perm('view_datastore', instance))
        self.assertTrue(instance.incident_contacts == [self.user.email])

    @mock.patch('app.revisioner.tasks.v1.core.start_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_when_valid_ip_address(self, verify_connection, mock_run):
        """It should be able to create the resource.
        """
        attributes = self._get_attributes(host='54.32.11.00')
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        instance = serializer.save(workspace=self.workspace, creator=self.user)
        self.assertTrue(self.user.has_perm('view_datastore', instance))

    @mock.patch('app.revisioner.tasks.v1.core.start_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_when_name_invalid(self, verify_connection, mock_run):
        """It should be invalid if the name is null.
        """
        attributes = self._get_attributes(name=None)
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'code': 'nulled',
                'field': 'name',
                'resource': 'Datastore',
            }
        ])

    @mock.patch('app.revisioner.tasks.v1.core.start_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_when_host_invalid(self, verify_connection, mock_run):
        """It should be invalid if the host has spaces, etc.
        """
        attributes = self._get_attributes(host='not a valid host')
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'Datastore',
                'field': 'host',
                'code': 'invalid',
            }
        ])

    @mock.patch('app.revisioner.tasks.v1.core.start_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_when_port_out_of_range(self, verify_connection, mock_run):
        """It should be invalid if the port is larger than 65535.
        """
        attributes = self._get_attributes(port=70000)
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'Datastore',
                'field': 'port',
                'code': 'max_value',
            }
        ])

    @mock.patch('app.revisioner.tasks.v1.core.start_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_when_port_negative(self, verify_connection, mock_run):
        """It should be invalid if the port is less than 1.
        """
        attributes = self._get_attributes(port=-50)
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'Datastore',
                'field': 'port',
                'code': 'min_value',
            }
        ])

    @mock.patch('app.revisioner.tasks.v1.core.start_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_when_duplicate_tags(self, verify_connection, mock_run):
        """It should automatically de-duplicate tags.
        """
        attributes = self._get_attributes(tags=['red', 'red', 'blue'])
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())

        instance = serializer.save(workspace=self.workspace, creator=self.user)

        self.assertEqual(set(instance.tags), {'red', 'blue'})

    @mock.patch('app.revisioner.tasks.v1.core.start_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_invalid_ssh_information(self, verify_connection, mock_run):
        """It should be able to create the resource.
        """
        extras = {
            'ssh_enabled': True,
            'ssh_host': 'ec2.dns.com',
            'ssh_user': 'scott',
            'ssh_port': 22,
        }

        attributes = self._get_attributes(**extras)
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'Datastore',
                'field': 'ssh_host',
                'code': 'invalid',
            }
        ])

    @mock.patch('app.revisioner.tasks.v1.core.start_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_partial_ssh_information(self, verify_connection, mock_run):
        """If we need SSH information, we need all 3 fields.
        """
        extras = {
            'ssh_enabled': True,
            'ssh_host': '54.32.11.12',
            'ssh_user': 'scott',
        }

        attributes = self._get_attributes(**extras)
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'Datastore',
                'field': 'ssh',
                'code': 'invalid',
            }
        ])

    @mock.patch('app.revisioner.tasks.v1.core.start_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_entire_ssh_information(self, verify_connection, mock_run):
        """It should be able to create the resource.
        """
        extras = {
            'ssh_enabled': True,
            'ssh_host': '54.32.11.11',
            'ssh_user': 'scott',
            'ssh_port': 22,
        }

        attributes = self._get_attributes(**extras)
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())

        instance = serializer.save(workspace=self.workspace, creator=self.user)

        self.assertEqual(instance.ssh_host, extras['ssh_host'])
        self.assertEqual(instance.ssh_user, extras['ssh_user'])
        self.assertEqual(instance.ssh_port, extras['ssh_port'])

    @mock.patch('app.revisioner.tasks.v1.core.start_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_google_bigquery_valid(self, verify_connection, mock_run):
        """It should be able to create the resource.
        """
        extras = {
            'engine': models.Datastore.BIGQUERY,
            'extras': {
                'credentials': GOOGLE_SERVICE_ACCOUNT_INFO,
                'invalid': 'this_will_be_stripped_off',
            },
        }

        attributes = self._get_attributes(**extras)
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        instance = serializer.save(workspace=self.workspace, creator=self.user)

        self.assertEqual(instance.host, 'bigquery.googleapis.com')
        self.assertEqual(instance.username, 'googleapis')
        self.assertEqual(instance.port, 443)
        self.assertEqual(list(instance.extras.keys()), ['credentials'])
        self.assertEqual(instance.extras['credentials'], extras['extras']['credentials'])

    @mock.patch('app.revisioner.tasks.v1.core.start_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_google_bigquery_invalid(self, verify_connection, mock_run):
        """It should be able to create the resource.
        """
        extras = {
            'engine': models.Datastore.BIGQUERY,
            'extras': {
                'credentials': None,
            },
        }

        attributes = self._get_attributes(**extras)
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {'code': 'invalid', 'field': 'extras', 'resource': 'Datastore'}
        ])

    @mock.patch('app.revisioner.tasks.v1.core.start_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_aws_athena_valid(self, verify_connection, mock_run):
        """It should be able to create the resource.
        """
        extras = {
            'engine': models.Datastore.ATHENA,
            'extras': {
                'role': 'arn:aws:iam::123456789012:role/default',
                'region': 'us-west-2',
                'invalid': 'this_will_be_stripped_off',
            },
        }

        attributes = self._get_attributes(**extras)
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        instance = serializer.save(workspace=self.workspace, creator=self.user)
        self.assertEqual(instance.host, 'api.amazonaws.com')
        self.assertEqual(instance.username, 'amazonapis')
        self.assertEqual(instance.port, 443)
        self.assertEqual(list(instance.extras.keys()), ['role', 'region'])
        self.assertEqual(instance.extras['role'], extras['extras']['role'])
        self.assertEqual(instance.extras['region'], extras['extras']['region'])

    @mock.patch('app.revisioner.tasks.v1.core.start_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_aws_athena_invalid(self, verify_connection, mock_run):
        """It should be able to create the resource.
        """
        extras = {
            'engine': models.Datastore.ATHENA,
            'extras': {
                'role': 'arn:aws:iam::123456789012:role/default',
            },
        }

        attributes = self._get_attributes(**extras)
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {'code': 'invalid', 'field': 'extras', 'resource': 'Datastore'}
        ])

    @mock.patch('app.revisioner.tasks.v1.core.start_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_hive_valid(self, verify_connection, mock_run):
        """It should be able to create the resource.
        """
        extras = {
            'engine': models.Datastore.HIVE,
            'extras': {
                'dialect': models.Datastore.POSTGRESQL,
                'invalid': 'this_will_be_stripped_off',
            },
        }

        attributes = self._get_attributes(**extras)
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())

        instance = serializer.save(workspace=self.workspace, creator=self.user)

        self.assertEqual(list(instance.extras.keys()), ['dialect'])
        self.assertEqual(instance.extras['dialect'], extras['extras']['dialect'])

    @mock.patch('app.revisioner.tasks.v1.core.start_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_hive_invalid_dialect(self, verify_connection, mock_run):
        """It should be able to create the resource.
        """
        extras = {
            'engine': models.Datastore.HIVE,
            'extras': {
                'dialect': models.Datastore.BIGQUERY,
            },
        }

        attributes = self._get_attributes(**extras)
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {'code': 'invalid', 'field': 'extras', 'resource': 'Datastore'}
        ])

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        test_case_dict = {
            'engine': [
                {'code': 'nulled', 'value': None},
                {'code': 'invalid_choice', 'value': 'AS/400'},
            ],
            'username': [
                {'code': 'blank', 'value': ''},
                {'code': 'nulled', 'value': None},
            ],
            'password': [
                {'code': 'blank', 'value': ''},
                {'code': 'nulled', 'value': None},
            ],
            'database': [
                {'code': 'blank', 'value': ''},
                {'code': 'nulled', 'value': None},
            ],
            'host': [
                {'code': 'blank', 'value': ''},
                {'code': 'nulled', 'value': None},
            ],
            'port': [
                {'code': 'invalid', 'value': ''},
                {'code': 'nulled', 'value': None},
                {'code': 'min_value', 'value': -10},
                {'code': 'max_value', 'value': 70000},
            ],
            'ssh_host': [
                {'code': 'invalid', 'value': 'not an ip address'},
            ],
            'ssh_user': [
                {'code': 'max_length', 'value': helpers.faker.pystr(130, 175)},
                {'code': 'invalid', 'value': 'no spaces'},
            ],
            'ssh_port': [
                {'code': 'min_value', 'value': -10},
                {'code': 'max_value', 'value': 70000},
            ],
            'name': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'max_length', 'value': helpers.faker.pystr(60, 75)},
            ],
            'is_enabled': [
                {'code': 'nulled', 'value': None},
            ],
            'interval': [
                {'code': 'invalid', 'value': '01:30:00'},
            ],
            'short_desc': [
                {
                    'code': 'max_length',
                    'value': helpers.faker.pystr(145, 175),
                },
            ],
            'tags': [
                {
                    'code': 'item_max_length',
                    'value': [helpers.faker.pystr(35, 40)],
                },
                {
                    'code': 'max_length',
                    'value': [str(i) for i in range(15)],
                },
            ],
        }

        self.assertDjangoRestFrameworkRules(test_case_dict)


class DatastoreSerializerUpdateTests(cases.SerializerTestCase):
    """Test cases for the Datastore serializer class.
    """
    factory = factories.DatastoreFactory

    serializer_class = serializers.DatastoreSerializer

    serializer_resource_name = 'Datastore'

    @classmethod
    def setUpTestData(cls):
        cls.instance = cls.factory(engine=models.Datastore.MYSQL)

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'name': 'Metamapper Test Database',
            'username': 'admin',
            'password': 'password1234',
            'database': 'other_db',
            'host': 'web-86.cortez.net',
            'port': 6667,
        }
        attributes.update(**overrides)
        return attributes

    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_valid_update(self, verify_connection):
        """It should update the provided attributes.
        """
        attributes = {
            'name': 'Data Warehouse',
            'username': 'scott',
            'port': 1234,
            'incident_contacts': [],
        }

        serializer = self.serializer_class(
            instance=self.instance,
            data=attributes,
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceUpdated(self.instance, **attributes)

    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_invalid_update(self, verify_connection):
        """It should update the provided attributes.
        """
        attributes = {
            'name': 'Data Warehouse',
            'username': 'scott',
            'port': -10,
        }

        serializer = self.serializer_class(
            instance=self.instance,
            data=attributes,
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'Datastore',
                'field': 'port',
                'code': 'min_value',
            }
        ])
        self.assertInstanceNotUpdated(self.instance, **attributes)

    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_cannot_update_engine(self, verify_connection):
        """It should not allow for the engine to be updated.
        """
        attributes = {'engine': models.Datastore.REDSHIFT}
        serializer = self.serializer_class(
            instance=self.instance,
            data=attributes,
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceNotUpdated(self.instance, **attributes)

    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_disable_ssh(self, verify_connection):
        """It should not clear the extra parameters.
        """
        instance = self.factory(
            engine=models.Datastore.MYSQL,
            ssh_enabled=True,
            ssh_host='127.0.0.1',
            ssh_user='scott',
            ssh_port=22,
        )

        attributes = {'ssh_enabled': False}
        serializer = self.serializer_class(
            instance=instance,
            data=attributes,
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceUpdated(instance, **attributes)

    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_google_bigquery_valid(self, verify_connection):
        """It should be able to create the resource.
        """
        extras = {
            'extras': {
                'credentials': GOOGLE_SERVICE_ACCOUNT_INFO,
                'invalid': 'this_will_be_stripped_off',
            },
        }

        instance = self.factory(
            engine=models.Datastore.BIGQUERY,
            database='bigquery-sample-data',
            extras=extras['extras']['credentials'],
        )

        attributes = copy.deepcopy(extras)
        attributes['database'] = 'metamapper'
        attributes['extras']['credentials']['project_id'] = 'metamapper-dev'

        serializer = self.serializer_class(
            instance=instance,
            data=attributes,
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())

        instance.refresh_from_db()

        self.assertEqual(instance.database, attributes['database'])
        self.assertEqual(list(instance.extras.keys()), ['credentials'])
        self.assertEqual(
            instance.extras['credentials']['project_id'],
            attributes['extras']['credentials']['project_id'])

    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_google_bigquery_invalid(self, verify_connection):
        """It should be able to create the resource.
        """
        extras = {
            'extras': {
                'credentials': GOOGLE_SERVICE_ACCOUNT_INFO,
                'invalid': 'this_will_be_stripped_off',
            },
        }

        instance = self.factory(
            engine=models.Datastore.BIGQUERY,
            database='bigquery-sample-data',
            extras=extras['extras']['credentials'],
        )

        attributes = copy.deepcopy(extras)
        del attributes['extras']['credentials']['private_key']

        serializer = self.serializer_class(
            instance=instance,
            data=attributes,
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {'code': 'invalid', 'field': 'extras', 'resource': 'Datastore'}
        ])

    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_aws_athena_valid(self, verify_connection):
        """It should be able to create the resource.
        """
        instance = self.factory(
            engine=models.Datastore.ATHENA,
            host='athena.amazonaws.com',
            database='AwsDataCatalog',
            extras={
                'role': 'arn:aws:iam::123456789012:role/default',
                'region': 'us-west-2',
            },
        )

        serializer = self.serializer_class(
            instance=instance,
            data={
                'extras': {
                    'role': 'arn:aws:iam::123456789012:role/other',
                    'region': 'us-east-1',
                }
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())

        instance.refresh_from_db()

        self.assertEqual(instance.host, 'athena.amazonaws.com')
        self.assertEqual(list(instance.extras.keys()), ['role', 'region'])
        self.assertEqual(instance.extras['role'], 'arn:aws:iam::123456789012:role/other')
        self.assertEqual(instance.extras['region'], 'us-east-1')

    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_aws_athena_invalid(self, verify_connection):
        """It should be able to create the resource.
        """
        instance = self.factory(
            engine=models.Datastore.ATHENA,
            host='athena.amazonaws.com',
            database='bigquery-sample-data',
            extras={
                'role': 'arn:aws:iam::123456789012:role/default',
                'region': 'us-west-2',
            },
        )

        serializer = self.serializer_class(
            instance=instance,
            data={
                'extras': {
                    'iam_role': 'arn:aws:iam::123456789012:role/other',
                    'region': 'us-west-2',
                }
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {'code': 'invalid', 'field': 'extras', 'resource': 'Datastore'}
        ])

    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_hive_valid(self, verify_connection):
        """It should be able to create the resource.
        """
        instance = self.factory(
            engine=models.Datastore.HIVE,
            extras={
                'dialect': models.Datastore.POSTGRESQL,
            },
        )

        serializer = self.serializer_class(
            instance=instance,
            data={
                'extras': {
                    'dialect': models.Datastore.MYSQL,
                }
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())

        instance.refresh_from_db()

        self.assertEqual(list(instance.extras.keys()), ['dialect'])
        self.assertEqual(instance.extras['dialect'], models.Datastore.MYSQL)

    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_hive_invalid_dialect(self, verify_connection):
        """It should be able to create the resource.
        """
        instance = self.factory(
            engine=models.Datastore.HIVE,
            extras={
                'dialect': models.Datastore.MYSQL,
            },
        )

        serializer = self.serializer_class(
            instance=instance,
            data={
                'extras': {},
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {'code': 'invalid', 'field': 'extras', 'resource': 'Datastore'}
        ])

    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_validate_incident_contacts(self, verify_connection):
        """It should update the provided attributes.
        """
        attributes = {
            'incident_contacts': [
                'test1@metamapper.io',
                'test2@metamapper.io',
                'test3@metamapper.io',
            ],
        }

        serializer = self.serializer_class(
            instance=self.instance,
            data=attributes,
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceUpdated(self.instance, **attributes)

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        test_case_dict = {
            'username': [
                {'code': 'blank', 'value': ''},
                {'code': 'nulled', 'value': None},
            ],
            'password': [
                {'code': 'blank', 'value': ''},
                {'code': 'nulled', 'value': None},
            ],
            'database': [
                {'code': 'blank', 'value': ''},
                {'code': 'nulled', 'value': None},
            ],
            'host': [
                {'code': 'blank', 'value': ''},
                {'code': 'nulled', 'value': None},
            ],
            'port': [
                {'code': 'invalid', 'value': ''},
                {'code': 'nulled', 'value': None},
                {'code': 'min_value', 'value': -10},
                {'code': 'max_value', 'value': 70000},
            ],
            'ssh_host': [
                {'code': 'invalid', 'value': 'not an ip address'},
            ],
            'ssh_user': [
                {'code': 'max_length', 'value': helpers.faker.pystr(130, 175)},
                {'code': 'invalid', 'value': 'no spaces'},
            ],
            'ssh_port': [
                {'code': 'min_value', 'value': -10},
                {'code': 'max_value', 'value': 70000},
            ],
            'name': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'max_length', 'value': helpers.faker.pystr(60, 75)},
            ],
            'is_enabled': [
                {'code': 'nulled', 'value': None},
            ],
            'interval': [
                {'code': 'invalid', 'value': '01:30:00'},
            ],
            'short_desc': [
                {
                    'code': 'max_length',
                    'value': helpers.faker.pystr(145, 175),
                },
            ],
            'tags': [
                {
                    'code': 'item_max_length',
                    'value': [helpers.faker.pystr(35, 40)],
                },
                {
                    'code': 'max_length',
                    'value': [str(i) for i in range(15)],
                },
            ],
            'incident_contacts': [
                {
                    'code': 'item_invalid',
                    'value': [
                        'bugs.bunny@acmecorp.com',
                        'not-an-email',
                    ],
                },
            ],
        }

        self.assertDjangoRestFrameworkRules(
            test_case_dict,
            instance=self.instance,
            partial=True,
        )


class DatastoreAccessPrivilegesSerializerTests(cases.UserFixtureMixin, cases.SerializerTestCase):
    """Test cases for the Datastore serializer class.
    """
    factory = factories.DatastoreFactory

    serializer_class = serializers.DatastoreAccessPrivilegesSerializer

    serializer_resource_name = 'Datastore'

    def test_when_granting_privileges_for_user(self):
        """It should grant privileges to a User that is in the workspace.
        """
        instance = self.factory(engine=models.Datastore.MYSQL, workspace=self.workspace)
        content_object = self.users['MEMBER']

        instance.assign_perm(content_object, 'change_datastore_metadata')

        serializer = self.serializer_class(
            instance=instance,
            data={
                'content_object': content_object,
                'privileges': [
                    'view_datastore',
                    'change_datastore_settings',
                ],
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())

        self.assertTrue(content_object.has_perm('view_datastore', instance))
        self.assertTrue(content_object.has_perm('change_datastore_settings', instance))
        self.assertFalse(content_object.has_perm('change_datastore_metadata', instance))

    def test_when_revoking_privileges_from_user(self):
        """It should be able to remove all user privileges.
        """
        instance = self.factory(engine=models.Datastore.MYSQL, workspace=self.workspace)
        content_object = self.users['MEMBER']

        instance.assign_perm(content_object, 'change_datastore_metadata')

        serializer = self.serializer_class(
            instance=instance,
            data={
                'content_object': content_object,
                'privileges': [],
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())

        self.assertFalse(content_object.has_perm('change_datastore_metadata', instance))

    def test_when_user_is_not_on_team(self):
        """It should return an error message.
        """
        instance = self.factory(engine=models.Datastore.MYSQL, workspace=self.workspace)
        content_object = self.users['OUTSIDER']

        serializer = self.serializer_class(
            instance=instance,
            data={
                'content_object': content_object,
                'privileges': ['view_datastore', 'change_datastore'],
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'code': 'invalid_user',
                'field': 'content_object',
                'resource': 'Datastore',
            }
        ])

    def test_when_granting_privileges_for_group(self):
        """It should grant privileges to a Group that is in the workspace.
        """
        instance = self.factory(engine=models.Datastore.MYSQL, workspace=self.workspace)
        content_object = factories.GroupFactory(workspace=self.workspace)

        instance.assign_perm(content_object, 'change_datastore_metadata')

        serializer = self.serializer_class(
            instance=instance,
            data={
                'content_object': content_object,
                'privileges': [
                    'view_datastore',
                    'change_datastore_settings',
                ],
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())

        checker = ObjectPermissionChecker(content_object)

        self.assertTrue(checker.has_perm('view_datastore', instance))
        self.assertTrue(checker.has_perm('change_datastore_settings', instance))
        self.assertFalse(checker.has_perm('change_datastore_metadata', instance))

    def test_when_revoking_grants_for_group(self):
        """It should be able to remove all group privileges.
        """
        instance = self.factory(engine=models.Datastore.MYSQL, workspace=self.workspace)
        content_object = factories.GroupFactory(workspace=self.workspace)

        instance.assign_perm(content_object, 'change_datastore_metadata')

        serializer = self.serializer_class(
            instance=instance,
            data={
                'content_object': content_object,
                'privileges': [],
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())

        checker = ObjectPermissionChecker(content_object)
        self.assertFalse(checker.has_perm('change_datastore_metadata', instance))

    def test_when_group_is_not_in_workspace(self):
        """It should return an error message.
        """
        instance = self.factory(engine=models.Datastore.MYSQL, workspace=self.workspace)

        serializer = self.serializer_class(
            instance=instance,
            data={
                'content_object': factories.GroupFactory(),
                'privileges': ['view_datastore', 'change_datastore'],
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'code': 'invalid_group',
                'field': 'content_object',
                'resource': 'Datastore',
            }
        ])

    def test_when_privilege_is_invalid(self):
        """It should return an error message if the privilege is not accepted.
        """
        instance = self.factory(engine=models.Datastore.MYSQL, workspace=self.workspace)

        serializer = self.serializer_class(
            instance=instance,
            data={
                'content_object': factories.GroupFactory(workspace=self.workspace),
                'privileges': ['view_datastore', 'upsert_datastore'],
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'code': 'invalid_grant',
                'field': 'privileges',
                'resource': 'Datastore',
            }
        ])


class ToggleDatastoreObjectPermissionsSerializerTest(cases.SerializerTestCase):
    """Test cases for toggling object permissions on and off.
    """
    factory = factories.DatastoreFactory

    serializer_class = serializers.ToggleDatastoreObjectPermissionsSerializer

    serializer_resource_name = 'Datastore'

    def test_from_on_to_off(self):
        """It should successfully disable object-level permissions.
        """
        instance = self.factory(object_permissions_enabled=True)

        serializer = self.serializer_class(
            instance=instance,
            data={'object_permissions_enabled': False},
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceUpdated(instance, object_permissions_enabled=False)

    def test_from_off_to_on(self):
        """It should successfully disable object-level permissions.
        """
        instance = self.factory(object_permissions_enabled=False)

        serializer = self.serializer_class(
            instance=instance,
            data={'object_permissions_enabled': True},
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceUpdated(instance, object_permissions_enabled=True)


class TableSerializerUpdateTests(cases.SerializerTestCase):
    """Test cases for the Table serializer class.
    """
    factory = factories.TableFactory

    serializer_class = serializers.TableSerializer

    serializer_resource_name = 'Table'

    @classmethod
    def setUpTestData(cls):
        cls.instance = cls.factory(tags=['one', 'two', 'three'])

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'tags': helpers.faker.words(unique=True),
            'short_desc': helpers.faker.text(max_nb_chars=80),
            'readme': helpers.faker.text(max_nb_chars=80),
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should be able to update the resource.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(
            instance=self.instance,
            data=attributes,
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceUpdated(self.instance, **attributes)

    def test_when_nullifying_tags(self):
        """It should be able to update the resource.
        """
        serializer = self.serializer_class(
            instance=self.instance,
            data={'tags': None},
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceUpdated(self.instance, tags=[])

    def test_when_nullifying_short_desc(self):
        """It should be able to update the resource.
        """
        serializer = self.serializer_class(
            instance=self.instance,
            data={'short_desc': None},
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceUpdated(self.instance, short_desc='')

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        test_case_dict = {
            'tags': [
                {
                    'code': 'item_max_length',
                    'value': [helpers.faker.pystr(35, 40)],
                },
                {
                    'code': 'max_length',
                    'value': [str(i) for i in range(15)],
                },
            ],
        }

        self.assertDjangoRestFrameworkRules(
            test_case_dict,
            instance=self.instance,
            partial=True,
        )


class ColumnSerializerUpdateTests(cases.SerializerTestCase):
    """Test cases for the Column serializer class.
    """
    factory = factories.ColumnFactory

    serializer_class = serializers.ColumnSerializer

    serializer_resource_name = 'Column'

    @classmethod
    def setUpTestData(cls):
        cls.instance = cls.factory(short_desc='Something random.')

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'short_desc': helpers.faker.text(max_nb_chars=45),
            'readme': helpers.faker.text(max_nb_chars=45),
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should be able to update the resource.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(
            instance=self.instance,
            data=attributes,
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceUpdated(self.instance, **attributes)

    def test_when_blankifying_short_desc(self):
        """It should be able to update the resource.
        """
        serializer = self.serializer_class(
            instance=self.instance,
            data={'short_desc': ''},
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceUpdated(self.instance, short_desc='')

    def test_when_nullifying_short_desc(self):
        """It should be able to update the resource.
        """
        serializer = self.serializer_class(
            instance=self.instance,
            data={'short_desc': None},
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceUpdated(self.instance, short_desc='')


class AssetOwnerSerializerCreateTests(cases.SerializerTestCase):
    """Test cases for creating an asset owner.
    """
    factory = factories.DatastoreFactory

    serializer_class = serializers.AssetOwnerSerializer

    serializer_resource_name = 'AssetOwner'

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.user = factories.UserFactory()
        cls.workspace.grant_membership(cls.user, 'MEMBER')
        cls.request = collections.namedtuple('Request', ['user', 'workspace'])(user=cls.user, workspace=cls.workspace)
        cls.content_object = factories.TableFactory(workspace=cls.workspace)

    def test_valid_group(self):
        """It should create the asset owner.
        """
        group = factories.GroupFactory(workspace=self.workspace)

        attributes = {'owner': group, 'content_object': self.content_object, 'order': 1}
        serializer = self.serializer_class(data=attributes, context={'request': self.request})

        self.assertTrue(serializer.is_valid())
        instance = serializer.save(workspace=self.workspace)
        self.assertTrue(instance)
        self.assertTrue(instance.order == attributes['order'])

    def test_with_invalid_group(self):
        """It should throw an error if the group is not a part of the workspace.
        """
        group = factories.GroupFactory()

        attributes = {'owner': group, 'content_object': self.content_object, 'order': 1}
        serializer = self.serializer_class(data=attributes, context={'request': self.request})

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'code': 'invalid',
                'field': 'owner',
                'resource': 'AssetOwner',
            }
        ])

    def test_with_valid_user(self):
        """It should create the asset owner.
        """
        user = factories.UserFactory()
        self.workspace.grant_membership(user, 'MEMBER')

        attributes = {'owner': user, 'content_object': self.content_object, 'order': 1}
        serializer = self.serializer_class(data=attributes, context={'request': self.request})

        self.assertTrue(serializer.is_valid())
        instance = serializer.save(workspace=self.workspace)
        self.assertTrue(instance)
        self.assertTrue(instance.order == attributes['order'])

    def test_with_invalid_user(self):
        """It should throw an error if the user is not a part of the workspace.
        """
        user = factories.UserFactory()

        attributes = {'owner': user, 'content_object': self.content_object, 'order': 1}
        serializer = self.serializer_class(data=attributes, context={'request': self.request})

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'code': 'invalid',
                'field': 'owner',
                'resource': 'AssetOwner',
            }
        ])

    def test_reposition(self):
        """It should shift around the positions.
        """
        content_object = factories.TableFactory(workspace=self.workspace)
        owners = []
        for user in factories.UserFactory.create_batch(5):
            self.workspace.grant_membership(user, 'MEMBER')
            owners.append(
                content_object.owners.create(owner=user, workspace=self.workspace)
            )

        group = factories.GroupFactory(workspace=self.workspace)

        attributes = {'owner': group, 'content_object': content_object, 'order': 3}
        serializer = self.serializer_class(data=attributes, context={'request': self.request})

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(workspace=self.workspace))

        for n, owner in enumerate(owners[attributes['order']:], 1):
            order = owner.order
            owner.refresh_from_db()
            self.assertTrue(owner.order != order)
            self.assertTrue(owner.order == attributes['order'] + n)


class AssetOwnerSerializerUpdateTests(cases.SerializerTestCase):
    """Test cases for updating an asset owner.
    """
    factory = factories.DatastoreFactory

    serializer_class = serializers.AssetOwnerSerializer

    serializer_resource_name = 'AssetOwner'

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.user = factories.UserFactory()
        cls.workspace.grant_membership(cls.user, 'MEMBER')
        cls.request = collections.namedtuple('Request', ['user', 'workspace'])(user=cls.user, workspace=cls.workspace)

    def test_reposition(self):
        """It should shift around the positions.
        """
        content_object = factories.TableFactory(workspace=self.workspace)

        owners = []
        for user in factories.UserFactory.create_batch(5):
            self.workspace.grant_membership(user, 'MEMBER')
            owners.append(
                content_object.owners.create(owner=user, workspace=self.workspace)
            )

        group = factories.GroupFactory(workspace=self.workspace)
        owner = content_object.owners.create(owner=group, workspace=self.workspace)
        order = owner.order

        attributes = {'owner': group, 'content_object': content_object, 'order': 3}
        serializer = self.serializer_class(
            instance=owner,
            data=attributes,
            partial=True,
            context={'request': self.request},
        )

        owner.refresh_from_db()

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(workspace=self.workspace))
        self.assertTrue(owner.order != order)
        self.assertTrue(owner.order == attributes['order'])

        for n, owner in enumerate(owners[attributes['order']:], 1):
            order = owner.order
            owner.refresh_from_db()
            self.assertTrue(owner.order != order)
            self.assertTrue(owner.order == attributes['order'] + n)
