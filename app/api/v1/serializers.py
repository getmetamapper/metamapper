# -*- coding: utf-8 -*-
from rest_framework import serializers

import utils.fields as fields

from app.authentication.models import User
from app.authorization.models import Group
from app.customfields.models import CustomField
from app.definitions.models import AssetOwner, Table


class ApiSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        for field_name, field in fields.items():
            field.read_only = field_name not in self.Meta.writable_fields
        return fields

    @property
    def errors(self):
        output = []
        for field, errors in super().errors.items():
            if isinstance(errors, (dict,)) and len(errors) > 0:
                errors = errors[next(iter(errors))]
            output += [
                {
                    'reason': error.code,
                    'message': str(error) or 'Sorry, an error occurred.',
                    'location_type': 'field',
                    'location': field,
                }
                for error in errors
            ]
        return output

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
        custom_properties = obj.get_custom_properties(allow_null=False)
        custom_output = [
            {
                'id': i,
                'label': v['label'],
                'value': self.serialize_property(v['value']),
            }
            for i, v in custom_properties.items()
        ]
        return sorted(custom_output, key=lambda v: v['label'])


class CustomPropertySerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    value = serializers.CharField(required=True, allow_null=True)


class CustomPropertiesSerializer(serializers.Serializer):
    properties = CustomPropertySerializer(many=True)

    class Meta:
        model = CustomField

    @property
    def errors(self):
        output = []
        for errors in super().errors.values():
            if isinstance(errors, (list,)) and len(errors) > 0:
                errors = {'properties': next(iter(errors))}
            output += [
                {
                    'reason': error.code,
                    'message': str(error) or 'Sorry, an error occurred.',
                    'location_type': 'property',
                    'location': field,
                }
                for field, error in errors.items()
            ]
        return output

    def validate_user(self, value, customfield):
        """Validators for USER type.
        """
        if value and not self.instance.get_related_user(value):
            return 'The provided team member does not exist.'
        return None

    def validate_text(self, value, customfield):
        """Validators for TEXT type.
        """
        return None

    def validate_enum(self, value, customfield):
        """Validators for ENUM type.
        """
        choices = customfield.validators.get('choices', [])
        if value and value not in choices:
            return 'The provided value is invalid.'
        return None

    def validate_group(self, value, customfield):
        """Validators for GROUP type.
        """
        if value and not self.instance.get_related_group(value):
            return 'The provided group does not exist.'
        return None

    def validate_multi(self, value, customfield):
        """Validators for MULTI type.
        """
        choices = customfield.validators.get('choices', [])
        if value is not None and not isinstance(value, list):
            return 'The provided value must be a list.'
        if value is not None and not all(v in choices for v in value):
            return 'The provided value is invalid.'
        return None

    def validate_properties(self, properties):
        """Perform property-level validation.
        """
        validators = {
            CustomField.ENUM: self.validate_enum,
            CustomField.GROUP: self.validate_group,
            CustomField.TEXT: self.validate_text,
            CustomField.USER: self.validate_user,
            CustomField.MULTI: self.validate_multi,
        }

        custom_fields = {
            field.pk: field
            for field in self.instance.get_custom_fields()
        }

        properties = {
            p['id']: p['value']
            for p in properties if 'id' in p
        }

        for field_pk in custom_fields.keys():
            properties[field_pk] = properties.get(
                field_pk,
                self.instance.custom_properties.get(field_pk),
            )

        errors = {}
        for field_pk, value in properties.items():
            error = None
            if field_pk not in custom_fields:
                error = 'This custom property does not exist.'.format(**locals())
            else:
                field = custom_fields[field_pk]
                error = validators[field.field_type](value, field)
            if error:
                errors[field_pk] = error

        if len(errors):
            raise serializers.ValidationError(errors)

        return {k: v for k, v in properties.items() if v is not None}

    def update(self, instance, validated_data):
        """Update the provided instance.
        """
        instance.custom_properties = validated_data.get('properties', instance.custom_properties)
        instance.save()
        return instance


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


class AssetOwnerSerializer(serializers.Serializer):
    content_object = fields.RelatedObjectField(
        allowed_models=(Table,),
        allow_null=False,
    )

    owner = fields.RelatedObjectField(
        allowed_models=(User, Group,),
        allow_null=False,
    )

    class Meta:
        model = AssetOwner
        fields = ('content_object', 'owner',)

    def validate_owner(self, owner):
        """The owner must be part of the provided workspace.
        """
        workspace = self.context['request'].workspace
        has_error = False

        if isinstance(owner, (User,)) and not owner.is_on_team(workspace.id):
            has_error = True
        elif isinstance(owner, (Group,)) and not owner.workspace_id == workspace.id:
            has_error = True

        if has_error:
            raise serializers.ValidationError(
                'The provided owner is not part of this workspace.',
                'invalid',
            )
        return owner

    def create(self, validated_data):
        """Create a brand new AssetOwner instance.
        """
        return AssetOwner.objects.create(**validated_data)
