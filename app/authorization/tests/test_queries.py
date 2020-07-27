# -*- coding: utf-8 -*-
import app.authorization.models as models

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


class TestGetGroups(cases.GraphQLTestCase):
    """Test cases for fetching a list of workspace groups.
    """
    factory = factories.GroupFactory
    operation = 'workspaceGroups'
    statement = '''
    query getWorkspaceGroups {
      workspaceGroups {
        edges {
          node {
            pk
            name
            description
            createdAt
          }
        }
        totalCount
      }
    }
    '''

    def setUp(self):
        super(TestGetGroups, self).setUp()

        models.Group.objects.all().delete()

        self.count = 5
        self.groups = self.factory.create_batch(self.count, workspace=self.workspace)
        self.other_group = self.factory(workspace=self.other_workspace)

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_when_authorized(self):
        results = self.execute(self.statement)
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg="Node count should equal number of active datastores."
        )

        self.assertEqual(
            first=len(results['edges']),
            second=results['totalCount'],
            msg="Node count should equal totalCount field."
        )

        self.assertNotIn(
            self.other_group.pk,
            map(lambda g: g['node']['pk'], results['edges']),
        )

    @decorators.as_someone(['OUTSIDER', 'ANONYMOUS'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        self.assertPermissionDenied(self.execute(self.statement))


class TestGetGroup(cases.GraphQLTestCase):
    """Test cases for fetching a specific group.
    """
    factory = factories.GroupFactory
    operation = 'workspaceGroup'
    statement = '''
    query workspaceGroup($id: ID!) {
      workspaceGroup(id: $id) {
        name
        description
        createdAt
      }
    }
    '''

    def setUp(self):
        super(TestGetGroup, self).setUp()

        self.group = self.factory(workspace=self.workspace)
        self.global_id = helpers.to_global_id('GroupType', self.group.pk)

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_when_authorized(self):
        results = self.execute(self.statement, variables={'id': self.global_id})
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'name': self.group.name,
            'description': self.group.description,
            'createdAt': str(self.group.created_at).replace(' ', 'T'),
        })

    @decorators.as_someone(['OUTSIDER', 'ANONYMOUS'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        results = self.execute(self.statement, variables={'id': self.global_id})
        self.assertPermissionDenied(results)


class TestGetGroupUsers(cases.GraphQLTestCase):
    """Test cases for fetching the users that belong to specific group.
    """
    factory = factories.GroupFactory
    operation = 'workspaceGroupUsers'
    statement = '''
    query getWorkspaceGroupUsers($groupId: ID!) {
      workspaceGroupUsers(groupId: $groupId) {
        edges {
          node {
            pk
            name
            email
          }
        }
        totalCount
      }
    }
    '''

    def setUp(self):
        super(TestGetGroupUsers, self).setUp()

        self.group = self.factory(workspace=self.workspace)
        self.global_id = helpers.to_global_id('GroupType', self.group.pk)

        self.user_set = [self.users['MEMBER'], self.users['READONLY']]
        for u in self.user_set:
            self.group.user_set.add(u)

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_when_authorized(self):
        results = self.execute(self.statement, variables={'groupId': self.global_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=len(self.user_set),
            msg="Node count should equal number of active datastores."
        )

        self.assertEqual(
            first=len(results['edges']),
            second=results['totalCount'],
            msg="Node count should equal totalCount field."
        )

        self.assertNotIn(
            self.users['OWNER'].pk,
            map(lambda g: g['node']['pk'], results['edges']),
        )

    @decorators.as_someone(['OUTSIDER', 'ANONYMOUS'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        results = self.execute(self.statement, variables={'groupId': self.global_id})
        self.assertPermissionDenied(results)
