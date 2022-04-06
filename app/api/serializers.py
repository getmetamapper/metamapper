# -*- coding: utf-8 -*-
import rest_framework.serializers as serializers

import app.api.models as models

from django.utils.crypto import get_random_string

from utils.mixins.serializers import MetamapperSerializer


class ApiTokenSerializer(MetamapperSerializer, serializers.ModelSerializer):
    name = serializers.CharField(required=True, max_length=60)
    is_enabled = serializers.BooleanField(required=False, default=True, allow_null=False)

    class Meta:
        model = models.ApiToken
        fields = (
            'name',
            'is_enabled',
        )

    def validate_name(self, name):
        token = models.ApiToken.objects.filter(
            name__iexact=name,
            workspace=self.context['request'].workspace,
        ).first()
        if token:
            raise serializers.ValidationError('Token with this name already exists.', 'exists')
        return name

    def validate_is_enabled(self, is_enabled):
        """We should cast NULL values as false.
        """
        return bool(is_enabled)

    def create(self, validated_data):
        """Create a brand new ApiToken instance.
        """
        validated_data['token'] = get_random_string(32).lower()
        return models.ApiToken.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.is_enabled = validated_data.get('is_enabled', instance.is_enabled)
        instance.save()
        return instance
