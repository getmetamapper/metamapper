# -*- coding: utf-8 -*-
import random

import testutils.cases as cases
import testutils.factories as factories
import testutils.helpers as helpers
import testutils.decorators as decorators

from app.comments.models import Comment
from django.contrib.contenttypes.models import ContentType


class TestGetComments(cases.GraphQLTestCase):
    """Test cases for retrieving existing workspace.
    """
    factory = factories.WorkspaceFactory
    operation = 'comments'
    statement = '''
    query getComments(
      $objectId: ID!,
    ) {
      comments(objectId: $objectId) {
        edges {
          node {
            id
            html
            numVoteUp
            numVoteDown
            author {
              name
              email
              isCurrentUser
            }
            createdAt
            pinnedAt
            pinnedBy {
              name
            }
            childComments {
              id
              html
              numVoteUp
              numVoteDown
              author {
                name
                email
                isCurrentUser
              }
              createdAt
            }
          }
        }
        totalCount
      }
    }
    '''

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query(self):
        """It should return only the workspaces that the current User belongs to.
        """
        table = factories.TableFactory(workspace=self.workspace)
        count = 3

        content_type = ContentType.objects.get(model='table')

        for co in range(count):
            comment = Comment.objects.create(
                author=random.choice(self.users_list),
                html='Test',
                workspace=self.workspace,
                object_id=table.pk,
                content_type_id=content_type.pk,
                parent=None,
            )

            for c in range(count):
                Comment.objects.create(
                    author=random.choice(self.users_list),
                    html='Nested',
                    parent=comment,
                    object_id=table.pk,
                    content_type_id=content_type.pk,
                    workspace=self.workspace,
                )

        global_id = helpers.to_global_id('TableType', table.pk)
        variables = {'objectId': global_id}

        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=count,
            msg="Node count should equal number of active comments."
        )

        self.assertEqual(
            first=len(results['edges']),
            second=results['totalCount'],
            msg="Node count should equal totalCount field."
        )

        self.assertEqual(
            len(results['edges'][0]['node']['childComments']),
            count,
        )

    @decorators.as_someone(['OUTSIDER', 'ANONYMOUS'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        table = factories.TableFactory(workspace=self.workspace)
        global_id = helpers.to_global_id('TableType', table.pk)
        variables = {'objectId': global_id}
        results = self.execute(self.statement, variables=variables)
        self.assertPermissionDenied(results)
