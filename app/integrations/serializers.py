# -*- coding: utf-8 -*-
import rest_framework.serializers as serializers

import app.integrations.models as models
import app.integrations.registry as registry

from utils.mixins.serializers import MetamapperSerializer


class IntegrationConfigSerializer(MetamapperSerializer, serializers.ModelSerializer):
    integration = serializers.ChoiceField(required=True, choices=[i.id for i in registry.AVAILABLE_INTEGRATIONS])
    meta = serializers.JSONField(required=True)

    class Meta:
        model = models.IntegrationConfig
        fields = ('integration', 'meta',)

    def validate(self, data):
        """Handle custom validation based on the `meta` value.
        """
        integration_id = self.instance.integration if self.instance else data['integration']
        integration = registry.find_integration(integration_id)
        validator = integration.handler.Meta.validator(
            data=data.get('meta', {}),
            context=self.context)
        validator.is_valid(raise_exception=True)

        meta = validator.data.copy()
        auth = []
        displayable = meta.get(integration.handler.Meta.displayable_key)

        for auth_key in integration.handler.Meta.auth_keys:
            auth_value = meta.pop(auth_key)
            if auth_value != "<redacted>":
                auth.append(auth_value)

        if len(auth):
            data['auth'] = integration.handler.auth_in(*auth)

        data['displayable'] = integration.handler.displayable_in(displayable)
        data['meta'] = meta

        return data

    def create(self, validated_data):
        """Create a brand new IntegrationConfig instance.
        """
        return models.IntegrationConfig.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.displayable = validated_data.get('displayable', instance.displayable)
        instance.auth = validated_data.get('auth', instance.auth)
        instance.meta = validated_data.get('meta', instance.meta)
        instance.save()
        return instance
