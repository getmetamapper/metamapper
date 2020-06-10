# -*- coding: utf-8 -*-
import collections

import app.authentication.serializers as serializers

import testutils.cases as cases
import testutils.factories as factories
import testutils.helpers as helpers


class UserSerializerTest(cases.SerializerTestCase):
    """Test cases for the creating instances via UserSerializer class.
    """
    factory = factories.UserFactory

    serializer_class = serializers.UserSerializer

    serializer_resource_name = 'User'

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'fname': helpers.faker.first_name(),
            'lname': helpers.faker.last_name(),
            'email': helpers.faker.email(),
            'password': helpers.faker.password(),
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should be able to create the resource.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        user = self.factory()

        test_case_dict = {
            'email': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'invalid', 'value': 'django-is-not-an-email'},
                {'code': 'exists', 'value': user.email},
            ],
            'fname': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'max_length', 'value': helpers.faker.pystr(65, 80)},
            ],
            'lname': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'max_length', 'value': helpers.faker.pystr(65, 80)},
            ],
            'password': [
                {'code': 'too_weak', 'value': 'password'}
            ]
        }

        self.assertDjangoRestFrameworkRules(test_case_dict)


class CurrentUserSerializerTest(cases.SerializerTestCase):
    """Test cases for the editing instances via CurrentUserSerializer class.
    """
    factory = factories.UserFactory

    serializer_class = serializers.CurrentUserSerializer

    serializer_resource_name = 'User'

    @classmethod
    def setUpTestData(cls):
        cls.password = 'correctbatteryhorsestaple'
        cls.resource = cls.factory(password=cls.password)
        cls.resource.set_password(cls.password)
        cls.resource.save()
        cls.request = collections.namedtuple('Request', ['user'])(user=cls.resource)

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'fname': helpers.faker.first_name(),
            'lname': helpers.faker.last_name(),
            'email': helpers.faker.email(),
            'current_password': self.password,
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should be able to update the resource.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(
            instance=self.resource,
            data=attributes,
            partial=True,
            context={'request': self.request},
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceUpdated(self.resource, **attributes)

    def test_when_wrong_current_password(self):
        """It should return the proper error payload.
        """
        attributes = self._get_attributes(current_password='password1234')
        serializer = self.serializer_class(
            instance=self.resource,
            data=attributes,
            partial=True,
            context={'request': self.request},
        )

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'User',
                'field': 'current_password',
                'code': 'wrong_password',
            }
        ])

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        user = self.factory()

        test_case_dict = {
            'email': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'invalid', 'value': 'django-is-not-an-email'},
                {'code': 'exists', 'value': user.email},
            ],
            'fname': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'max_length', 'value': helpers.faker.pystr(65, 80)},
            ],
            'lname': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'max_length', 'value': helpers.faker.pystr(65, 80)},
            ],
            'password': [
                {'code': 'too_weak', 'value': 'password'}
            ]
        }

        self.assertDjangoRestFrameworkRules(
            test_case_dict,
            instance=self.resource,
            partial=True,
            context={'request': self.request},
        )


class WorkspaceSerializerCreateTest(cases.SerializerTestCase):
    """Test cases for the creating instances via WorkspaceSerializer class.
    """
    factory = factories.WorkspaceFactory

    serializer_class = serializers.WorkspaceSerializer

    serializer_resource_name = 'Workspace'

    @classmethod
    def setUpTestData(cls):
        cls.creator = factories.UserFactory()
        cls.workspace = cls.factory()

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'name': 'Vesuvio',
            'slug': 'vesuvio',
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should be able to update the resource.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(creator=self.creator))
        self.assertTrue(self.creator.is_owner(serializer.instance.id))

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        workspace = self.factory()

        test_case_dict = {
            'name': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'min_length', 'value': helpers.faker.pystr(1, 2)},
                {'code': 'max_length', 'value': helpers.faker.pystr(260, 400)},
            ],
            'slug': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'invalid', 'value': 'no spaces allowed'},
                {'code': 'min_length', 'value': helpers.faker.pystr(1, 2)},
                {'code': 'max_length', 'value': helpers.faker.pystr(65, 80)},
                {'code': 'exists', 'value': workspace.slug},
            ],
        }

        self.assertDjangoRestFrameworkRules(test_case_dict)


class WorkspaceSerializerUpdateTest(cases.SerializerTestCase):
    """Test cases for the editing instances via WorkspaceSerializer class.
    """
    factory = factories.WorkspaceFactory

    serializer_class = serializers.WorkspaceSerializer

    serializer_resource_name = 'Workspace'

    @classmethod
    def setUpTestData(cls):
        cls.creator = factories.UserFactory()
        cls.resource = cls.factory()
        cls.workspace = cls.factory()

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'name': 'vesuvio',
            'slug': 'vesuvio',
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should be able to update the resource.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(
            instance=self.resource,
            data=attributes,
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceUpdated(self.resource, **attributes)

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        workspace = self.factory()

        test_case_dict = {
            'name': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'min_length', 'value': helpers.faker.pystr(1, 2)},
                {'code': 'max_length', 'value': helpers.faker.pystr(260, 400)},
            ],
            'slug': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'min_length', 'value': helpers.faker.pystr(1, 2)},
                {'code': 'max_length', 'value': helpers.faker.pystr(65, 80)},
                {'code': 'exists', 'value': workspace.slug},
            ],
        }

        self.assertDjangoRestFrameworkRules(
            test_case_dict,
            instance=self.resource,
            partial=True,
        )
