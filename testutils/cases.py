# -*- coding: utf-8 -*-
import factory
import json

from django.core.management import call_command
from django.db.utils import IntegrityError, DataError
from django.test import TestCase
from django.utils.crypto import get_random_string

from app.authentication.models import User, Workspace
from app.api.models import ApiToken

from utils.regexp import jwt_regex

from testutils.helpers import api_client, graphql_client
from testutils.assertions import EmailAssertionsMixin, InstanceAssertionsMixin


class UserFixtureMixin(object):
    load_data = ['workspaces.json', 'users.json']

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata', *cls.load_data, **{'verbosity': 0})

        cls.workspace = Workspace.objects.get(slug="dunder-mifflin")
        cls.workspace.save()

        cls.other_workspace = Workspace.objects.get(slug="acmecorp")
        cls.other_workspace.save()

        user_kwargs = {
            'OWNER': 'owner@metamapper.io',
            'MEMBER': 'member@metamapper.io',
            'READONLY': 'readonly@metamapper.io',
            'OUTSIDER': 'outsider@metamapper.io',
        }

        cls.users = {}
        for permissions, email in user_kwargs.items():
            cls.users[permissions] = User.objects.get(email=email)
            cls.users[permissions].set_password(cls.users[permissions].password)
            cls.users[permissions].save()

        cls.users_list = list(cls.users.values())
        cls.users['ANONYMOUS'] = None
        cls.user_type = 'OWNER'
        cls.user = cls.users[cls.user_type]
        cls.staff = cls.users['MEMBER']
        cls.owner = cls.users['OWNER']
        cls.team_list = [cls.staff, cls.owner]


class ModelTestCase(TestCase):
    """Mixin for model test cases.
    """
    factory = None
    model_class = None

    def setUp(self):
        self.attrs = factory.build(dict, FACTORY_CLASS=self.factory)

    def validate_uniqueness_of(self, attr, **kwargs):
        """Test for unique constraint on DB model.
        """
        resource = self.factory(**kwargs)
        attrs = attr if isinstance(attr, (list, tuple)) else [attr]
        attributes = self.attrs.copy()

        for a in attrs:
            attributes[a] = getattr(resource, a)
            attributes.update(kwargs)

        with self.assertRaises(IntegrityError) as ctx:
            self.model_class.objects.create(**attributes)

        self.assertTrue('violates unique constraint' in str(ctx.exception))

    def validate_max_length_of(self, attribute, value, **kwargs):
        """Test for unique length on DB model.
        """
        self._validate_length_of(attribute, value + 5, 'too long', **kwargs)

    def validate_min_length_of(self, attribute, value, **kwargs):
        """Test for unique length on DB model.
        """
        self._validate_length_of(attribute, value - 1, 'too short', **kwargs)

    def _validate_length_of(self, attribute, value, message, **kwargs):
        attributes = self.attrs.copy()
        attributes[attribute] = get_random_string(value)
        attributes.update(kwargs)

        with self.assertRaises(DataError) as ctx:
            self.model_class.objects.create(**attributes)

        self.assertTrue(message in str(ctx.exception))


class SerializerTestCase(InstanceAssertionsMixin, TestCase):
    """docstring for SerializerTestCase
    """
    serializer_resource_name = None

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        raise NotImplementedError('The `_get_attributes` method is not implemented.')

    def assertDjangoRestFrameworkRules(self, test_case_dict, **serializer_extras):
        """Simplify testing for DRF rules.
        """
        for field, test_cases in test_case_dict.items():
            for test_case in test_cases:
                attributes = self._get_attributes(**{field: test_case['value']})
                serializer = self.serializer_class(
                    data=attributes,
                    **serializer_extras
                )

                msg = '({code}) {field}={value}'.format(field=field, **test_case)

                self.assertFalse(serializer.is_valid(), msg)
                self.assertSerializerErrorsEqual(serializer, [
                    {
                        'resource': self.serializer_resource_name,
                        'field': field,
                        'code': test_case['code'],
                    },
                ], msg)

    def assertSerializerErrorsEqual(self, serializer, expectation, msg=None):
        """Compare errors of serializer to expected value.
        """
        self.assertEqual(json.loads(json.dumps(serializer.errors)), expectation, msg)


