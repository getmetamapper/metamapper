# -*- coding: utf-8 -*-
import unittest.mock as mock

import testutils.cases as cases
import testutils.decorators as decorators

import app.authorization.models as models


class GrantMembershipTests(cases.GraphQLTestCase):
    """Test cases for granting membership to a workspace.
    """
    operation = 'grantMembership'
    statement = '''
    mutation grantMembership($email: String!, $permissions: String!) {
      grantMembership(input: {
        email: $email,
        permissions: $permissions,
      }) {
        ok
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    @mock.patch('app.authorization.emails.membership_granted')
    @decorators.as_someone(['OWNER'])
    def test_grant_new_membership(self, membership_granted):
        variables = {
            'permissions': 'MEMBER',
            'email': self.users['OUTSIDER'].email,
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        membership_granted.assert_called_once()
        membership_granted.assert_called_with(
            variables['email'],
            self.workspace,
            variables['permissions'],
        )

        self.assertOk(response)
        self.assertInstanceExists(
            model_class=models.Membership,
            workspace=self.workspace,
            user_id=variables['email'],
            permissions=variables['permissions'],
        )

    @mock.patch('app.authorization.emails.membership_granted')
    @decorators.as_someone(['OWNER'])
    def test_upgrade_membership(self, membership_granted):
        variables = {
            'permissions': 'MEMBER',
            'email': self.users['READONLY'].email,
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        membership_granted.assert_called_once()
        membership_granted.assert_called_with(
            variables['email'],
            self.workspace,
            variables['permissions'],
        )

        self.assertOk(response)
        self.assertInstanceExists(
            model_class=models.Membership,
            workspace=self.workspace,
            user_id=variables['email'],
            permissions=variables['permissions'],
        )

    @mock.patch('app.authorization.emails.membership_granted')
    @decorators.as_someone(['OWNER'])
    def test_downgrade_membership(self, membership_granted):
        variables = {
            'permissions': 'READONLY',
            'email': self.users['MEMBER'].email,
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        membership_granted.assert_called_once()
        membership_granted.assert_called_with(
            variables['email'],
            self.workspace,
            variables['permissions'],
        )

        self.assertOk(response)
        self.assertInstanceExists(
            model_class=models.Membership,
            workspace=self.workspace,
            user_id=variables['email'],
            permissions=variables['permissions'],
        )

    @mock.patch('app.authorization.emails.membership_granted')
    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER'])
    def test_grant_membership_when_unauthorized(self, membership_granted):
        owner = self.users['OWNER']
        variables = {
            'permissions': 'MEMBER',
            'email': owner.email,
        }

        response = self.execute(variables=variables)

        owner.refresh_from_db()
        membership_granted.assert_not_called()
        self.assertPermissionDenied(response)
        self.assertTrue(owner.is_owner(self.workspace.pk))

    @mock.patch('app.authorization.emails.membership_granted')
    @decorators.as_someone(['OWNER'])
    def test_grant_membership_invalid_permissions(self, membership_granted):
        variables = {
            'permissions': 'super-hero',
            'email': self.users['READONLY'].email,
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ok': False,
            'errors': [
                {
                    'resource': 'Membership',
                    'field': 'permissions',
                    'code': 'invalid_choice',
                },
            ],
        })

        membership_granted.assert_not_called()

        self.assertInstanceDoesNotExist(
            model_class=models.Membership,
            workspace=self.workspace,
            user_id=variables['email'],
            permissions=variables['permissions'],
        )

    @mock.patch('app.authorization.emails.membership_granted')
    @decorators.as_someone(['OWNER'])
    def test_grant_membership_invalid_email(self, membership_granted):
        variables = {
            'permissions': 'MEMBER',
            'email': 'thisisnotanemail',
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ok': False,
            'errors': [
                {
                    'resource': 'Membership',
                    'field': 'email',
                    'code': 'invalid',
                },
            ],
        })

        membership_granted.assert_not_called()

        self.assertInstanceDoesNotExist(
            model_class=models.Membership,
            workspace=self.workspace,
            user_id=variables['email'],
        )

    @mock.patch('app.authorization.emails.membership_granted')
    @decorators.as_someone(['OWNER'])
    def test_grant_membership_on_self(self, membership_granted):
        variables = {
            'permissions': 'MEMBER',
            'email': self.user.email,
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ok': False,
            'errors': [
                {
                    'resource': 'Membership',
                    'field': 'email',
                    'code': 'self_update',
                },
            ],
        })

        membership_granted.assert_not_called()

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_owner(self.workspace.id))


class RevokeMembershipTests(cases.GraphQLTestCase):
    """Test cases for revoking membership to a workspace.
    """
    operation = 'revokeMembership'
    statement = '''
    mutation revokeMembership($email: String!) {
      revokeMembership(input: {
        email: $email
      }) {
        ok
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    @mock.patch('app.authorization.emails.membership_revoked')
    @decorators.as_someone(['OWNER'])
    def test_revoke_readonly(self, membership_revoked):
        user = self.users['READONLY']
        variables = {
            'email': user.email,
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        membership_revoked.assert_called_once()
        membership_revoked.assert_called_with(user.email, self.workspace)

        self.assertOk(response)
        self.assertInstanceDeleted(
            model_class=models.Membership,
            workspace=self.workspace,
            user_id=variables['email'],
        )

    @mock.patch('app.authorization.emails.membership_revoked')
    @decorators.as_someone(['OWNER'])
    def test_revoke_member(self, membership_revoked):
        user = self.users['MEMBER']
        variables = {
            'email': user.email,
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        membership_revoked.assert_called_once()
        membership_revoked.assert_called_with(user.email, self.workspace)

        self.assertOk(response)
        self.assertInstanceDeleted(
            model_class=models.Membership,
            workspace=self.workspace,
            user_id=variables['email'],
        )

    @mock.patch('app.authorization.emails.membership_revoked')
    @decorators.as_someone(['OWNER'])
    def test_revoke_owner(self, membership_revoked):
        user = self.users['MEMBER']
        self.workspace.grant_membership(user, models.Membership.OWNER)

        variables = {
            'email': user.email,
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        membership_revoked.assert_called_once()
        membership_revoked.assert_called_with(user.email, self.workspace)

        self.assertOk(response)
        self.assertInstanceDeleted(
            model_class=models.Membership,
            workspace=self.workspace,
            user_id=variables['email'],
        )

    @mock.patch('app.authorization.emails.membership_revoked')
    @decorators.as_someone(['OWNER', 'MEMBER', 'READONLY'])
    def test_revoke_self(self, membership_revoked):
        variables = {
            'email': self.user.email,
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        membership_revoked.assert_called_once()
        membership_revoked.assert_called_with(self.user.email, self.workspace)

        self.assertOk(response)
        self.assertInstanceDeleted(
            model_class=models.Membership,
            workspace=self.workspace,
            user_id=variables['email'],
        )

        membership_revoked.reset_mock()

    @mock.patch('app.authorization.emails.membership_revoked')
    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER'])
    def test_revoke_membership_unauthorized(self, membership_revoked):
        variables = {
            'email': self.users['OWNER'].email,
        }

        response = self.execute(variables=variables)

        membership_revoked.assert_not_called()

        self.assertPermissionDenied(response)
        self.assertInstanceExists(
            model_class=models.Membership,
            workspace=self.workspace,
            user_id=variables['email'],
        )
