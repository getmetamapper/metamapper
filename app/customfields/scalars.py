# -*- coding: utf-8 -*-
from graphene.types import Scalar
from app.authentication.models import User


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
            'pk': user.pk,
            'name': user.name,
            'email': user.email,
            'type': 'User',
        }
