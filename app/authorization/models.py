# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import Group

from app.authorization import constants

from utils.mixins.models import TimestampedModel, AuditableModel
from utils.shortcuts import get_gratavar_url


Group.add_to_class('description', models.CharField(max_length=180, null=True, blank=True))
Group.add_to_class('created_at', models.DateTimeField(auto_now_add=True))
Group.add_to_class('updated_at', models.DateTimeField(auto_now=True))
Group.add_to_class(
    'workspace',
    models.ForeignKey(
        on_delete=models.CASCADE,
        related_name='groups',
        to='authentication.Workspace',
    )
)

setattr(Group, 'avatar_url', property(lambda s: None))


class Membership(TimestampedModel, AuditableModel):
    """Represents User membership to a Workspace.
    """
    OWNER = constants.OWNER
    MEMBER = constants.MEMBER
    READONLY = constants.READONLY

    PERMISSION_GROUP_CHOICES = constants.PERMISSION_GROUP_CHOICES

    PERMISSION_GROUPS = [
        p for p, v in constants.PERMISSION_GROUP_CHOICES
    ]

    workspace = models.ForeignKey(
        to='authentication.Workspace',
        related_name='memberships',
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        to='authentication.User',
        db_column='email',
        to_field='email',
        related_name='memberships',
        db_constraint=False,
        on_delete=models.CASCADE,
    )

    permissions = models.CharField(
        max_length=10,
        choices=constants.PERMISSION_GROUP_CHOICES,
        default=constants.MEMBER,
        help_text="Global access permissions for the workspace.",
    )

    class Meta:
        db_table = 'auth_memberships'
        unique_together = ('workspace', 'user')

    def __str__(self):
        return self.user_id

    @property
    def is_owner(self):
        return self.permissions == Membership.OWNER

    @property
    def avatar_url(self):
        return get_gratavar_url(self.user_id)
