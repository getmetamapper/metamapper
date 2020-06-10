# -*- coding: utf-8 -*-
import factory
import unittest.mock as mock

import app.sso.models as models
import app.sso.serializers as serializers
import app.authorization.constants as constants

import testutils.cases as cases
import testutils.helpers as helpers
import testutils.factories as factories


class SSOConnectionSerializerSaml2CreateTests(cases.SerializerTestCase):
    """Test cases for the SSOConnection serializer class.
    """
    factory = factories.SSOConnectionFactory
    serializer_class = serializers.SSOConnectionSerializer

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'id': models.SSOConnection.generate_primary_key(),
            'entity_id': 'urn:auth0:metamapper',
            'provider': models.SSOConnection.GENERIC,
            'sso_url': helpers.faker.uri(),
            'x509cert': factories.x509cert(),
            'default_permissions': constants.READONLY,
            'workspace': self.workspace,
            'extras': {
                'mappings': {
                    'user_id': 'identifier',
                    'user_email': 'user_email',
                    'fname': 'first_name',
                    'lname': 'last_name',
                },
            },
        }
        attributes.update(**overrides)
        return attributes

    def test_incorrect_provider(self):
        """It should only allow one of the accepted providers.
        """
        attributes = self._get_attributes(provider='GARBAGE')
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'SSOConnection',
                'field': 'provider',
                'code': 'invalid_choice',
            }
        ])

    def test_create_when_valid(self):
        """It should create a SSO Connection for each
        """
        attributes = self._get_attributes(provider=models.SSOConnection.GENERIC)
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(workspace=self.workspace))

    def test_invalid_extras_mappings(self):
        """It should not accept invalid mappings.
        """
        overrides = {
            'extras': {
                'user': 'ok',
                'whatever': 'one',
            }
        }

        attributes = self._get_attributes(**overrides)
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'SSOConnection',
                'field': 'mappings',
                'code': 'missing_user_id',
            }
        ])

    def test_when_sso_url_is_invalid(self):
        """General test for errors...
        """
        attributes = self._get_attributes(sso_url='not formatted correctly')
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'SSOConnection',
                'field': 'sso_url',
                'code': 'invalid',
            }
        ])

    def test_when_x509cert_is_missing(self):
        """General test for errors...
        """
        attributes = self._get_attributes(x509cert=None)
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'SSOConnection',
                'field': 'x509cert',
                'code': 'invalid',
            }
        ])


class SSOConnectionSerializerSaml2UpdateTests(cases.SerializerTestCase):
    """Test cases for the SSOConnection serializer class.
    """
    factory = factories.SSOConnectionFactory
    serializer_class = serializers.SSOConnectionSerializer

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.resource = cls.factory(provider=models.SSOConnection.GENERIC, workspace=cls.workspace)

    def test_contains_expected_fields(self):
        """It should respond with the correct fields.
        """
        serializer = self.serializer_class(self.resource)
        expected_fields = {
            'id',
            'entity_id',
            'sso_url',
            'is_enabled',
            'x509cert',
            'extras',
            'default_permissions',
            'provider',
            'created_at',
            'updated_at',
        }
        self.assertEqual(
            set(serializer.data.keys()),
            expected_fields,
        )

    def test_disable_connection(self):
        """It should not clear the extra parameters.
        """
        resource = self.factory(is_enabled=True, workspace=self.workspace)

        attributes = {'is_enabled': False}
        serializer = self.serializer_class(
            instance=resource,
            data=attributes,
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceUpdated(resource, **attributes)

    def test_update_entity_id(self):
        """It should not clear the extra parameters.
        """
        resource = self.factory(is_enabled=True, workspace=self.workspace)

        attributes = {'entity_id': None}
        serializer = self.serializer_class(
            instance=resource,
            data=attributes,
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'SSOConnection',
                'field': 'entity_id',
                'code': 'nulled',
            }
        ])


