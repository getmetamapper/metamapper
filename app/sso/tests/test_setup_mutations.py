# -*- coding: utf-8 -*-
import app.sso.models as models
import app.authorization.constants as constants

import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories
import testutils.helpers as helpers


class CreateSSOConnectionTests(cases.GraphQLTestCase):
    """Tests for creating a connection for Single Sign-On.
    """
    operation = 'createSSOConnection'
    statement = '''
    mutation CreateSSOConnection(
      $id: String!,
      $provider: String!,
      $entityId: String!,
      $defaultPermissions: String!,
      $ssoUrl: String,
      $x509cert: String,
      $extras: JSONObject,
    ) {
      createSSOConnection(input: {
        id: $id,
        provider: $provider,
        entityId: $entityId,
        defaultPermissions: $defaultPermissions,
        ssoUrl: $ssoUrl,
        x509cert: $x509cert,
        extras: $extras,
      }) {
        ssoConnection {
          pk
          provider
          entityId
          ssoUrl
          defaultPermissions
        }
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'id': models.SSOConnection.generate_primary_key(),
            'provider': models.SSOConnection.GENERIC,
            'entityId': 'urn:auth0:metamapper-io',
            'defaultPermissions': constants.MEMBER,
            'ssoUrl': helpers.faker.uri(),
            'x509cert': factories.x509cert(),
            'extras': {},
        }
        attributes.update(**overrides)
        return attributes

    @decorators.as_someone(['OWNER'])
    def test_with_saml2(self):
        """It should create the SAML2.0 connection.
        """
        variables = self._get_attributes(extras={
            'mappings': {
                'user_id': 'user_id',
                'user_email': 'user_email',
                'fname': 'first_name',
                'lname': 'last_name',
            }
        })

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ssoConnection': {
                'pk': variables['id'],
                'provider': variables['provider'],
                'entityId': variables['entityId'],
                'ssoUrl': variables['ssoUrl'],
                'defaultPermissions': variables['defaultPermissions'],
            },
            'errors': None
        })

        self.assertInstanceCreated(models.SSOConnection, id=variables['id'])

    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        variables = self._get_attributes()
        self.assertPermissionDenied(self.execute(variables=variables))


class UpdateSSOConnectionTests(cases.GraphQLTestCase):
    """Tests for updating a connection for Single Sign-On.
    """
    factory = factories.SSOConnectionFactory
    operation = 'updateSSOConnection'
    statement = '''
    mutation UpdateSSOConnection(
      $id: ID!,
      $entityId: String,
      $ssoUrl: String,
      $extras: JSONObject,
      $x509cert: String,
      $defaultPermissions: String,
    ) {
      updateSSOConnection(input: {
        id: $id,
        entityId: $entityId,
        ssoUrl: $ssoUrl,
        extras: $extras,
        x509cert: $x509cert,
        defaultPermissions: $defaultPermissions,
      }) {
        ssoConnection {
          id
          pk
          name
          defaultPermissions
          extras
        }
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    @decorators.as_someone(['OWNER'])
    def test_valid(self):
        """It should permanently delete the datastore.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('SSOConnectionType', resource.pk)

        variables = {
            'id': globalid,
            'defaultPermissions': 'OWNER',
            'extras': {
                'mappings': {
                    'user_id': 'http://schemas.auth0.com/identifier',
                    'user_email': 'http://schemas.auth0.com/email',
                    'fname': 'http://schemas.auth0.com/first_name',
                    'lname': 'http://schemas.auth0.com/first_name',
                }
            },
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ssoConnection': {
                'id': globalid,
                'pk': resource.pk,
                'name': 'generic-{}'.format(resource.pk),
                'defaultPermissions': variables['defaultPermissions'],
                'extras': variables['extras'],
            },
            'errors': None,
        })

        self.assertInstanceUpdated(
            instance=resource,
            default_permissions=variables['defaultPermissions'],
            extras=variables['extras'],
        )

    @decorators.as_someone(['OWNER'])
    def test_invalid(self):
        """It should permanently delete the datastore.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('SSOConnectionType', resource.pk)

        variables = {
            'id': globalid,
            'defaultPermissions': 'OWNER',
            'extras': {
                'mappings': {
                    'user_id': 'http://schemas.auth0.com/identifier',
                    'user_email': 'http://schemas.auth0.com/email',
                    'fname': 'http://schemas.auth0.com/first_name',
                }
            },
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ssoConnection': None,
            'errors': [
                {
                    'resource': 'SSOConnection',
                    'field': 'mappings',
                    'code': 'missing_lname',
                },
            ]
        })

        self.assertInstanceNotUpdated(
            instance=resource,
            default_permissions=variables['defaultPermissions'],
            extras=variables['extras'],
        )

    def test_not_found(self):
        """It should permanently delete the sso connection.
        """
        globalid = helpers.to_global_id('SSOConnectionType', '12345')
        response = self.execute(variables={'id': globalid})

        self.assertPermissionDenied(response)

    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('SSOConnectionType', resource.pk)
        response = self.execute(variables={'id': globalid})
        self.assertPermissionDenied(response)


class DeleteSSOConnectionTests(cases.GraphQLTestCase):
    """Tests for deleting a connection for Single Sign-On.
    """
    factory = factories.SSOConnectionFactory
    operation = 'removeSSOConnection'
    statement = '''
    mutation DeleteSSOConnection(
      $id: ID!,
    ) {
      removeSSOConnection(input: {
        id: $id,
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

    @decorators.as_someone(['OWNER'])
    def test_valid(self):
        """It should permanently delete the ssoConnection.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('SSOConnectionType', resource.pk)
        response = self.execute(variables={'id': globalid})
        response = response['data'][self.operation]

        self.assertOk(response)
        self.assertInstanceDeleted(
            model_class=models.SSOConnection,
            pk=resource.pk,
            workspace_id=self.workspace.id,
        )

    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('SSOConnectionType', resource.pk)
        response = self.execute(variables={'id': globalid})
        self.assertPermissionDenied(response)


class SetDefaultSSOConnectionTests(cases.GraphQLTestCase):
    """Tests for setting the default SSO connection for the workspace.
    """
    operation = 'setDefaultSSOConnection'
    statement = '''
    mutation SetDefaultSSOConnection(
      $connection: String,
    ) {
      setDefaultSSOConnection(input: {
        connection: $connection,
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

    def setUp(self):
        super().setUp()
        self.connection = factories.SSOConnectionFactory(
            workspace=self.workspace,
            provider=models.SSOConnection.GENERIC,
            is_enabled=True,
            entity_id='urn:auth0:metamapper',
            x509cert=None,
            extras={
                'mappings': {
                    'user_id': 'identifier',
                    'user_email': 'user_email',
                    'fname': 'first_name',
                    'lname': 'last_name',
                },
            },
        )

    @decorators.as_someone(['OWNER'])
    def test_valid(self):
        response = self.execute(variables={'connection': self.connection.pk})
        response = response['data'][self.operation]

        self.workspace.refresh_from_db()

        self.assertOk(response)
        self.assertEqual(self.workspace.active_sso_id, self.connection.pk)

    @decorators.as_someone(['OWNER'])
    def test_does_not_exist(self):
        response = self.execute(variables={'connection': '12345'})

        self.workspace.refresh_from_db()

        self.assertNotFound(response)
        self.assertNotEqual(self.workspace.active_sso_id, self.connection.pk)

    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        response = self.execute(variables={'connection': self.connection.pk})

        self.workspace.refresh_from_db()

        self.assertPermissionDenied(response)
        self.assertNotEqual(self.workspace.active_sso_id, self.connection.pk)


class CreateSSODomainTests(cases.GraphQLTestCase):
    """Tests for creating a domain for Single Sign-On.
    """
    operation = 'createSSODomain'
    statement = '''
    mutation CreateSSODomain(
      $domain: String!,
    ) {
      createSSODomain(input: {
        domain: $domain,
      }) {
        ssoDomain {
          domain
          isVerified
        }
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    @decorators.as_someone(['OWNER'])
    def test_valid_domain(self):
        """It should create the SSODomain instance.
        """
        domain = helpers.faker.domain_name()

        response = self.execute(variables={'domain': domain})
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ssoDomain': {
                'domain': domain,
                'isVerified': False,
            },
            'errors': None
        })

        self.assertInstanceCreated(models.SSODomain, domain=domain)

    @decorators.as_someone(['OWNER'])
    def test_invalid_domain(self):
        """It should not create the SSODomain instance.
        """
        domain = 'not-a-domain'

        response = self.execute(variables={'domain': domain})
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ssoDomain': None,
            'errors': [
                {
                    'code': 'invalid',
                    'field': 'domain',
                    'resource': 'SSODomain',
                }
            ]
        })

        self.assertInstanceDoesNotExist(models.SSODomain, domain=domain)

    @decorators.as_someone(['OWNER'])
    def test_duplicate_domain(self):
        """It should not create the SSODomain instance.
        """
        domain = factories.SSODomainFactory()

        response = self.execute(variables={'domain': domain.domain})
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ssoDomain': None,
            'errors': [
                {
                    'code': 'unique',
                    'field': 'domain',
                    'resource': 'SSODomain',
                }
            ]
        })

        self.assertInstanceDoesNotExist(
            model_class=models.SSODomain,
            domain=domain,
            workspace_id=self.workspace.id,
        )

    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should raise a PermissionDenied.
        """
        domain = helpers.faker.domain_name()
        response = self.execute(variables={'domain': domain})

        self.assertPermissionDenied(response)


class RemoveSSODomainTests(cases.GraphQLTestCase):
    """Tests for removing a domain for Single Sign-On.
    """
    operation = 'removeSSODomain'
    statement = '''
    mutation DeleteSSODomain(
      $id: ID!,
    ) {
      removeSSODomain(input: {
        id: $id,
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

    def setUp(self):
        super().setUp()
        self.resource = factories.SSODomainFactory(workspace=self.workspace)
        self.global_id = helpers.to_global_id('SSODomainType', self.resource.pk)

    @decorators.as_someone(['OWNER'])
    def test_valid_removal(self):
        """It should raise a PermissionDenied.
        """
        response = self.execute(variables={'id': self.global_id})
        response = response['data'][self.operation]

        self.assertOk(response)
        self.assertInstanceDeleted(
            model_class=models.SSODomain,
            pk=self.resource.pk,
            workspace_id=self.workspace.id,
        )

    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should raise a PermissionDenied.
        """
        self.assertPermissionDenied(
            self.execute(variables={'id': self.global_id})
        )

    @decorators.as_someone(['OWNER'])
    def test_does_not_exist(self):
        """It should return a "Resource Not Found" error.
        """
        response = self.execute(variables={'id': '12345'})
        self.assertNotFound(response)
