# -*- coding: utf-8 -*-
import testutils.cases as cases
import testutils.factories as factories
import testutils.helpers as helpers
import testutils.decorators as decorators


class TestGetMyWorkspaces(cases.GraphQLTestCase):
    """Test cases for retrieving existing workspace.
    """
    factory = factories.WorkspaceFactory
    operation = 'myWorkspaces'
    statement = '''
    query {
      myWorkspaces {
        edges {
          node {
            pk
            name
            slug
          }
        }
        totalCount
      }
    }
    '''

    def test_query(self):
        """It should return only the workspaces that the current User belongs to.
        """
        restricted_workspace = factories.WorkspaceFactory()
        restricted_workspace.grant_membership(self.users['OUTSIDER'], 'MEMBER')

        results = self.execute(self.statement)
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.user.workspaces.count(),
            msg="Node count should equal number of workspaces that the current user belongs to."
        )

        self.assertEqual(
            first=results['totalCount'],
            second=len(results['edges']),
            msg="Node count should equal totalCount field."
        )

        self.assertNotIn(
            str(restricted_workspace.pk),
            list(map(lambda m: m['node']['pk'], results['edges'])),
            msg="Workspace that the User is not a part of should be excluded."
        )


class TestGetWorkspaceByID(cases.GraphQLTestCase):
    """Test cases for fetching a specific workspace by ID.
    """
    factory = factories.WorkspaceFactory
    operation = 'workspace'
    statement = '''
    query getWorkspaceByID($id: ID!) {
      workspace(id: $id) {
        id
        pk
        name
        slug
      }
    }
    '''

    @decorators.as_someone(['READONLY', 'MEMBER', 'OWNER'])
    def test_query_when_has_active_membership(self):
        node_id = helpers.to_global_id('WorkspaceType', self.workspace.pk)
        results = self.execute(self.statement, variables={'id': node_id})
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'id': node_id,
            'pk': str(self.workspace.pk),
            'name': self.workspace.name,
            'slug': self.workspace.slug,
        })

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_has_no_membership(self):
        node_id = helpers.to_global_id('WorkspaceType', self.workspace.pk)
        results = self.execute(self.statement, variables={'id': node_id})

        self.assertIsNone(
            results['data'][self.operation],
            msg="Nothing should return if User is not a member of the Workspace.",
        )


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


class TestGetCurrentUser(cases.GraphQLTestCase):
    """Test cases for getting the current user.
    """
    operation = 'me'
    statement = '''
    query {
      me {
        id
        fname
        lname
        email
        currentMembership {
          permissions
        }
      }
    }
    '''

    def test_query_when_has_current_membership(self):
        """It should return the current user.
        """
        results = self.execute(self.statement)
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'id': helpers.to_global_id('UserType', self.user.pk),
            'fname': self.user.fname,
            'lname': self.user.lname,
            'email': self.user.email,
            'currentMembership': {
                'permissions': self.user.permissions_for(self.workspace),
            }
        })

    def test_query_when_has_no_memberships(self):
        self.set_api_client(self.users['OWNER'], None, True)

        results = self.execute(self.statement)
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'id': helpers.to_global_id('UserType', self.user.pk),
            'fname': self.user.fname,
            'lname': self.user.lname,
            'email': self.user.email,
            'currentMembership': None,
        })
