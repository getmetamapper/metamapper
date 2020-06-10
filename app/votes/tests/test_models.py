# -*- coding: utf-8 -*-
from app.comments.models import Comment

import app.votes.models as models

import testutils.cases as cases
import testutils.factories as factories


class VoteTests(cases.ModelTestCase):
    """Test cases for the Vote model class.
    """
    factory = factories.VoteFactory
    model_class = models.Vote

    def test_voteable_types(self):
        """Snapshot test for what models are voteable.
        """
        self.assertEqual(
            {Comment},
            set(self.model_class.voteable_types()),
        )

    def test_vote_count_field_when_up(self):
        """It should return `num_vote_up` as a result.
        """
        vote = self.factory(action=self.model_class.UP)

        self.assertEqual(
            vote.vote_count_field,
            'num_vote_up',
        )

    def test_vote_count_field_when_down(self):
        """It should return `num_vote_down` as a result.
        """
        vote = self.factory(action=self.model_class.DOWN)

        self.assertEqual(
            vote.vote_count_field,
            'num_vote_down',
        )

    def test_saves_with_workspace_id(self):
        """It should automatically add the workspace of the ContentObject.
        """
        user = factories.UserFactory()
        voteable = factories.CommentFactory()

        properties = {
            'content_object': voteable,
            'action': self.model_class.UP,
            'user': user,
        }

        vote = self.model_class.objects.create(**properties)

        self.assertEqual(
            vote.workspace_id,
            voteable.workspace_id,
        )

    def test_unique_together(self):
        """It should enforce a UNIQUE constraint.
        """
        self.validate_uniqueness_of(('user', 'content_object'))


class VoteableTestsMixin(object):
    """Test cases for a class that has voting abilities.
    """
    def test_vote(self):
        """It should cast a vote successfully.
        """
        voter = factories.UserFactory()
        resource = self.factory()
        vote = resource.vote(voter, models.Vote.UP)
        self.assertEqual(type(vote), models.Vote)

    def test_vote_when_exists(self):
        """It should update the vote (and counters) accordingly.
        """
        voter = factories.UserFactory()
        resource = self.factory()

        resource.vote(voter, models.Vote.UP)
        self.assertEqual(resource.num_vote_up, 1)
        self.assertEqual(resource.num_vote_down, 0)

        resource.vote(voter, models.Vote.DOWN)
        self.assertEqual(resource.num_vote_up, 0)
        self.assertEqual(resource.num_vote_down, 1)

        self.assertEqual(resource.votes.count(), 1)

    def test_get_vote_when_exists(self):
        """It should return the vote if exists.
        """
        voter = factories.UserFactory()
        resource = self.factory()
        vote = resource.vote(voter, models.Vote.UP)

        self.assertEqual(
            vote,
            resource.get_vote(voter),
        )

    def test_get_vote_when_not_exists(self):
        """It should return the vote if exists.
        """
        voter = factories.UserFactory()
        resource = self.factory()

        self.assertEqual(
            None,
            resource.get_vote(voter),
        )

    def test_delete_vote(self):
        """It should delete the vote and update the counters.
        """
        voter = factories.UserFactory()
        resource = self.factory()

        resource.vote(voter, models.Vote.UP)
        resource.delete_vote(voter)

        self.assertEqual(resource.votes.count(), 0)
