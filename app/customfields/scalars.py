# -*- coding: utf-8 -*-
from graphene.types import Scalar
from graphql_relay import to_global_id

from app.authentication.models import User
from app.authorization.models import Group


class CustomPropScalar(Scalar):
    """Serialize custom properties correctly.
    """
    @staticmethod
    def serialize(value):
        output = []
        for k, attrs in value.items():
            label = attrs['label']
            value = attrs['value']
            if isinstance(value, (User,)):
                value = CustomPropScalar.serialize_user(value)
            elif isinstance(value, (Group,)):
                value = CustomPropScalar.serialize_group(value)
            output.append({
                'fieldId': k,
                'fieldLabel': label,
                'fieldValue': value,
            })
        return output

    @staticmethod
    def serialize_user(user):
        """Builds the response for a User.
        """
        return {
            'id': to_global_id('UserType', user.pk),
            'pk': user.pk,
            'name': user.name,
            'email': user.email,
            'type': 'User',
        }

    @staticmethod
    def serialize_group(group):
        """Builds the response for a Group.
        """
        return {
            'id': to_global_id('GroupType', group.pk),
            'pk': group.pk,
            'name': group.name,
            'type': 'Group',
        }
