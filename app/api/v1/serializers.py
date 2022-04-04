# -*- coding: utf-8 -*-
from rest_framework import serializers

from app.authentication.models import User
from app.authorization.models import Group


class ApiSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        for field_name, field in fields.items():
            field.read_only = field_name not in self.Meta.writable_fields
        return fields

    def serialize_property(self, value):
        if isinstance(value, (User,)):
            value = self.serialize_user(value)
        elif isinstance(value, (Group,)):
            value = self.serialize_group(value)
        return value

    def serialize_user(self, user):
        return {
            'id': user.id,
            'name': user.name,
            'type': 'USER',
        }

    def serialize_group(self, group):
        return {
            'id': group.id,
            'name': group.name,
            'type': 'GROUP',
        }


class CustomPropertiesMixin(serializers.Serializer):
    properties = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def get_properties(self, obj):
        custom_properties = obj.get_custom_properties()
        custom_output = [
            {
                'id': i,
                'label': v['label'],
                'value': self.serialize_property(v['value']),
            }
            for i, v in custom_properties.items()
        ]
        return sorted(custom_output, key=lambda v: v['label'])


class AssetOwnersMixin(serializers.Serializer):
    owners = serializers.SerializerMethodField()

    def get_owners(self, obj):
        owners = [
            self.serialize_property(o.owner)
            for o in obj.owners.order_by('order').prefetch_related('owner')
        ]
        return sorted(owners, key=lambda v: v['name'])

    class Meta:
        abstract = True
