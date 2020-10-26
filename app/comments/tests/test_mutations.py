# -*- coding: utf-8 -*-
import unittest.mock as mock

import app.comments.models as models
import app.comments.serializers as serializers
import app.audit.models as audit

import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories
import testutils.helpers as helpers


@mock.patch('app.omnisearch.tasks.update_single_es_object.delay')
class CreateCommentTests(cases.GraphQLTestCase):
    """Tests for creating a comment.
    """
    factory = factories.CommentFactory

    operation = 'createComment'
    statement = '''
    mutation CreateComment(
      $objectId: ID!,
      $html: String!,
      $parentId: ID,
    ) {
      createComment(input: {
        objectId: $objectId,
        html: $html,
        parentId: $parentId,
      }) {
        comment {
          html
          parent {
            pk
          }
        }
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
        self.resource = factories.ColumnFactory(workspace_id=self.workspace.pk)
        self.objectid = helpers.to_global_id('ColumnType', self.resource.pk)

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'objectId': self.objectid,
            'parentId': None,
            'html': ''.join(helpers.faker.sentences(nb=3)),
        }
        attributes.update(**overrides)
        return attributes

    def execute_success_test_case(self):
        """It should create the comment.
        """
        variables = self._get_attributes()

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'comment': {
                'html': variables['html'],
                'parent': None,
            },
            'errors': None
        })

        self.assertInstanceCreated(models.Comment, html=variables['html'])
        self.assertInstanceCreated(
            audit.Activity,
            verb='commented on',
            **serializers.get_audit_kwargs(models.Comment.objects.last()),
        )

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid(self, mock_es_update):
        """It should create the comment successfully.
        """
        self.execute_success_test_case()
        self.assertTrue(mock_es_update.called)

    @decorators.as_someone(['OWNER'])
    def test_valid_with_object_permission_as_owner(self, mock_es_update):
        """It should create the comment successfully.
        """
        self.resource.datastore.object_permissions_enabled = True
        self.resource.datastore.save()

        self.execute_success_test_case()
        self.assertTrue(mock_es_update.called)

    @decorators.as_someone(['MEMBER'])
    def test_valid_with_object_permission_as_member(self, mock_es_update):
        """It should create the comment successfully.
        """
        self.resource.datastore.object_permissions_enabled = True
        self.resource.datastore.save()

        permissions = [
            'definitions.change_datastore_settings',
            'definitions.comment_on_datastore',
            'definitions.change_datastore_metadata',
        ]

        for permission in permissions:
            self.resource.datastore.assign_perm(self.user, permission)

        self.execute_success_test_case()
        self.assertTrue(mock_es_update.called)

    @decorators.as_someone(['MEMBER'])
    def test_invalid_without_object_permission(self, mock_es_update):
        """It should return a "Permission Denied" error.
        """
        self.resource.datastore.object_permissions_enabled = True
        self.resource.datastore.save()

        permissions = [
            'definitions.change_datastore_settings',
            'definitions.change_datastore_metadata',
        ]

        for permission in permissions:
            self.resource.datastore.assign_perm(self.user, permission)

        variables = self._get_attributes()
        response = self.execute(variables=variables)

        self.assertPermissionDenied(response)
        self.assertFalse(mock_es_update.called)

    @decorators.as_someone(['READONLY'])
    def test_invalid_with_object_permission_as_readonly(self, mock_es_update):
        """It should return a "Permission Denied" error.
        """
        self.resource.datastore.object_permissions_enabled = True
        self.resource.datastore.save()

        permissions = [
            'definitions.comment_on_datastore',
            'definitions.change_datastore_metadata',
        ]

        for permission in permissions:
            self.resource.datastore.assign_perm(self.user, permission)

        variables = self._get_attributes()
        response = self.execute(variables=variables)

        self.assertPermissionDenied(response)
        self.assertFalse(mock_es_update.called)

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_when_invalid_html(self, mock_es_update):
        """It should NOT create the comment.
        """
        variables = self._get_attributes(html='')

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'comment': None,
            'errors': [
                {
                    'resource': 'Comment',
                    'field': 'html',
                    'code': 'blank',
                },
            ],
        })
        self.assertFalse(mock_es_update.called)

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_when_valid_parent(self, mock_es_update):
        """It should create the comment with a parent.
        """
        parent = factories.CommentFactory(content_object=self.resource)
        parent_id = helpers.to_global_id('CommentType', parent)
        variables = self._get_attributes(parentId=parent_id)

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'comment': {
                'html': variables['html'],
                'parent': {
                    'pk': parent.pk,
                },
            },
            'errors': None
        })

        self.assertInstanceCreated(models.Comment, html=variables['html'])
        self.assertInstanceCreated(
            audit.Activity,
            verb='commented on',
            **serializers.get_audit_kwargs(models.Comment.objects.last()),
        )
        self.assertTrue(mock_es_update.called)


@mock.patch('app.omnisearch.tasks.update_single_es_object.delay')
class UpdateCommentTests(cases.GraphQLTestCase):
    """Tests for updating a comment.
    """
    factory = factories.CommentFactory

    operation = 'updateComment'
    statement = '''
    mutation UpdateComment(
      $id: ID!,
      $html: String!,
    ) {
      updateComment(input: {
        id: $id,
        html: $html,
      }) {
        comment {
          pk
          html
        }
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
        self.resource = factories.ColumnFactory(workspace_id=self.workspace.pk)
        self.objectid = helpers.to_global_id('ColumnType', self.resource.pk)

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_when_valid_html(self, mock_es_update):
        """It should update the HTML of a comment.
        """
        resource = factories.CommentFactory(content_object=self.resource, author=self.user)
        globalid = helpers.to_global_id('CommentType', resource.pk)

        response = self.execute(variables={'id': globalid, 'html': '<p>This is valid html</p>'})
        response = response['data'][self.operation]

        self.assertInstanceUpdated(resource, html='<p>This is valid html</p>')
        self.assertEqual(response, {
            'comment': {
                'pk': resource.pk,
                'html': '<p>This is valid html</p>',
            },
            'errors': None,
        })

        self.assertInstanceCreated(
            audit.Activity,
            verb='updated comment on',
            **serializers.get_audit_kwargs(resource),
        )
        self.assertTrue(mock_es_update.called)

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_when_not_exists(self, mock_es_update):
        """It should return a 404 error.
        """
        globalid = helpers.to_global_id('CommentType', '1234')
        response = self.execute(variables={'id': globalid, 'html': 'Test'})

        self.assertPermissionDenied(response)
        self.assertFalse(mock_es_update.called)

    @decorators.as_someone(['OWNER', 'OUTSIDER', 'ANONYMOUS'])
    def test_update_other_user_comment(self, mock_es_update):
        """It should not update the comment of another user.
        """
        resource = factories.CommentFactory(content_object=self.resource, author=self.users['MEMBER'])
        globalid = helpers.to_global_id('CommentType', resource.pk)

        variables = {'id': globalid, 'html': 'Test'}
        response = self.execute(variables=variables)

        self.assertPermissionDenied(response)
        self.assertInstanceDoesNotExist(
            audit.Activity,
            verb='updated comment on',
            **serializers.get_audit_kwargs(resource),
        )
        self.assertFalse(mock_es_update.called)


@mock.patch('app.omnisearch.tasks.remove_single_es_object.delay')
class DeleteCommentTests(cases.GraphQLTestCase):
    """Tests for deleting a comment.
    """
    factory = factories.CommentFactory

    operation = 'deleteComment'
    statement = '''
    mutation DeleteComment(
        $id: ID!,
    ) {
        deleteComment(input: {
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

    def test_on_own_comment(self, mock_es_remove):
        """It should permanently delete the comment.
        """
        resource = self.factory(workspace_id=self.workspace.pk, author=self.user)
        globalid = helpers.to_global_id('CommentType', resource.pk)
        response = self.execute(variables={'id': globalid})
        response = response['data'][self.operation]

        self.assertOk(response)
        self.assertInstanceDeleted(models.Comment, pk=resource.pk)
        self.assertTrue(mock_es_remove.called)

    @decorators.as_someone(['MEMBER', 'ANONYMOUS'])
    def test_update_other_user_comment(self, mock_es_remove):
        """It should not delete the comment.
        """
        resource = self.factory(workspace_id=self.workspace.pk)
        globalid = helpers.to_global_id('CommentType', resource.pk)
        response = self.execute(variables={'id': globalid})

        self.assertPermissionDenied(response)
        self.assertFalse(mock_es_remove.called)

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_when_not_exists(self, mock_es_remove):
        """It should return a 404 error.
        """
        globalid = helpers.to_global_id('CommentType', '1234')
        response = self.execute(variables={'id': globalid, 'html': 'Test'})

        self.assertPermissionDenied(response)
        self.assertFalse(mock_es_remove.called)


class TogglePinnedCommentTests(cases.GraphQLTestCase):
    """Tests for pinning a comment.
    """
    factory = factories.CommentFactory

    operation = 'togglePinnedComment'
    statement = '''
    mutation TogglePinnedComment(
        $id: ID!,
    ) {
        togglePinnedComment(input: {
          id: $id,
        }) {
          comment {
            pk
            isPinned
            pinnedBy {
                email
            }
          }
          errors {
            resource
            field
            code
          }
        }
    }
    '''

    def execute_success_test_case(self, resource):
        """It should pin the comment.
        """
        globalid = helpers.to_global_id('CommentType', resource.pk)
        response = self.execute(variables={'id': globalid})
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'comment': {
                'pk': resource.pk,
                'isPinned': True,
                'pinnedBy': {
                    'email': self.user.email,
                }
            },
            'errors': None,
        })

    def test_when_not_pinned(self):
        """It should pin the comment.
        """
        resource = self.factory(workspace_id=self.workspace.pk, author=self.user)
        self.execute_success_test_case(resource)

    def test_when_pinned(self):
        """It should unpin the comment.
        """
        resource = self.factory(workspace_id=self.workspace.pk, author=self.user)
        resource.pin(self.user)

        globalid = helpers.to_global_id('CommentType', resource.pk)
        response = self.execute(variables={'id': globalid})
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'comment': {
                'pk': resource.pk,
                'isPinned': False,
                'pinnedBy': None,
            },
            'errors': None,
        })

    @decorators.as_someone(['OUTSIDER', 'READONLY'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        resource = self.factory(workspace_id=self.workspace.pk, author=self.user)
        globalid = helpers.to_global_id('CommentType', resource.pk)
        response = self.execute(variables={'id': globalid})
        self.assertPermissionDenied(response)

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid(self):
        """It should create the comment successfully.
        """
        resource = self.factory(workspace_id=self.workspace.pk, author=self.user)
        self.execute_success_test_case(resource)

    @decorators.as_someone(['OWNER'])
    def test_valid_with_object_permission_as_owner(self):
        """It should create the comment successfully.
        """
        resource = self.factory(workspace_id=self.workspace.pk, author=self.user)

        datastore = resource.content_object.datastore
        datastore.object_permissions_enabled = True
        datastore.save()

        self.execute_success_test_case(resource)

    @decorators.as_someone(['MEMBER'])
    def test_valid_with_object_permission_as_member(self):
        """It should create the comment successfully.
        """
        resource = self.factory(workspace_id=self.workspace.pk, author=self.user)

        datastore = resource.content_object.datastore
        datastore.object_permissions_enabled = True
        datastore.save()

        permissions = [
            'definitions.change_datastore_settings',
            'definitions.comment_on_datastore',
            'definitions.change_datastore_metadata',
        ]

        for permission in permissions:
            datastore.assign_perm(self.user, permission)

        self.execute_success_test_case(resource)

    @decorators.as_someone(['MEMBER'])
    def test_invalid_without_object_permission(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace_id=self.workspace.pk, author=self.user)
        globalid = helpers.to_global_id('CommentType', resource.pk)

        datastore = resource.content_object.datastore
        datastore.object_permissions_enabled = True
        datastore.save()

        permissions = [
            'definitions.change_datastore_settings',
            'definitions.change_datastore_metadata',
        ]

        for permission in permissions:
            datastore.assign_perm(self.user, permission)

        response = self.execute(variables={'id': globalid})
        self.assertPermissionDenied(response)

    @decorators.as_someone(['READONLY'])
    def test_invalid_with_object_permission_as_readonly(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace_id=self.workspace.pk, author=self.user)
        globalid = helpers.to_global_id('CommentType', resource.pk)

        datastore = resource.content_object.datastore
        datastore.object_permissions_enabled = True
        datastore.save()

        permissions = [
            'definitions.comment_on_datastore',
            'definitions.change_datastore_metadata',
        ]

        for permission in permissions:
            datastore.assign_perm(self.user, permission)

        response = self.execute(variables={'id': globalid})
        self.assertPermissionDenied(response)


class VoteForCommentTests(cases.GraphQLTestCase):
    """Tests for voting for a comment.
    """
    factory = factories.CommentFactory

    operation = 'voteForComment'
    statement = '''
    mutation VoteForComment(
        $id: ID!,
        $action: String!,
    ) {
        voteForComment(input: {
          id: $id,
          action: $action,
        }) {
          comment {
            pk
            numVoteUp
            numVoteDown
          }
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
        self.commentable = factories.TableFactory(workspace=self.workspace)

    @decorators.as_someone(['MEMBER', 'OWNER', 'READONLY'])
    def test_valid_upvote(self):
        resource = self.factory(content_object=self.commentable)
        globalid = helpers.to_global_id('CommentType', resource.pk)

        variables = {
            'id': globalid,
            'action': 1,
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'comment': {
                'pk': resource.pk,
                'numVoteUp': 1,
                'numVoteDown': 0,
            },
            'errors': None,
        })

    @decorators.as_someone(['MEMBER', 'OWNER', 'READONLY'])
    def test_valid_downvote(self):
        resource = self.factory(content_object=self.commentable)
        resource.upvote(self.user)

        global_id = helpers.to_global_id('CommentType', resource.pk)
        variables = {
            'id': global_id,
            'action': -1,
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'comment': {
                'pk': resource.pk,
                'numVoteUp': 0,
                'numVoteDown': 1,
            },
            'errors': None,
        })

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        resource = self.factory(content_object=self.commentable)
        globalid = helpers.to_global_id('CommentType', resource.pk)

        variables = {
            'id': globalid,
            'action': -1,
        }

        self.assertPermissionDenied(self.execute(variables=variables))


class UnvoteForCommentTests(cases.GraphQLTestCase):
    """Tests for removing a vote on a comment.
    """
    factory = factories.CommentFactory

    operation = 'unvoteForComment'
    statement = '''
    mutation UnvoteForComment(
        $id: ID!,
    ) {
        unvoteForComment(input: {
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
        self.commentable = factories.TableFactory(workspace=self.workspace)

    @decorators.as_someone(['MEMBER', 'OWNER', 'READONLY'])
    def test_valid(self):
        resource = self.factory(content_object=self.commentable)
        resource.upvote(self.user)

        global_id = helpers.to_global_id('CommentType', resource.pk)
        variables = {
            'id': global_id,
            'action': -1,
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertOk(response)
        self.assertIsNone(resource.get_vote(self.user))

    @decorators.as_someone(['MEMBER', 'OWNER', 'READONLY'])
    def test_when_no_vote(self):
        resource = self.factory(content_object=self.commentable)

        global_id = helpers.to_global_id('CommentType', resource.pk)
        variables = {
            'id': global_id,
            'action': -1,
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertOk(response)
        self.assertIsNone(resource.get_vote(self.user))

    @decorators.as_someone(['OUTSIDER', 'ANONYMOUS'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        resource = self.factory(content_object=self.commentable)
        globalid = helpers.to_global_id('CommentType', resource.pk)

        variables = {
            'id': globalid,
            'action': -1,
        }

        self.assertPermissionDenied(self.execute(variables=variables))
