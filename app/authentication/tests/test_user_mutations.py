# -*- coding: utf-8 -*-
import datetime as dt
import uuid
import unittest.mock as mock

import testutils.cases as cases

import app.authentication.models as models

from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone

from freezegun import freeze_time


class RegisterTests(cases.GraphQLTestCase):
    """Test cases for registering a new User.
    """
    authenticated = False
    operation = 'registerUser'
    statement = '''
    mutation registerUser(
      $fname: String!,
      $lname: String!,
      $email: String!,
      $password: String!,
    ) {
      registerUser(input: {
        fname: $fname,
        lname: $lname,
        email: $email,
        password: $password
      }) {
        user {
          fname
          lname
          email
        }
        jwt
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    def test_register_valid_user(self):
        """It creates a valid User.
        """
        variables = {
            'fname': 'Scott',
            'lname': 'Cruwys',
            'email': 'scruwys@metamapper.io',
            'password': 'passwordOk1431',
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response['user'], {
            'fname': variables['fname'],
            'lname': variables['lname'],
            'email': variables['email'],
        })

        self.assertValidJsonWebToken(response['jwt'])
        self.assertEqual(response['errors'], None)
        self.assertInstanceCreated(models.User, **variables)

    def test_register_with_invalid_inputs(self):
        """It does not create the User.
        """
        variables = {
            'fname': 'Scott',
            'lname': '',
            'email': 'notavalidemail',
            'password': 'password',
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'user': None,
            'jwt': None,
            'errors': [
                {
                    'resource': 'User',
                    'field': 'lname',
                    'code': 'blank',
                },
                {
                    'resource': 'User',
                    'field': 'email',
                    'code': 'invalid',
                },
                {
                    'resource': 'User',
                    'field': 'password',
                    'code': 'too_weak',
                },
            ],
        })

        self.assertInstanceDoesNotExist(models.User, **variables)


class ResetPasswordTests(cases.GraphQLTestCase):
    """Test cases for requesting a password reset email.
    """
    authenticated = False
    operation = 'resetPassword'
    statement = '''
    mutation resetPassword($email: String!) {
        resetPassword(email: $email) {
          ok
          errors {
            resource
            field
            code
          }
        }
    }
    '''

    @mock.patch('app.authentication.emails.reset_password')
    def test_reset_password(self, reset_password):
        response = self.execute(variables={'email': self.user.email})
        response = response['data'][self.operation]

        self.assertOk(response)
        reset_password.assert_called_once()

    @mock.patch('app.authentication.emails.reset_password')
    def test_reset_password_invalid_email(self, reset_password):
        response = self.execute(variables={'email': 'takeshi@kovacs.com'})

        self.assertNotFound(response)
        reset_password.assert_not_called()


class ResetPasswordConfirmTests(cases.GraphQLTestCase):
    """Test cases for changing the user password.
    """
    authenticated = False
    operation = 'resetPasswordConfirm'
    statement = '''
    mutation resetPasswordConfirm(
      $password: String!,
      $uid: Int!,
      $token: String!,
    ) {
      resetPasswordConfirm(
        password: $password,
        uid: $uid,
        token: $token
      ) {
        ok
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    def make_payload(self, **overrides):
        token = default_token_generator.make_token(self.user)
        payload = {
            'password': 'correctbatteryhorsestaple',
            'uid': self.user.id,
            'token': token,
        }
        payload.update(overrides)
        return payload

    @mock.patch('app.authentication.emails.password_was_reset')
    def test_reset_password(self, password_was_reset):
        variables = self.make_payload()

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        password_was_reset.assert_called_once_with(self.user.email)
        self.user.refresh_from_db()

        self.assertOk(response)
        self.assertTrue(self.user.check_password(variables['password']))
        self.assertFalse(default_token_generator.check_token(self.user, variables['token']))

    @mock.patch('app.authentication.emails.password_was_reset')
    def test_reset_password_invalid_token(self, password_was_reset):
        variables = self.make_payload(token=str(uuid.uuid4()))

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ok': False,
            'errors': [
                {
                    'resource': 'User',
                    'field': 'password_reset_token',
                    'code': 'invalid',
                },
            ],
        })

        password_was_reset.assert_not_called()
        self.user.refresh_from_db()

        self.assertFalse(self.user.check_password(variables['password']))

    @mock.patch('app.authentication.emails.password_was_reset')
    def test_reset_password_expired_token(self, password_was_reset):
        variables = self.make_payload()

        with freeze_time(str(dt.datetime.utcnow() + dt.timedelta(days=4))):
            response = self.execute(variables=variables)
            response = response['data'][self.operation]

            self.assertEqual(response, {
                'ok': False,
                'errors': [
                    {
                        'resource': 'User',
                        'field': 'password_reset_token',
                        'code': 'invalid',
                    },
                ],
            })

            password_was_reset.assert_not_called()
            self.user.refresh_from_db()

            self.assertFalse(self.user.check_password(variables['password']))

    @mock.patch('app.authentication.emails.password_was_reset')
    def test_reset_password_not_valid(self, password_was_reset):
        variables = self.make_payload(password='password')

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ok': False,
            'errors': [
                {
                    'resource': 'User',
                    'field': 'password',
                    'code': 'invalid',
                },
            ],
        })

        password_was_reset.assert_not_called()
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(variables['password']))


