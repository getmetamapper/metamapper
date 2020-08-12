# -*- coding: utf-8 -*-
from django.apps import apps
from django.db import models, transaction
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from app.authentication.models import User, Workspace
from utils.mixins.models import TimestampedModel
from utils.shortcuts import get_user_id


class Vote(TimestampedModel):
    """Comment or annotation on any model in the application.
    """
    UP = 1
    DOWN = -1

    VOTE_COUNT_FIELDS = {
        UP: 'num_vote_up',
        DOWN: 'num_vote_down'
    }

    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='+',
    )

    object_id = models.CharField(max_length=30)

    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
    )

    content_object = GenericForeignKey('content_type', 'object_id')

    action = models.SmallIntegerField(default=UP)

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'votes'
        unique_together = ('user', 'content_type', 'object_id')
        index_together = ('content_type', 'object_id')

    @classmethod
    def voteable_types(cls):
        """List the models that are voteable.
        """
        return tuple(
            m for m in apps.get_models()
            if hasattr(m, 'votes')
        )

    @property
    def vote_count_field(self):
        """Retrieves string name of field that should be updated.
        """
        return Vote.VOTE_COUNT_FIELDS[self.action]

    def save(self, *args, **kwargs):
        """Override save method to add related workspace by default.
        """
        created = self._state.adding is True and not self.pk
        if created and not self.workspace_id:
            self.workspace_id = self.content_object.workspace_id
        return super().save(*args, **kwargs)


class Voteable(models.Model):
    """Mixin to add voting functionality to a model.
    """
    num_vote_up = models.PositiveIntegerField(default=0, db_index=True)
    num_vote_down = models.PositiveIntegerField(default=0, db_index=True)

    votes = GenericRelation(Vote)

    class Meta:
        abstract = True

    def vote(self, user, action):
        """Vote for the model instance.
        """
        with transaction.atomic():
            obj, created = self.votes.get_or_create(
                user_id=get_user_id(user),
                workspace=self.workspace,
                defaults={'action': action},
            )
            if created:
                self.set_vote_count(action, 1)
                self.save()
            else:
                old_action = obj.action
                if old_action != action:
                    obj.action = action
                    obj.save()
                    self.set_vote_count(action, 1)
                    self.set_vote_count(old_action, -1)
                    self.save()
        return obj

    def upvote(self, user):
        """Shortcut for giving a positive vote.
        """
        return self.vote(user, action=Vote.UP)

    def downvote(self, user):
        """Shortcut for giving a negative vote.
        """
        return self.vote(user, action=Vote.DOWN)

    def set_vote_count(self, action, increment_by):
        """Updates the total vote counters for the provided action.
        """
        attribute = Vote.VOTE_COUNT_FIELDS[int(action)]
        new_value = getattr(self, attribute) + increment_by

        setattr(self, attribute, new_value)

    def get_vote(self, user):
        """If the provided user has voted for the model instance, retrieve it.
        """
        return self.votes.filter(
            user_id=get_user_id(user)
        ).first()

    def delete_vote(self, user):
        """If the provided user has voted for the model instance, remove it.
        """
        vote = self.get_vote(user)
        if not vote:
            return (0, {})
        with transaction.atomic():
            num_deleted, deleted = vote.delete()
            if num_deleted:
                self.set_vote_count(vote.action, -1 * deleted['votes.Vote'])
                self.save()
        return (num_deleted, deleted)

    def exists(self, user, action=None):
        """Indicates if the user voted for the model instance already.
        """
        filter_kwargs = {
            'user_id': get_user_id(user),
        }

        if action:
            filter_kwargs['action'] = action

        return self.votes.filter(**filter_kwargs).exists()
