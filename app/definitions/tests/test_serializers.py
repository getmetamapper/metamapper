# -*- coding: utf-8 -*-
import unittest.mock as mock
import random

import app.definitions.models as models
import app.definitions.serializers as serializers

import app.inspector.service as inspector

import testutils.cases as cases
import testutils.factories as factories
import testutils.helpers as helpers


class DatastoreSerializerCreateTests(cases.SerializerTestCase):
    """Test cases for the Datastore serializer class.
    """
    factory = factories.DatastoreFactory

    serializer_class = serializers.DatastoreSerializer

    serializer_resource_name = 'Datastore'

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()

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

    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_when_valid_hostname(self, verify_connection, mock_run):
        """It should be able to create the resource.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(workspace=self.workspace))

    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_when_valid_ip_address(self, verify_connection, mock_run):
        """It should be able to create the resource.
        """
        attributes = self._get_attributes(host='54.32.11.00')
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(workspace=self.workspace))

    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
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

    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
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

    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
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

    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
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

    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_when_duplicate_tags(self, verify_connection, mock_run):
        """It should automatically de-duplicate tags.
        """
        attributes = self._get_attributes(tags=['red', 'red', 'blue'])
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())

        instance = serializer.save(workspace=self.workspace)

        self.assertEqual(set(instance.tags), {'red', 'blue'})

    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
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

    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_partial_ssh_information(self, verify_connection, mock_run):
        """If we need SSH information, we need all 3 fields.
        """
        extras = {
            'ssh_enabled': True,
            'ssh_host': '54.32.11.00',
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

    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_with_entire_ssh_information(self, verify_connection, mock_run):
        """It should be able to create the resource.
        """
        extras = {
            'ssh_enabled': True,
            'ssh_host': '54.32.11.00',
            'ssh_user': 'scott',
            'ssh_port': 22,
        }

        attributes = self._get_attributes(**extras)
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())

        instance = serializer.save(workspace=self.workspace)

        self.assertEqual(instance.ssh_host, extras['ssh_host'])
        self.assertEqual(instance.ssh_user, extras['ssh_user'])
        self.assertEqual(instance.ssh_port, extras['ssh_port'])

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
                {'code': 'invalid', 'value': 'no spaces'},
            ],
            'password': [
                {'code': 'blank', 'value': ''},
                {'code': 'nulled', 'value': None},
            ],
            'database': [
                {'code': 'blank', 'value': ''},
                {'code': 'nulled', 'value': None},
                {'code': 'invalid', 'value': 'no spaces'},
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

    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_valid_update(self, verify_connection, mock_run):
        """It should update the provided attributes.
        """
        attributes = {
            'name': 'Data Warehouse',
            'username': 'scott',
            'port': 1234,
        }

        serializer = self.serializer_class(
            instance=self.instance,
            data=attributes,
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceUpdated(self.instance, **attributes)

    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_invalid_update(self, verify_connection, mock_run):
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

    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_cannot_update_engine(self, verify_connection, mock_run):
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

    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_disable_ssh(self, verify_connection, mock_run):
        """It should not clear the extra parameters.
        """
        instance = self.factory(
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

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        test_case_dict = {
            'username': [
                {'code': 'blank', 'value': ''},
                {'code': 'nulled', 'value': None},
                {'code': 'invalid', 'value': 'no spaces'},
            ],
            'password': [
                {'code': 'blank', 'value': ''},
                {'code': 'nulled', 'value': None},
            ],
            'database': [
                {'code': 'blank', 'value': ''},
                {'code': 'nulled', 'value': None},
                {'code': 'invalid', 'value': 'no spaces'},
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

        self.assertDjangoRestFrameworkRules(
            test_case_dict,
            instance=self.instance,
            partial=True,
        )


class TableSerializerUpdateTests(cases.SerializerTestCase):
    """Test cases for the Table serializer class.
    """
    factory = factories.DatastoreFactory

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

        self.assertDjangoRestFrameworkRules(
            test_case_dict,
            instance=self.instance,
            partial=True,
        )


class ColumnSerializerUpdateTests(cases.SerializerTestCase):
    """Test cases for the Column serializer class.
    """
    factory = factories.DatastoreFactory

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

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        test_case_dict = {
            'short_desc': [
                {
                    'code': 'max_length',
                    'value': helpers.faker.pystr(91, 105),
                },
            ],
        }

        self.assertDjangoRestFrameworkRules(
            test_case_dict,
            instance=self.instance,
            partial=True,
        )
