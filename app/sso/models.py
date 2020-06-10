# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.postgres import fields as pgfields
from django.db import models
from django.db.models import ProtectedError
from django.utils import timezone
from django.utils.crypto import get_random_string

from app.authorization import constants

from utils.encrypt.fields import EncryptedTextField
from utils.regexp import domain_verification_regex
from utils.mixins.models import (
    StringPrimaryKeyModel, TimestampedModel, DirtyModel
)


class SSOConnection(StringPrimaryKeyModel, DirtyModel, TimestampedModel):
    """Service provider configuration for single sign on.
    """
    GITHUB = 'GITHUB'
    GOOGLE = 'GOOGLE'
    GENERIC = 'GENERIC'

    PROVIDER_CHOICES = (
        (GITHUB, 'Github'),
        (GOOGLE, 'Google for Work'),
        (GENERIC, 'SAML2'),
    )

    SAML2_PROVIDERS = [
        GENERIC,
    ]

    OAUTH2_PROVIDERS = [
        GITHUB,
        GOOGLE,
    ]

    workspace = models.ForeignKey(
        to='authentication.Workspace',
        related_name='sso_connections',
        on_delete=models.CASCADE
    )

    is_enabled = models.BooleanField(default=False)
    entity_id = models.CharField(max_length=128)
    sso_url = models.CharField(max_length=512, null=True)
    x509cert = EncryptedTextField(null=True)
    extras = pgfields.JSONField(default=dict)

    provider = models.CharField(
        max_length=30,
        choices=PROVIDER_CHOICES,
        default=GENERIC,
    )

    default_permissions = models.CharField(
        max_length=10,
        choices=constants.PERMISSION_GROUP_CHOICES,
        default=constants.READONLY,
    )

    class Meta:
        db_table = 'sso_connections'

    @classmethod
    def get_protocol(cls, provider):
        if provider.upper() in cls.SAML2_PROVIDERS:
            return 'saml2'
        if provider.upper() in cls.OAUTH2_PROVIDERS:
            return 'oauth2'

    @classmethod
    def provider_is_enabled(cls, provider):
        """If certain environment variables are not set, the provider is inactive.
        """
        if provider == SSOConnection.GOOGLE and settings.GOOGLE_ENABLED:
            return True
        if provider == SSOConnection.GITHUB and settings.GITHUB_ENABLED:
            return True
        if provider == SSOConnection.GENERIC:
            return True
        return False

    def get_provider(self):
        """Return the provider class for that connection.
        """
        from app.sso.providers.saml2.provider import SAML2Provider
        from app.sso.providers.oauth2.github.provider import GithubOAuth2Provider
        from app.sso.providers.oauth2.google.provider import GoogleOAuth2Provider

        mapping = {
            SSOConnection.GITHUB: GithubOAuth2Provider,
            SSOConnection.GOOGLE: GoogleOAuth2Provider,
            SSOConnection.GENERIC: SAML2Provider,
        }

        return mapping[self.provider](connection=self)

    @property
    def name(self):
        pk = self.id
        if self.provider == SSOConnection.GITHUB:
            pk = self.extras.get("login", self.id)
        if self.provider == SSOConnection.GOOGLE:
            pk = '-'.join(self.extras.get("domain", self.id).split('.'))
        return "{0}-{1}".format(self.provider.lower(), pk)

    @property
    def protocol(self):
        return self.get_protocol(self.provider.upper())

    @property
    def audience(self):
        return "urn:{0}:metamapper:{1}".format(self.protocol.lower(), self.name)

    @property
    def uses_saml2(self):
        return self.provider in SSOConnection.SAML2_PROVIDERS

    @property
    def uses_oauth2(self):
        return self.provider in SSOConnection.OAUTH2_PROVIDERS

    def delete(self):
        workspace = self.workspace
        if workspace.active_sso_id == self.id:
            raise ProtectedError('Cannot remove default connection.', [self])
        return super().delete()


class SSOIdentity(StringPrimaryKeyModel, TimestampedModel):
    """Identity between a user and an SSO provider.
    """
    user = models.ForeignKey(
        to='authentication.User',
        related_name='sso_identities',
        on_delete=models.CASCADE
    )

    provider = models.ForeignKey(
        to=SSOConnection,
        related_name='sso_identities',
        on_delete=models.CASCADE
    )

    ident = models.CharField(max_length=128)
    metadata = pgfields.JSONField(default=dict)

    last_verified_at = models.DateTimeField(auto_now_add=True)
    last_synced_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sso_identities'
        unique_together = ("provider", "ident",)


class SSODomain(StringPrimaryKeyModel, TimestampedModel):
    """Domain associated with a workspace for single sign-on.
    """
    TOKEN_LENGTH = 40
    MAX_ATTEMPTS = 16

    workspace = models.ForeignKey(
        to='authentication.Workspace',
        related_name='sso_domains',
        on_delete=models.CASCADE
    )

    domain = models.CharField(max_length=255, db_index=True, unique=True, null=False)

    attempts = models.PositiveIntegerField(default=0)
    last_attempted_at = models.DateTimeField(null=True, default=None)

    verified_at = models.DateTimeField(null=True, default=None)
    verification_token = models.CharField(max_length=100)

    class Meta:
        db_table = 'sso_domains'

    def __str__(self):
        return self.domain

    def save(self, *args, **kwargs):
        """Override and add the verification token.
        """
        if not self.verification_token:
            is_invalid = True

            while is_invalid:
                token = get_random_string(self.TOKEN_LENGTH)
                is_invalid = self.__class__.objects.filter(
                    verification_token=token
                ).exists()

            self.verification_token = token

        self.domain = self.domain.lower()

        return super().save(*args, **kwargs)

    @property
    def verified(self):
        return self.verified_at is not None

    @property
    def verification_failed(self):
        return self.attempts >= SSODomain.MAX_ATTEMPTS

    def verify_TXT_record(self, txt_record_str):
        """Regular expression verification against a DNS record.
        """
        match = domain_verification_regex.match(txt_record_str)
        if match:
            groups = match.groups()
            return (
                len(groups) == 2 and groups[1] == self.verification_token
            )
        return False

    def mark_as_verified(self):
        """Mark the domain as verified.
        """
        now = timezone.now()
        self.attempts = 0
        self.verified_at = now
        self.last_attempted_at = now
        self.save()

    def mark_as_failed(self):
        """Mark the domain as verified.
        """
        self.attempts = self.attempts + 1
        self.verified_at = None
        self.last_attempted_at = timezone.now()
        self.save()
