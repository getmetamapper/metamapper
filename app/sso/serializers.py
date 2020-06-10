# -*- coding: utf-8 -*-
import app.sso.models as models

import utils.regexp as regexp
import rest_framework.serializers as serializers

from django.utils.translation import ugettext_lazy as _
from rest_framework.validators import UniqueValidator

from app.authorization.constants import PERMISSION_GROUP_CHOICES

from app.sso.providers.saml2.provider import Attributes
from app.sso.providers.oauth2.google.constants import DOMAIN_BLOCKLIST

from utils.mixins.serializers import MetamapperSerializer


class GithubOAuth2ExtrasValidator(serializers.Serializer):
    """Extra validation parameters for GITHUB provider.
    """
    ident = serializers.CharField(required=True, max_length=90)
    login = serializers.CharField(required=True, max_length=90)

    def is_github_org_member(self, org_id):
        """Separate function for easier patching in tests.
        """
        return self.context['request'].user.is_github_org_member(org_id)

    def validate_ident(self, ident):
        """Organization needs to be allowed to work.
        """
        if not self.is_github_org_member(ident):
            raise serializers.ValidationError('Github identity could not be not verified.')
        return ident


class GoogleOAuth2ExtrasValidator(serializers.Serializer):
    """Extra validation parameters for GOOGLE provider.
    """
    domain = serializers.CharField(required=True, max_length=90)

    def get_gsuite_domain(self):
        """Separate function for easier patching in tests.
        """
        return self.context['request'].user.get_gsuite_domain()

    def validate_domain(self, domain):
        """Domain needs to be allowed to work.
        """
        domain = domain.lower()
        google_domain = self.get_gsuite_domain()

        if not google_domain == domain:
            raise serializers.ValidationError('GSuite domain could not be not authorized.', 'authorized')

        if domain in DOMAIN_BLOCKLIST:
            raise serializers.ValidationError('GSuite domain could not be not authorized.', 'authorized')

        return domain


class GenericSaml2ExtrasValidator(serializers.Serializer):
    """Extra validation parameters for GENERIC provider.
    """
    mappings = serializers.JSONField(default=dict)

    def validate_mappings(self, mappings):
        """Make sure the mappings field has the correct keys.
        """
        for attr in Attributes.values():
            if attr not in mappings or not mappings[attr]:
                raise serializers.ValidationError(
                    _(
                        "Required mapping attribute is missing: %(attr)s"
                    )
                    % {"attr": attr},
                    "missing_%s" % attr
                )
        return mappings


class SSOConnectionSerializer(MetamapperSerializer, serializers.ModelSerializer):
    id = serializers.CharField(required=True)
    is_enabled = serializers.BooleanField(default=True)
    entity_id = serializers.CharField(required=True)
    provider = serializers.ChoiceField(
        choices=models.SSOConnection.PROVIDER_CHOICES,
        error_messages={'invalid_choice': 'Please provide a valid SSO provider.'},
    )
    default_permissions = serializers.ChoiceField(
        choices=PERMISSION_GROUP_CHOICES,
        error_messages={'invalid_choice': 'Please provide a valid permission group.'},
    )
    sso_url = serializers.URLField(required=False, allow_null=True)
    extras = serializers.JSONField(default=dict)
    x509cert = serializers.RegexField(
        regex=regexp.X509_CERT_PATTERN,
        required=False,
        allow_null=True,
        error_messages={'invalid': 'Please provide a valid x509 certificate.'},
    )

    class Meta:
        model = models.SSOConnection
        fields = (
            'id',
            'provider',
            'entity_id',
            'default_permissions',
            'sso_url',
            'extras',
            'x509cert',
            'is_enabled',
            'created_at',
            'updated_at')

    def validate_extras(self, extras):
        """Should return an empty dictionary if needed.
        """
        return extras or {}

    def validate_github_oauth2(self, data):
        """Validators for Github OAuth2 type.
        """
        validator = GithubOAuth2ExtrasValidator(data=data, context=self.context)
        validator.is_valid(raise_exception=True)
        return validator.data

    def validate_google_oauth2(self, data):
        """Validators for Google OAuth2 type.
        """
        validator = GoogleOAuth2ExtrasValidator(data=data, context=self.context)
        validator.is_valid(raise_exception=True)
        return validator.data

    def validate_generic_saml2(self, data):
        """Validators for SAML2 type.
        """
        validator = GenericSaml2ExtrasValidator(data=data)
        validator.is_valid(raise_exception=True)
        return validator.data

    def validate(self, data):
        """Validation rules for SSO connection model.
        """
        provider = data.get("provider", getattr(self.instance, "provider", None))
        protocol = models.SSOConnection.get_protocol(provider)

        x509cert = data.get("x509cert", getattr(self.instance, "x509cert", None))
        if protocol == "saml2" and not x509cert:
            raise serializers.ValidationError(
                {"x509cert": "SAML connection requires valid x509 certificate."}
            )

        sso_url = data.get("sso_url", getattr(self.instance, "sso_url", None))
        if protocol == "saml2" and not sso_url:
            raise serializers.ValidationError(
                {"sso_url": "SAML connection requires valid single sign-on URL."}
            )

        # Validate `extra` field for the specific provider.
        extras = data.get("extras", getattr(self.instance, "extras", {}))

        validators = {
            models.SSOConnection.GITHUB: self.validate_github_oauth2,
            models.SSOConnection.GOOGLE: self.validate_google_oauth2,
            models.SSOConnection.GENERIC: self.validate_generic_saml2,
        }
        data['extras'] = validators[provider](extras)
        return data

    def update(self, instance, validated_data):
        """You can only update attributes of a GENERIC Saml2 connection.
        """
        instance.is_enabled = validated_data.get('is_enabled', instance.is_enabled)
        instance.default_permissions = validated_data.get('default_permissions', instance.default_permissions)
        if instance.uses_saml2:
            instance.entity_id = validated_data.get('entity_id', instance.entity_id)
            instance.extras = validated_data.get('extras', instance.extras)
            instance.sso_url = validated_data.get('sso_url', instance.sso_url)
            instance.x509cert = validated_data.get('x509cert', instance.x509cert)
        instance.save()
        return instance


class SSODomainSerializer(MetamapperSerializer, serializers.ModelSerializer):
    domain = serializers.RegexField(
        regex=regexp.DOMAIN_PATTERN,
        required=True,
        error_messages={'invalid': 'Enter a valid domain name.'},
        validators=[
            UniqueValidator(queryset=models.SSODomain.objects.all(), message='Domain has already been claimed.'),
        ],
    )
    verified = serializers.SerializerMethodField()

    class Meta:
        model = models.SSODomain
        fields = (
            'domain',
            'verified',
            'created_at')

    def get_verified(self, instance):
        """Boolean indicator of domain verification.
        """
        return instance.verified_at is not None

    def update(self, instance, validated_data):
        raise NotImplementedError('SSODomainSerializer cannot update resources.')
