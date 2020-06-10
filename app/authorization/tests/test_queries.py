# -*- coding: utf-8 -*-
import testutils.cases as cases
import testutils.factories as factories
import testutils.helpers as helpers
import testutils.decorators as decorators


class TestGetWorkspaceUsers(cases.GraphQLTestCase):
    """Test cases for fetching a list of workspace users.
    """
    factory = factories.WorkspaceFactory
    operation = 'workspaceUsers'
    statement = '''
    query getWorkspaceUsers($workspaceId: ID!) {
      workspaceUsers(workspaceId: $workspaceId) {
        edges {
          node {
            name
            email
            permissions
          }
        }
        totalCount
      }
    }
    '''

    @decorators.as_someone(['READONLY', 'MEMBER', 'OWNER'])
    def test_query_when_has_active_membership(self):
        node_id = helpers.to_global_id('WorkspaceType', self.workspace.pk)
        results = self.execute(self.statement, variables={'workspaceId': node_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.workspace.team_members.count(),
            msg="Node count should equal the number of team members."
        )

        self.assertEqual(
            first=results['totalCount'],
            second=len(results['edges']),
            msg="Node count should equal totalCount field."
        )

    @decorators.as_someone(['READONLY', 'MEMBER', 'OWNER'])
    def test_query_with_orphan_membership(self):
        """Tests when an email is invited that does not have an associated User.
        """
        email = 'kevin.malone@dunder-mifflin.com'
        membership, created = self.workspace.grant_membership(email, 'MEMBER')

        node_id = helpers.to_global_id('WorkspaceType', self.workspace.pk)
        results = self.execute(self.statement, variables={'workspaceId': node_id})
        results = results['data'][self.operation]
        members = self.workspace.memberships.all()

        self.assertEqual(
            first=len(results['edges']),
            second=members.count(),
            msg="Node count should equal the number of team members."
        )

        self.assertEqual(
            first=results['totalCount'],
            second=len(results['edges']),
            msg="Node count should equal totalCount field."
        )

        output = next(filter(lambda m: m['node']['email'] == email, results['edges']))

        self.assertIsNone(
            output['node']['name'],
            msg="Output should contain User without a name."
        )

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_has_no_membership(self):
        node_id = helpers.to_global_id('WorkspaceType', self.workspace.pk)
        results = self.execute(self.statement, variables={'workspaceId': node_id})

        self.assertPermissionDenied(results)
        self.assertIsNone(
            results['data'][self.operation],
            msg="Nothing should return if User is not a member of the Workspace.",
        )
