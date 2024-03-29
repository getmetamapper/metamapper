# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.db import models

from app.authentication.models import Workspace

from utils.mixins.models import (
    StringPrimaryKeyModel, TimestampedModel, AuditableModel
)


class CustomField(StringPrimaryKeyModel, AuditableModel, TimestampedModel):
    """User-defined field scoped to a specific model type.
    """
    USER = 'USER'
    TEXT = 'TEXT'
    ENUM = 'ENUM'
    GROUP = 'GROUP'
    MULTI = 'MULTI'

    FIELD_TYPE_CHOICES = (
        (USER, 'User'),
        (TEXT, 'Text'),
        (ENUM, 'Enum'),
        (GROUP, 'Group'),
        (MULTI, 'Multiselect'),
    )

    SUPPORTED_MODELS = [
        'datastore',
        'table',
    ]

    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='custom_fields',
    )

    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        related_name='custom_fields',
    )

    field_name = models.CharField(max_length=30)
    field_type = models.CharField(max_length=30, choices=FIELD_TYPE_CHOICES)
    validators = models.JSONField(default=dict)
    short_desc = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'customfields'
        unique_together = ('workspace', 'content_type', 'field_name',)

    @classmethod
    def get_content_type_from_name(cls, model):
        model = model.lower()
        if model not in CustomField.SUPPORTED_MODELS:
            return None
        return ContentType.objects.get(model=model)

    @property
    def is_text_type(self):
        return self.field_type == self.TEXT

    @property
    def is_user_type(self):
        return self.field_type == self.USER

    @property
    def is_enum_type(self):
        return self.field_type == self.ENUM

    @property
    def is_group_type(self):
        return self.field_type == self.GROUP

    @property
    def choices(self):
        """list: Retrieve the list of available choices for an ENUM field.
        """
        if not self.is_enum_type:
            return None
        return self.validators.get('choices', [])


class CustomPropertiesModel(models.Model):
    """Mixin for adding custom properties field.
    """
    custom_properties = models.JSONField(default=dict)

    class Meta:
        abstract = True

    @classmethod
    def get_content_type(cls):
        return ContentType.objects.get_for_model(cls)

    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self)

    def get_custom_fields(self, **kwargs):
        """Retrieve the custom fields associated with this model.
        """
        return self.content_type.custom_fields.exclude(id__in=self.disabled_custom_fields).filter(
            workspace_id=self.workspace_id,
            **kwargs,
        )

    def get_related_user(self, user_id, queryset=None):
        """Retrieve the workspace team member.
        """
        try:
            user_id = int(user_id)
        except (AttributeError, TypeError):
            pass
        if not isinstance(user_id, int):
            return None
        if not queryset:
            return self.workspace.team_members.filter(id=user_id).first()
        return next(filter(lambda u: u.id == user_id, queryset), None)

    def get_related_group(self, group_id, queryset=None):
        """Retrieve the workspace group.
        """
        if not isinstance(group_id, int):
            return None
        if not queryset:
            return self.workspace.groups.filter(id=group_id).first()
        return next(filter(lambda g: g.id == group_id, queryset), None)

    def get_custom_properties(self, allow_null=True):
        """Retrieve all custom properties associated with a model.
        """
        custom_fields = self.get_custom_fields().order_by('created_at')
        custom_output = {}

        user_queryset = None
        group_queryset = None

        for f in custom_fields:
            value = self.custom_properties.get(f.pk)
            if f.is_user_type:
                if not user_queryset:
                    user_queryset = self.workspace.team_members.all()
                value = self.get_related_user(value, user_queryset)
            elif f.is_group_type:
                if not group_queryset:
                    group_queryset = self.workspace.groups.all()
                value = self.get_related_group(value, group_queryset)
            elif f.is_enum_type and value not in f.choices:
                value = None
            if not allow_null and value is None:
                continue
            custom_output[f.pk] = {
                'label': f.field_name,
                'value': value,
            }
        return custom_output
