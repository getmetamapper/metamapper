# -*- coding: utf-8 -*-
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

    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_when_valid_hostname(self, verify_connection, mock_run):
        """It should be able to create the resource.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        instance = serializer.save(workspace=self.workspace, creator=self.user)
        self.assertTrue(self.user.has_perm('view_datastore', instance))

    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    def test_when_valid_ip_address(self, verify_connection, mock_run):
        """It should be able to create the resource.
        """
        attributes = self._get_attributes(host='54.32.11.00')
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        instance = serializer.save(workspace=self.workspace, creator=self.user)
        self.assertTrue(self.user.has_perm('view_datastore', instance))

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

        instance = serializer.save(workspace=self.workspace, creator=self.user)

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

        instance = serializer.save(workspace=self.workspace, creator=self.user)

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
