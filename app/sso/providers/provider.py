# -*- coding: utf-8 -*-
from django.utils.crypto import get_random_string

from app.authentication.models import User
from app.sso.exceptions import IdentityNotValid


class Attributes(object):
    IDENTIFIER = "identifier"
    USER_EMAIL = "user_email"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"

    @classmethod
    def values(self):
        return [
            self.IDENTIFIER,
            self.USER_EMAIL,
            self.FIRST_NAME,
            self.LAST_NAME,
        ]


def verified_domain_exists(workspace, domain):
    return workspace.sso_domains.filter(
        domain__iexact=domain,
        verified_at__isnull=False,
    ).exists()


class SSOProvider(object):
    """docstring for SSOProvider
    """
    def __init__(self, connection, client=None):
        self.connection = connection
        self.workspace = self.connection.workspace
        self.client = client

    def is_domain_verified(self, email):
        """Parses an email and checks if the domain is verified.
        """
        return verified_domain_exists(self.workspace, email.split("@")[-1])

    def authenticate(self, state):
        """Just-in-time provisioning for the requested user.
        """
        identity = self.build_identity(state)

        # If a user exists with the provided SSO Identity, we'll authenticate them.
        user = User.objects.filter(
            sso_identities__ident=identity["ident"],
            sso_identities__provider=self.connection,
        ).first()

        if not self.is_domain_verified(identity["email"]):
            raise IdentityNotValid("Domain is not authorized for the provided workspace.")

        # Otherwise, we find the user by email and create the identity for future use.
        if not user:
            # We check Github and Google for email verification.
            if not identity["email_verified"]:
                raise IdentityNotValid("Could not link the provided account: %s" % identity["email"])

            try:
                user = User.objects.get(email__iexact=identity["email"])
            except User.DoesNotExist:
                user = User.objects.create_user(
                    email=identity["email"].lower(),
                    fname=identity["fname"],
                    lname=identity["lname"],
                    password=get_random_string(40),
                )

            user.sso_identities.update_or_create(
                provider=self.connection,
                defaults={
                    "ident": identity["ident"],
                    "metadata": {},
                }
            )

        if not user.is_on_team(self.workspace.id):
            self.workspace.grant_membership(user, self.connection.default_permissions)

        return user

    def build_identity(self, raw_attributes):
        """Return a mapping containing the identity information:
        {
            "ident", "email", "fname", "lname",
        }
        """
        raise NotImplementedError

    def attribute_mapping(self):
        """Returns the default Attribute Key -> IdP attribute key mapping.
        """
        raise NotImplementedError

    def get_redirect_url(self, request=None):
        """Retrieve authorization link for the configured SSO provider.
        """
        raise NotImplementedError
