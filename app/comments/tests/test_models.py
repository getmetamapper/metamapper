# -*- coding: utf-8 -*-
import app.comments.models as models

import testutils.cases as cases
import testutils.helpers as helpers
import testutils.factories as factories

from app.votes.tests.test_models import VoteableTestsMixin
from app.definitions.models import Table, Column


class CommentTests(VoteableTestsMixin, cases.ModelTestCase):
    """Test cases for the Comment model class.
    """
    factory = factories.CommentFactory
    model_class = models.Comment

    def test_commentable_types(self):
        """Snapshot test for what models are voteable.
        """
        self.assertEqual(
            {Table, Column},
            set(self.model_class.commentable_types()),
        )

    def test_saves_with_workspace_id(self):
        """It should automatically add the workspace of the ContentObject.
        """
        user = factories.UserFactory()
        commentable = factories.TableFactory()

        properties = {
            'content_object': commentable,
            'author': user,
            'html': helpers.faker.sentence(),
        }

        comment = self.model_class.objects.create(**properties)

        self.assertEqual(
            comment.workspace_id,
            commentable.workspace_id,
        )

    def test_pin(self):
        """It should mark the `pinned_at` timestamp.
        """
        user = factories.UserFactory()
        comment = self.factory()
        comment.pin(user)
        pinned_at = comment.pinned_at
        self.assertTrue(pinned_at is not None)
        self.assertTrue(comment.pinned)

        comment.pin(user)
        self.assertTrue(pinned_at, comment.pinned_at)


class CommentableTestsMixin(object):
    """Test cases for a class that has commenting abilities.
    """
    def test_commentable(self):
        """It should have the comments attribute.
        """
        self.assertTrue(hasattr(self.factory(), 'comments'))