class SSOConnectionSerializerGoogleTests(cases.SerializerTestCase):
    """Test cases for the SSOConnection serializer class.
    """
    factory = factories.SSOConnectionFactory
    serializer_class = serializers.SSOConnectionSerializer

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'id': models.SSOConnection.generate_primary_key(),
            'entity_id': 'metamapper.io',
            'provider': models.SSOConnection.GOOGLE,
            'default_permissions': constants.READONLY,
            'extras': {'domain': 'metamapper.io'},
        }
        attributes.update(**overrides)
        return attributes

    @mock.patch.object(serializers.GoogleOAuth2ExtrasValidator, 'get_gsuite_domain')
    def test_create_when_valid(self, mock_google_call):
        """It should create the object.
        """
        domain = 'metamapper.io'
        mock_google_call.return_value = domain

        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(workspace=self.workspace))

    @mock.patch.object(serializers.GoogleOAuth2ExtrasValidator, 'get_gsuite_domain')
    def test_requires_extras_domain(self, mock_google_call):
        """It should throw an error if the domain is missing.
        """
        domain = 'metamapper.com'
        mock_google_call.return_value = domain

        attributes = self._get_attributes(extras={})
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {'resource': 'SSOConnection', 'field': 'domain', 'code': 'required'}
        ])

    @mock.patch.object(serializers.GoogleOAuth2ExtrasValidator, 'get_gsuite_domain')
    def test_extras_domain_is_unauthorized(self, mock_google_call):
        """It should throw an error if the domains do not match.
        """
        domain = 'metamapper.com'
        mock_google_call.return_value = domain

        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {'resource': 'SSOConnection', 'field': 'domain', 'code': 'authorized'}
        ])

    @mock.patch.object(serializers.GoogleOAuth2ExtrasValidator, 'get_gsuite_domain')
    def test_extras_domain_cannot_be_gmail(self, mock_google_call):
        """It should not allow `gmail.com` as a domain.
        """
        domain = 'gmail.com'
        mock_google_call.return_value = domain

        attributes = self._get_attributes(entity_id=domain, extras={'domain': domain})
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {'resource': 'SSOConnection', 'field': 'domain', 'code': 'authorized'}
        ])

    @mock.patch.object(serializers.GoogleOAuth2ExtrasValidator, 'get_gsuite_domain')
    def test_update_extras(self, mock_google_call):
        """It should not be able to update the `extras` field.
        """
        mock_google_call.return_value = 'google.com'

        resource = self.factory(
            provider=models.SSOConnection.GOOGLE,
            workspace=self.workspace,
            extras={'domain': 'metamapper.io'},
        )

        attributes = {'extras': {'domain': 'google.com'}}
        serializer = self.serializer_class(
            instance=resource,
            data=attributes,
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceNotUpdated(resource, **attributes)


class SSOConnectionSerializerGithubTests(cases.SerializerTestCase):
    """Test cases for the SSOConnection serializer class.
    """
    factory = factories.SSOConnectionFactory
    serializer_class = serializers.SSOConnectionSerializer

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'id': models.SSOConnection.generate_primary_key(),
            'entity_id': 'metamapper.io',
            'provider': models.SSOConnection.GITHUB,
            'default_permissions': constants.READONLY,
            'extras': {'ident': '123456', 'login': 'metamapper-io'},
        }
        attributes.update(**overrides)
        return attributes

    @mock.patch.object(serializers.GithubOAuth2ExtrasValidator, 'is_github_org_member')
    def test_create_when_valid(self, mock_github_call):
        """It should create the object.
        """
        mock_github_call.return_value = True

        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(workspace=self.workspace))

    @mock.patch.object(serializers.GithubOAuth2ExtrasValidator, 'is_github_org_member')
    def test_requires_extras_login(self, mock_github_call):
        mock_github_call.return_value = True

        attributes = self._get_attributes(extras={})
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {'resource': 'SSOConnection', 'field': 'ident', 'code': 'required'},
            {'resource': 'SSOConnection', 'field': 'login', 'code': 'required'}
        ])

    @mock.patch.object(serializers.GithubOAuth2ExtrasValidator, 'is_github_org_member')
    def test_extras_login_is_unauthorized(self, mock_github_call):
        mock_github_call.return_value = False

        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {'resource': 'SSOConnection', 'field': 'ident', 'code': 'invalid'}
        ])

    @mock.patch.object(serializers.GithubOAuth2ExtrasValidator, 'is_github_org_member')
    def test_update_extras(self, mock_github_call):
        """It should not be able to update the `extras` field.
        """
        resource = self.factory(
            provider=models.SSOConnection.GITHUB,
            workspace=self.workspace,
            extras={'ident': '541232131', 'login': 'metamapper-io'},
        )

        attributes = {'extras': {'ident': '9412312', 'login': 'metamapper-io'}}
        serializer = self.serializer_class(
            instance=resource,
            data=attributes,
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertInstanceNotUpdated(resource, **attributes)


class SSODomainSerializerCreateTests(cases.SerializerTestCase):
    """Test cases for the updating a SSODomain via serializer.
    """
    factory = factories.SSODomainFactory
    serializer_class = serializers.SSODomainSerializer

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()

    def test_contains_expected_fields(self):
        """It should respond with the correct fields.
        """
        resource = self.factory(workspace=self.workspace)
        serializer = self.serializer_class(resource)
        expected_fields = {
            'domain',
            'verified',
            'created_at',
        }
        self.assertEqual(
            set(serializer.data.keys()),
            expected_fields,
        )

    def test_create(self):
        """It should create a brand new SSO Domain.
        """
        attributes = factory.build(dict, FACTORY_CLASS=self.factory)
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(workspace=self.workspace))

    def test_format_of_domain(self):
        """It should validate domain format.
        """
        serializer = self.serializer_class(
            data={'domain': 'this is not a domain'},
        )
        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {'resource': 'SSODomain', 'field': 'domain', 'code': 'invalid'},
        ])


class SSODomainSerializerUpdateTests(cases.SerializerTestCase):
    """Test cases for the updating a SSODomain via serializer.
    """
    factory = factories.SSODomainFactory
    serializer_class = serializers.SSODomainSerializer

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.resource = cls.factory(workspace=cls.workspace)

    def test_update(self):
        """It should not be able to update an SSO Domain.
        """
        resource = self.factory(workspace=self.workspace)
        attributes = {
            'domain': 'metamapper.io',
        }
        serializer = self.serializer_class(
            resource,
            data=attributes,
            partial=True
        )

        self.assertTrue(serializer.is_valid())

        exc_msg = 'SSODomainSerializer cannot update resources.'

        with self.assertRaisesRegexp(NotImplementedError, exc_msg):
            serializer.save()

        self.assertInstanceNotUpdated(resource, **attributes)
