# -*- coding: utf-8 -*-
import collections

import app.authorization.models as models
import app.authorization.serializers as serializers

import testutils.cases as cases
import testutils.factories as factories


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
