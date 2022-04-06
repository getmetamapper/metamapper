# -*- coding: utf-8 -*-
import testutils.cases as cases
import testutils.factories as factories
import testutils.decorators as decorators


class TestGetApiTokens(cases.GraphQLTestCase):
    """Test cases for listing API tokens associated with a workspace.
    """
    factory = factories.ApiTokenFactory
    operation = 'apiTokens'
    statement = '''
    query GetApiTokens {
      apiTokens {
        edges {
          node {
            name
            isEnabled
          }
        }
        totalCount
      }
    }
    '''

    def setUp(self):
        super(TestGetApiTokens, self).setUp()

        self.count = 5
        self.api_tokens = self.factory.create_batch(
            self.count,
            workspace=self.workspace,
        )

    @decorators.as_someone(['OWNER'])
    def test_query_when_authorized(self):
        results = self.execute(self.statement)
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg="Node count should equal number of API tokens."
        )

        self.assertEqual(
            first=len(results['edges']),
            second=results['totalCount'],
            msg="Node count should equal totalCount field."
        )

    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        self.assertPermissionDenied(self.execute(self.statement))

    @decorators.as_someone(['OWNER'])
    def test_query_with_secret(self):
        results = self.execute('''
        query GetApiTokens {
          apiTokens {
            edges {
              node {
                name
                isEnabled
                secret
              }
            }
          }
        }
        ''')

        self.assertEqual(results['errors'], [
            {
                'message': 'Cannot query field "secret" on type "ApiTokenType".',
                'locations': [{'line': 8, 'column': 17}],
                'status': 400,
            },
        ])