class LoginWithSSOTokenTests(cases.GraphQLTestCase):
    """Test cases logging in with an SSO token.
    """
    authenticated = False
    operation = 'loginWithSSOToken'
    statement = '''
    mutation LoginWithSSOToken($uid: Int!, $token: String!) {
      loginWithSSOToken(
        uid: $uid,
        token: $token
      ) {
        jwt
      }
    }
    '''

    def test_valid_token(self):
        """It should redirect with a valid token.
        """
        self.user.set_sso_access_token(True)

        variables = {
            'uid': self.user.pk,
            'token': str(self.user.sso_access_token),
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertValidJsonWebToken(response['jwt'])

    def test_with_fake_token(self):
        """It should not redirect if the token is invalid.
        """
        variables = {
            'uid': self.user.pk,
            'token': str(uuid.uuid4()),
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertIsNone(response['jwt'])

    def test_with_expired_token(self):
        """It should not redirect if the token has expired.
        """
        self.user.set_sso_access_token(False)
        self.user.sso_access_token_issued_at = timezone.now() - dt.timedelta(minutes=30)
        self.user.save()

        variables = {
            'uid': self.user.pk,
            'token': str(self.user.sso_access_token),
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertIsNone(response['jwt'])


class TokenAuthTests(cases.GraphQLTestCase):
    """Test cases for logging in with a password.
    """
    authenticated = False
    operation = 'tokenAuth'
    statement = '''
    mutation AuthenticateUser($email: String!, $password: String!) {
      tokenAuth(
        email: $email,
        password: $password
      ) {
        token
      }
    }
    '''

    def test_valid_password(self):
        variables = {
            'email': 'owner@metamapper.io',
            'password': 'password1234',
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertValidJsonWebToken(response['token'])

    def test_invalid_password(self):
        variables = {
            'email': 'scott@metamapper.io',
            'password': 'notavalidpassword',
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, None)


class UpdateUserProfileTests(cases.GraphQLTestCase):
    """Test cases for updating metadata about the current user.
    """
    operation = 'updateCurrentUser'
    statement = '''
    mutation updateUserProfile(
      $fname: String,
      $lname: String,
      $email: String,
      $currentPassword: String!,
    ) {
      updateCurrentUser(input: {
        fname: $fname,
        lname: $lname,
        email: $email,
        currentPassword: $currentPassword,
      }) {
        user {
          fname
          lname
          email
        }
        jwt
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    def test_update(self):
        variables = {
            'fname': 'Burton',
            'lname': 'Guster',
            'email': 'owner@metamapper.io',
            'currentPassword': 'password1234',
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response['user'], {
            'fname': variables['fname'],
            'lname': variables['lname'],
            'email': variables['email'],
        })

        self.assertValidJsonWebToken(response['jwt'])
        self.assertEqual(response['errors'], None)
        self.assertInstanceUpdated(self.user, **variables)

    def test_update_incorrect_current_password(self):
        variables = {
            'fname': 'Burton',
            'lname': 'Guster',
            'email': 'burton.guster@metamapper.io',
            'currentPassword': 'definitelynotmaypassword',
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'user': None,
            'jwt': None,
            'errors': [
                {
                    'resource': 'User',
                    'field': 'current_password',
                    'code': 'wrong_password',
                },
            ],
        })

        self.assertInstanceNotUpdated(self.user, **variables)

    def test_update_duplicate_email(self):
        variables = {
            'email': self.users['MEMBER'].email,
            'currentPassword': 'password1234',
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'user': None,
            'jwt': None,
            'errors': [
                {
                    'resource': 'User',
                    'field': 'email',
                    'code': 'exists',
                },
            ],
        })


class UpdateUserPasswordTests(cases.GraphQLTestCase):
    """Test cases for updating metadata about the current user.
    """
    operation = 'updateCurrentUser'
    statement = '''
    mutation updateUserPassword(
      $password: String!,
      $currentPassword: String!,
    ) {
      updateCurrentUser(input: {
        password: $password,
        currentPassword: $currentPassword,
      }) {
        user {
          fname
          lname
          email
        }
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    def test_update(self):
        variables = {
            'password': 'correctbatteryhorsestaple',
            'currentPassword': 'password1234',
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(variables['password']))

        self.assertEqual(response, {
            'user': {
                'fname': self.user.fname,
                'lname': self.user.lname,
                'email': self.user.email,
            },
            'errors': None,
        })

    def test_update_incorrect_current_password(self):
        variables = {
            'password': 'correctbatteryhorsestaple',
            'currentPassword': 'definitelynotmaypassword',
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'user': None,
            'errors': [
                {
                    'resource': 'User',
                    'field': 'current_password',
                    'code': 'wrong_password',
                },
            ],
        })

        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(variables['password']))