class GraphQLTestCase(UserFixtureMixin,
                      EmailAssertionsMixin,
                      InstanceAssertionsMixin,
                      TestCase):
    """Mixin for GraphQL test cases.
    """
    operation = None
    authenticated = True

    def setUp(self):
        super(GraphQLTestCase, self).setUp()
        self.set_graphql_client(
            user=self.users['OWNER'],
            workspace=self.workspace,
            authenticated=self.authenticated
        )

    def set_graphql_client(self, user, workspace=None, authenticated=True):
        self._client = graphql_client(
            user,
            uuid=(workspace.id if workspace else None),
            authenticated=authenticated)

    def execute(self, query=None, operation=None, variables=None):
        """
        Args:
            query (string) - GraphQL query to run
            op_name (string) - If the query is a mutation or named query, you must
                               supply the op_name.  For annon queries ("{ ... }"),
                               should be None (default).
            input (dict) - If provided, the $input variable in GraphQL will be set
                           to this value

        Returns:
            dict, response from graphql endpoint.  The response has the "data" key.
                  It will have the "error" key if any error happened.
        """
        if not query:
            query = self.statement
        body = {'query': query}
        if self.operation:
            body['operation_name'] = self.operation
        if operation:
            body['operation_name'] = operation
        if variables:
            body['variables'] = variables
        data = json.dumps(body)
        resp = self._client.post('/graphql', data, content_type='application/json')
        jresp = json.loads(resp.content.decode())
        return jresp

    def assertNotFound(self, response, message='Resource was not found.'):
        """Assert that the resource not found message is shown.
        """
        assert 'errors' in response.keys()
        assert message in str(response['errors'])

    def assertPermissionDenied(self, response):
        """Assert that the PermissionDenied error has been thrown.
        """
        assert 'errors' in response.keys()
        assert 'Permission denied' in str(response['errors'])

    def assertOk(self, response):
        """Boilerplate test for checking if something is okay.
        """
        self.assertEqual(response, {
            'ok': True,
            'errors': None,
        })

    def assertValidJsonWebToken(self, token):
        """Assert that the token provided is a valid JSON web token.
        """
        self.assertTrue(jwt_regex.match(token))


class ApiTestCase(UserFixtureMixin, TestCase):
    """Mixin for API test cases.
    """
    authenticated = True

    def setUp(self):
        super(ApiTestCase, self).setUp()
        self.api_token = ApiToken.objects.create(
            name='test-api-token',
            workspace=self.workspace,
            is_enabled=True,
            token=get_random_string(32).lower(),
        )
        self.api_token_secret = self.api_token.get_secret()
        self.set_api_client(
            token_secret=self.api_token_secret,
            workspace=self.workspace,
            authenticated=self.authenticated
        )

    def set_api_client(self, token_secret, workspace=None, authenticated=True):
        self.client = api_client(
            token_secret,
            uuid=(workspace.id if workspace else None),
            authenticated=authenticated)

    def assertOk(self, response):
        self.assertStatus(response, 200)

    def assertStatus(self, response, status_code):
        self.assertEqual(response.status_code, status_code)

    def assertPermissionDenied(self, response):
        self.assertStatus(response, 403)
        self.assertEqual(response.json(), {
            'success': False,
            'error': {
                'code': 403,
                'message': 'You do not have permission to perform this action.',
            },
        })

    def assertParameterValidationFailed(self, response):
        self.assertStatus(response, 400)
        self.assertEqual(response.json(), {
            'success': False,
            'error': {
                'code': 400,
                'message': 'Parameter validation failed.',
            },
        })

    def assertNotFound(self, response):
        self.assertStatus(response, 404)
        self.assertEqual(response.json(), {
            'success': False,
            'error': {
                'code': 404,
                'message': 'Resource could not be found.',
            },
        })
