# -*- coding: utf-8 -*-
import rest_framework.serializers as drf

import app.comments.serializers as serializers

import testutils.cases as cases
import testutils.factories as factories

import app.votes.models as votemodels


class CommentSerializerCreateTests(cases.SerializerTestCase):
    """Test cases for the creating instances via CommentSerializer class.
    """
    factory = factories.CommentFactory

    serializer_class = serializers.CommentSerializer

    serializer_resource_name = 'Comment'

    @classmethod
    def setUpTestData(cls):
        cls.commentable = factories.TableFactory()
        cls.workspace = cls.commentable.workspace
        cls.user = factories.UserFactory()

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'html': '<p>Hello, this is my first comment.</p>',
            'content_object': self.commentable,
            'parent': None,
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should be able to create the resource.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(author=self.user))

    def test_validate_html(self):
        og_html = '<p>This is a <script>test</script>.</p>'
        attributes = self._get_attributes(html=og_html)
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(author=self.user))

        self.assertEqual(
            serializer.instance.html,
            '<p>This is a &lt;script&gt;test&lt;/script&gt;.</p>',
        )


class CommentSerializerUpdateTests(cases.SerializerTestCase):
    """Test cases for the updating instances via CommentSerializer class.
    """
    factory = factories.CommentFactory

    serializer_class = serializers.CommentSerializer

    serializer_resource_name = 'Comment'

    def test_when_valid(self):
        """It should be able to update the resource.
        """
        og_html = '<p>This is a test.</p>'
        comment = self.factory(html=og_html)

        serializer = self.serializer_class(
            instance=comment,
            data={
                'html': '<p>This is a <b>test</b>.</p>',
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())


class PinCommentSerializerTests(cases.SerializerTestCase):
    """Test cases for the pinning comments.
    """
    factory = None

    serializer_class = serializers.TogglePinCommentSerializer

    serializer_resource_name = 'Comment'

    @classmethod
    def setUpTestData(cls):
        cls.commentable = factories.TableFactory()
        cls.workspace = cls.commentable.workspace
        cls.user = factories.UserFactory()
        cls.comment = cls.commentable.comments.create(
            author=cls.user,
            html='This is a test',
        )

    def test_pin_when_valid(self):
        """It should be able to create the resource.
        """
        serializer = self.serializer_class(
            instance=self.comment,
            data={},
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(pinned_by=self.user))

        self.comment.refresh_from_db()
        self.assertTrue(self.comment.pinned)

    def test_pin_when_not_user(self):
        """You can only pin
        """
        serializer = self.serializer_class(
            instance=self.comment,
            data={},
            partial=True,
        )

        self.assertTrue(serializer.is_valid())

        with self.assertRaises(drf.ValidationError):
            serializer.save(pinned_by=None)

    def test_unpin(self):
        """It should be able to create the resource.
        """
        self.comment.pin(self.user)

        serializer = self.serializer_class(
            instance=self.comment,
            data={},
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(pinned_by=self.user))

        self.comment.refresh_from_db()
        self.assertFalse(self.comment.pinned)


class VoteForCommentSerializerTests(cases.SerializerTestCase):
    """Test cases for the pinning instances via CommentSerializer class.
    """
    factory = None

    serializer_class = serializers.VoteForCommentSerializer

    serializer_resource_name = 'Comment'

    @classmethod
    def setUpTestData(cls):
        cls.commentable = factories.TableFactory()
        cls.workspace = cls.commentable.workspace
        cls.user = factories.UserFactory()
        cls.comment = cls.commentable.comments.create(
            author=cls.user,
            html='This is a test',
        )

    def test_when_valid(self):
        """It should be able to create the resource.
        """
        serializer = self.serializer_class(
            instance=self.comment,
            data={'action': votemodels.Vote.UP},
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(user=self.user))

    def test_when_invalid_action(self):
        """It should be able to create the resource.
        """
        serializer = self.serializer_class(
            instance=self.comment,
            data={'action': 2},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'Comment',
                'field': 'action',
                'code': 'invalid_choice',
            }
        ])
