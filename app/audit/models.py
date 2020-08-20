# -*- coding: utf-8 -*-
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.timesince import timesince as djtimesince
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from app.audit import managers
from app.authentication.models import Workspace, User


class Activity(models.Model):
    """
    Activity model describing the actor acting out a verb (on an optional target).

    Nomenclature and model borrowed from https://django-activity-stream.readthedocs.io/en/latest/

    Generalized Format::
        <actor> <verb> <time>
        <actor> <verb> <target> <time>
        <actor> <verb> <action_object> <target> <time>

    Examples::
        <justquick> <reached level 60> <1 minute ago>
        <brosner> <commented on> <pinax/pinax> <2 hours ago>
        <washingtontimes> <started follow> <justquick> <8 minutes ago>
        <mitsuhiko> <closed> <issue 70> on <mitsuhiko/flask> <about 2 hours ago>

    Unicode Representation::
        justquick reached level 60 1 minute ago
        mitsuhiko closed issue 70 on mitsuhiko/flask 3 hours ago

    """
    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='activities',
    )

    actor = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='activities',
    )

    target_content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name='target',
        on_delete=models.CASCADE,
        db_index=True,
    )
    target_object_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        help_text="The object that the action (in)directly affects",
    )
    target = GenericForeignKey(
        'target_content_type',
        'target_object_id',
    )

    action_object_content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name='action_object',
        on_delete=models.CASCADE,
        db_index=True,
    )
    action_object_object_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        help_text="The object that the action was made on",
    )
    action_object = GenericForeignKey(
        'action_object_content_type',
        'action_object_object_id',
    )

    verb = models.CharField(max_length=255, db_index=True)

    extras = JSONField(
        default=dict,
        help_text="Additional metadata related to the change",
    )

    old_values = JSONField(default=dict)
    new_values = JSONField(default=dict)

    timestamp = models.DateTimeField(default=now, db_index=True)

    objects = managers.ActionManager()

    class Meta:
        ordering = ('-timestamp',)

    def __str__(self):
        ctx = {
            'actor': self.actor,
            'verb': self.verb,
            'action_object': self.action_object,
            'target': self.target,
            'timesince': self.timesince()
        }
        if self.target:
            if self.action_object:
                return _('%(actor)s %(verb)s %(action_object)s on %(target)s %(timesince)s ago') % ctx
            return _('%(actor)s %(verb)s %(target)s %(timesince)s ago') % ctx
        if self.action_object:
            return _('%(actor)s %(verb)s %(action_object)s %(timesince)s ago') % ctx
        return _('%(actor)s %(verb)s %(timesince)s ago') % ctx

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        return (
            djtimesince(self.timestamp, now).encode('utf8')
                                            .replace(b'\xc2\xa0', b' ')
                                            .decode('utf8')
        )

    def update_attributes(self, **validated_data):
        """Update the model from a dictionary.
        """
        for attr, value in validated_data.items():
            setattr(self, attr, value)
        self.save()
