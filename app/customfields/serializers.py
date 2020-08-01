# -*- coding: utf-8 -*-
import rest_framework.serializers as serializers

import app.customfields.models as models
import app.audit.decorators as audit

import utils.fields as fields

from django.contrib.contenttypes.models import ContentType

from utils.mixins.serializers import MetamapperSerializer


def get_audit_kwargs(instance):
    """Make the parameters for logging audit activity.
    """
    content_type = ContentType.objects.get_for_model(instance)

    return {
        'target_object_id': instance.pk,
        'target_content_type_id': content_type.pk,
        'extras': {
            'datastore_id': instance.datastore_id,
        }
    }


class EnumFieldTypeValidator(serializers.Serializer):
    """Extra validation parameters for ENUM fieldtype.
    """
    choices = serializers.ListField(child=serializers.CharField(), allow_empty=False)


class CustomFieldSerializer(MetamapperSerializer, serializers.ModelSerializer):
    """Manage a custom field instance.
    """
    field_name = serializers.CharField(required=True, max_length=30)
    field_type = serializers.ChoiceField(required=True, choices=models.CustomField.FIELD_TYPE_CHOICES)
    validators = serializers.JSONField(required=False)
    short_desc = serializers.CharField(
        required=False,
        max_length=50,
        trim_whitespace=True,
        allow_null=True,
        allow_blank=True,
    )

    content_type = fields.RelatedObjectField(allowed_models=(ContentType,), allow_null=False)

    class Meta:
        model = models.CustomField
        fields = (
            'field_name',
            'field_type',
            'short_desc',
            'validators',
            'content_type',)

    def validate_user(self, data):
        """Validators for USER type.
        """
        return {}

    def validate_text(self, data):
        """Validators for TEXT type.
        """
        return {}

    def validate_enum(self, data):
        """Validators for ENUM type.
        """
        validator = EnumFieldTypeValidator(data=data)
        validator.is_valid(raise_exception=True)
        return validator.data

    def validate_group(self, data):
        """Validators for GROUP type.
        """
        return {}

    def validate(self, data):
        """Handle custom validation based on the field_type value.
        """
        field_type = self.instance.field_type if self.instance else data['field_type']
        validators = {
            models.CustomField.USER: self.validate_user,
            models.CustomField.TEXT: self.validate_text,
            models.CustomField.ENUM: self.validate_enum,
            models.CustomField.GROUP: self.validate_group,
        }
        data['validators'] = validators[field_type](data.get('validators', {}))
        return data

    def create(self, validated_data):
        """Create a brand new Datastore instance.
        """
        return models.CustomField.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update the provided CustomField instance.
        """
        instance.field_name = validated_data.get('field_name', instance.field_name)
        instance.validators = validated_data.get('validators', instance.validators)
        instance.short_desc = validated_data.get('short_desc', instance.short_desc)
        instance.save()
        return instance


class CustomPropertiesSerializer(MetamapperSerializer, serializers.Serializer):
    """Used to update multiple properties on a model instance.
    """
    properties = serializers.JSONField(required=True)

    class Meta:
        model = models.CustomField

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
        if value and value not in customfield.validators.get('choices', []):
            return 'The provided value is invalid.'
        return None

    def validate_group(self, value, customfield):
        """Validators for GROUP type.
        """
        if value and not self.instance.get_related_group(value):
            return 'The provided group does not exist.'
        return None

    def validate_properties(self, properties):
        """Perform property-level validation.
        """
        validators = {
            models.CustomField.USER: self.validate_user,
            models.CustomField.TEXT: self.validate_text,
            models.CustomField.ENUM: self.validate_enum,
            models.CustomField.GROUP: self.validate_group,
        }

        custom_fields = {
            field.pk: field
            for field in self.instance.get_custom_fields()
        }

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
            raise serializers.ValidationError('One of the properties is invalid.')
        return properties

    @audit.capture_activity(
        verb='updated custom properties on',
        hydrater=get_audit_kwargs,
        capture_changes=True,
    )
    def perform_update(self, instance, validated_data):
        """We wrap the update in this function so we can use the `audit` decorator.
        """
        instance.custom_properties = validated_data.get('properties', instance.custom_properties)
        return instance

    def update(self, instance, validated_data):
        """Update the provided CustomField instance.
        """
        return self.perform_update(instance, validated_data).get_custom_properties()
