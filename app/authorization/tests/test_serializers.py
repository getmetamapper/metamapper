# -*- coding: utf-8 -*-
import collections

import app.authorization.models as models
import app.authorization.serializers as serializers

import testutils.cases as cases
import testutils.factories as factories
import testutils.helpers as helpers


class GrantMembershipSerializerTest(cases.SerializerTestCase):
    """Test cases for the granting workspace memberships to users.
    """
    factory = None

    serializer_class = serializers.GrantMembershipSerializer

    serializer_resource_name = 'Membership'

    @classmethod
    def setUpTestData(cls):
        cls.current_user = factories.UserFactory()
        cls.workspace = factories.WorkspaceFactory(creator=cls.current_user)
        cls.workspace.grant_membership(cls.current_user, models.Membership.OWNER)
        cls.user = factories.UserFactory()
        cls.membership, _ = cls.workspace.grant_membership(cls.user, models.Membership.READONLY)
        cls.request = collections.namedtuple('Request', ['user'])(user=cls.current_user)

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'email': self.user.email,
            'permissions': models.Membership.MEMBER,
        }
        attributes.update(**overrides)
        return attributes

    def test_when_existing_user(self):
        """It should be able to update the resource.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes, context={'request': self.request})

        membership_count = self.workspace.memberships.count()

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(workspace=self.workspace))
        self.assertTrue(self.user.is_staff(self.workspace))
        self.assertTrue(membership_count == self.workspace.memberships.count())

    def test_when_not_existing_user(self):
        """It should be able to create the resource.
        """
        attributes = self._get_attributes(email='nobody@metamapper.io')
        serializer = self.serializer_class(data=attributes, context={'request': self.request})

        self.assertTrue(serializer.is_valid())

        instance = serializer.save(workspace=self.workspace)

        self.assertTrue(isinstance(instance, (models.Membership,)))

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        test_case_dict = {
            'email': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'invalid', 'value': 'django-is-not-an-email'},
                {'code': 'self_update', 'value': self.current_user.email},
            ],
            'permissions': [
                {'code': 'nulled', 'value': None},
                {'code': 'invalid_choice', 'value': 'randomness'},
            ],
        }

        self.assertDjangoRestFrameworkRules(
            test_case_dict,
            context={'request': self.request},
        )


class RevokeMembershipSerializerTest(cases.SerializerTestCase):
    """Test cases for the revoking workspace memberships to users.
    """
    factory = None

    serializer_class = serializers.RevokeMembershipSerializer

    serializer_resource_name = 'Membership'

    @classmethod
    def setUpTestData(cls):
        cls.user = factories.UserFactory()
        cls.current_user = factories.UserFactory()
        cls.workspace = factories.WorkspaceFactory(creator=cls.current_user)
        cls.membership, _ = cls.workspace.grant_membership(cls.user, models.Membership.READONLY)
        cls.current_membership, _ = cls.workspace.grant_membership(cls.current_user, models.Membership.OWNER)
        cls.request = collections.namedtuple(
            'Request',
            ['user', 'workspace'],
        )(user=cls.current_user, workspace=cls.workspace)

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'email': self.user.email,
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should be able to create the resource.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(
            instance=self.membership,
            data=attributes,
            partial=True,
            context={'request': self.request},
        )

        serializer.save(workspace=self.workspace)

        self.assertFalse(self.user.is_on_team(self.workspace))

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        test_case_dict = {
            'email': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'invalid', 'value': 'django-is-not-an-email'},
                {'code': 'only_owner', 'value': self.current_user.email},
            ],
        }

        self.assertDjangoRestFrameworkRules(
            test_case_dict,
            instance=self.current_membership,
            partial=True,
            context={'request': self.request},
        ),


class GroupSerializerCreateTest(cases.SerializerTestCase):
    """Test cases for the creating Group instances via GroupSerializer class.
    """
    factory = factories.GroupFactory

    serializer_class = serializers.GroupSerializer

    serializer_resource_name = 'Group'

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'name': helpers.faker.text(max_nb_chars=20),
            'description': helpers.faker.text(max_nb_chars=50),
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should be able to create the resource.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(workspace=self.workspace))

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        test_case_dict = {
            'name': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'max_length', 'value': helpers.faker.pystr(26, 35)},
            ],
            'description': [
                {'code': 'max_length', 'value': helpers.faker.pystr(65, 80)},
            ],
        }

        self.assertDjangoRestFrameworkRules(test_case_dict)


class GroupSerializerUpdateTest(cases.SerializerTestCase):
    """Test cases for the updating Group instances via GroupSerializer class.
    """
    factory = factories.GroupFactory

    serializer_class = serializers.GroupSerializer

    serializer_resource_name = 'Group'

    @classmethod
    def setUpTestData(cls):
        cls.instance = cls.factory(name='Everyone')

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'name': helpers.faker.text(max_nb_chars=20),
            'description': helpers.faker.text(max_nb_chars=50),
        }
        attributes.update(**overrides)
        return attributes

    def test_valid_update(self):
        """It should update the provided attributes.
        """
        attributes = {
            'name': 'Nobody',
            'description': '',
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
            'name': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'max_length', 'value': helpers.faker.pystr(26, 35)},
            ],
            'description': [
                {'code': 'max_length', 'value': helpers.faker.pystr(65, 80)},
            ],
        }

        self.assertDjangoRestFrameworkRules(test_case_dict)


class AddUserToGroupSerializerTest(cases.SerializerTestCase):
    """Test cases for adding a User to a Group via the AddUserToGroupSerializer class.
    """
    factory = factories.GroupFactory

    serializer_class = serializers.AddUserToGroupSerializer

    serializer_resource_name = 'Group'

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.instance = cls.factory(name='Everyone', workspace=cls.workspace)

    def test_valid_update(self):
        """It should create the group membership.
        """
        user = factories.UserFactory()
        self.workspace.grant_membership(user, models.Membership.MEMBER)

        serializer = self.serializer_class(
            instance=self.instance,
            data={'user': user.pk},
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertTrue(user.groups.filter(name=self.instance.name).exists())

    def test_when_not_team_member(self):
        """It should return an error.
        """
        user = factories.UserFactory()

        serializer = self.serializer_class(
            instance=self.instance,
            data={'user': user.pk},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors, [
            {
                'code': 'no_membership',
                'field': 'user',
                'resource': 'User',
            }
        ])

    def test_when_not_existing_user(self):
        """It should return an error.
        """
        serializer = self.serializer_class(
            instance=self.instance,
            data={'user': 123456789},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors, [
            {
                'code': 'does_not_exist',
                'field': 'user',
                'resource': 'User',
            }
        ])


class RemoveUserFromGroupSerializerTest(cases.SerializerTestCase):
    """Test cases for removing a User from a Group via the RemoveUserFromGroupSerializer class.
    """
    factory = factories.GroupFactory

    serializer_class = serializers.RemoveUserFromGroupSerializer

    serializer_resource_name = 'Group'

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.instance = cls.factory(name='Everyone', workspace=cls.workspace)

    def test_valid_update(self):
        """It should create the group membership.
        """
        user = factories.UserFactory()

        self.workspace.grant_membership(user, models.Membership.MEMBER)
        self.instance.user_set.add(user)

        serializer = self.serializer_class(
            instance=self.instance,
            data={'user': user.pk},
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertFalse(user.groups.filter(name=self.instance.name).exists())

    def test_when_not_existing_user(self):
        """It should return an error.
        """
        serializer = self.serializer_class(
            instance=self.instance,
            data={'user': 123456789},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors, [
            {
                'code': 'does_not_exist',
                'field': 'user',
                'resource': 'User',
            }
        ])
