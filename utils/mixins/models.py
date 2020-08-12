# -*- coding: utf-8 -*-
import uuid

from dirtyfields import DirtyFieldsMixin

from django.db import models
from django.utils.crypto import get_random_string


def uuid4_hex(*args, **kwargs):
    return uuid.uuid4().hex


class UUIDModel(models.Model):
    """Mixin to add UUID pk to models.
    """
    id = models.CharField(
        db_index=True,
        primary_key=True,
        editable=False,
        unique=True,
        max_length=32,
        default=uuid4_hex,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)


class StringPrimaryKeyModel(models.Model):
    """Mixin to add Alphanumeric pk to models.
    """
    id = models.CharField(
        db_index=True,
        primary_key=True,
        editable=False,
        unique=True,
        max_length=40,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if self._state.adding is True and not self.id:
            self.id = self.__class__.generate_primary_key()
        super().save(*args, **kwargs)

    @classmethod
    def initialize(cls, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = cls.generate_primary_key()
        return cls(**kwargs)

    @classmethod
    def generate_primary_key(cls, max_length=12, downcase=False):
        """Helper function to generate a primary key.
        """
        is_invalid = True
        while is_invalid:
            surrogate = get_random_string(max_length)
            if downcase:
                surrogate = surrogate.lower()
            is_invalid = cls.objects.filter(id=surrogate).exists()
        return surrogate


class TimestampedModel(models.Model):
    """Mixin to add created and updated timestamps to models.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at', '-updated_at']


class DirtyModel(DirtyFieldsMixin):
    """Extension to django-dirtyfields module.
    """
    def dirty_fields(self, *exclude):
        """Get list of dirty fields.
        """
        return [
            f for f in list(self.get_dirty_fields())
            if f not in exclude
        ]

    def is_dirty(self, *fields):
        """Boolean check if a provided field has changed.
        """
        if not fields:
            return super().is_dirty()
        dirtyfields = self.get_dirty_fields()
        return any(f in dirtyfields for f in fields)


class AuditableModel(DirtyModel):
    """Mixin for auditing activity of a model.
    """
    audited_fields = []

    def get_old_values(self, audited_only=True):
        """Get all of the previous values of changed fields.
        """
        dirtyfields = self.get_dirty_fields()
        if not audited_only:
            return dirtyfields
        output = {}
        for field in self.audited_fields:
            if field in dirtyfields:
                output[field] = dirtyfields[field]
        return output

    def old_value(self, field):
        """Get the previous value of a dirty field.
        """
        dirtyfields = self.get_dirty_fields()
        if field not in dirtyfields:
            return getattr(self, field)
        return dirtyfields[field]

    def get_new_values(self, fields):
        """Get all of the current values for a list of fields.
        """
        fields = fields or self.dirty_fields()
        return {
            f: getattr(self, f) for f in fields
        }

    def new_value(self, field):
        """Get the current value of a field.
        """
        return getattr(self, field)
