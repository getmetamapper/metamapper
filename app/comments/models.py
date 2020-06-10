# -*- coding: utf-8 -*-
import bleach

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from app.authentication.models import User, Workspace
from app.votes.models import Voteable

from utils.mixins.models import (
    StringPrimaryKeyModel, TimestampedModel, AuditableModel
)


class Comment(StringPrimaryKeyModel,
              AuditableModel,
              TimestampedModel,
              Voteable):
    """Comment or annotation on any model in the application.
    """
    SUPPORTED_MODELS = [
        'table',
        'column',
    ]

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

    html = models.TextField()
    text = models.TextField()

    parent = models.ForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='child_comments',
        null=True,
    )

    author = models.ForeignKey(to=User, on_delete=models.CASCADE)

    pinned_at = models.DateTimeField(default=None, null=True)
    pinned_by = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='+',
        default=None,
        null=True,
    )

    class Meta:
        db_table = 'comments'
        index_together = ('content_type', 'object_id')

    @classmethod
    def get_content_type_from_name(cls, model):
        model = model.lower()
        if model not in Comment.SUPPORTED_MODELS:
            raise ValueError('That resource does not support custom fields.')
        return ContentType.objects.get(model=model)

    @classmethod
    def get_content_type_from_node(cls, node_type):
        mapping = {
            'TableType': 'table',
            'ColumnType': 'column',
        }
        if node_type not in mapping:
            raise ValueError('That resource does not support custom fields.')
        return cls.get_content_type_from_name(mapping[node_type])

    @classmethod
    def commentable_types(cls):
        """List the models that are commentable.
        """
        return tuple(
            m for m in apps.get_models()
            if hasattr(m, 'comments')
        )

    @property
    def pinned(self):
        return self.pinned_at is not None

    @property
    def search_label(self):
        return 'Comment on %s' % self.content_object.search_label

    @property
    def search_pathname(self):
        params = ''
        if self.content_object.__class__.__name__ == 'Column':
            params = '?selectedColumn=%s' % self.object_id
        return self.content_object.search_pathname + params

    def as_search_result(self):
        return {
            'pathname': self.search_pathname,
            'label': self.search_label,
            'description': self.text,
            'datastore_id': self.content_object.datastore_id,
        }

    def pin(self, user):
        """Pin by a specific user.
        """
        if not self.pinned:
            self.pinned_at = timezone.now()
            self.pinned_by = user
            self.save()
        return self.pinned

    def unpin(self):
        """Remove pinned status.
        """
        self.pinned_at = None
        self.pinned_by = None
        self.save()
        return self.pinned

    def save(self, *args, **kwargs):
        """Override save method to add related workspace by default.
        """
        created = self._state.adding is True and not self.pk
        if created and not self.workspace_id:
            self.workspace_id = self.content_object.workspace_id

        self.text = bleach.clean(self.html, strip=True)

        return super().save(*args, **kwargs)
