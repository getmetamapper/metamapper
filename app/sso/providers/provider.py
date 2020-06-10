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


class SSOProvider(object):
    """docstring for SSOProvider
    """
    def __init__(self, connection, client=None):
        self.connection = connection
        self.workspace = self.connection.workspace
        self.client = client

    def authenticate(self, state):
        """Just-in-time provisioning for the requested user.
        """
        identity = self.build_identity(state)

        # If a user exists with the provided SSO Identity, we'll authenticate them.
        user = User.objects.filter(
            sso_identities__ident=identity["ident"],
            sso_identities__provider=self.connection,
        ).first()

        # Otherwise, we find the user by email and create the identity for future use.
        if not user:
            try:
                user = User.objects.get(email__iexact=identity["email"])

                if not identity["email_verified"]:
                    raise IdentityNotValid("Could not link the provided account: %s" % identity["email"])
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
