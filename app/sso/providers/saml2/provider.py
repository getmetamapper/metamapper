# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework.reverse import reverse

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.constants import OneLogin_Saml2_Constants

from app.sso.exceptions import IdentityNotValid
from app.sso.providers.provider import SSOProvider


def build_saml_config(connection, request):
    """Helper function to prepare SAML configuration.
    """
    avd = {}

    security_config = {
        "authnRequestsSigned": avd.get("authn_request_signed", False),
        "logoutRequestSigned": avd.get("logout_request_signed", False),
        "logoutResponseSigned": avd.get("logout_response_signed", False),
        "signMetadata": avd.get("metadata_signed", False),
        "wantMessagesSigned": avd.get("want_message_signed", False),
        "wantAssertionsSigned": avd.get("want_assertion_signed", False),
        "wantAssertionsEncrypted": avd.get("want_assertion_encrypted", False),
        "signatureAlgorithm": avd.get("signature_algorithm", OneLogin_Saml2_Constants.RSA_SHA256),
        "digestAlgorithm": avd.get("digest_algorithm", OneLogin_Saml2_Constants.SHA256),
        "wantNameId": False,
        "requestedAuthnContext": [
            "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport",
            "urn:federation:authentication:windows",
        ],
    }

    acs_url = "%s?connection=%s" % (reverse("sso-saml-acs", request=request), connection.id)

    saml_config = {
        "strict": True,
        "sp": {
            "entityId": connection.audience,
            "assertionConsumerService": {
                "url": acs_url,
                "binding": OneLogin_Saml2_Constants.BINDING_HTTP_POST,
            },
            "singleLogoutService": {
                "url": None,
                "binding": OneLogin_Saml2_Constants.BINDING_HTTP_REDIRECT,
            },
        },
        "security": security_config,
    }

    idp = {
        "entity_id": connection.entity_id,
        "x509cert": connection.x509cert,
        "sso_url": connection.sso_url,
    }

    if idp is not None:
        saml_config["idp"] = {
            "entityId": idp["entity_id"],
            "x509cert": idp["x509cert"],
            "singleSignOnService": {"url": idp["sso_url"]},
            "singleLogoutService": {"url": None},
        }

    if avd.get("x509cert") is not None:
        saml_config["sp"]["x509cert"] = avd["x509cert"]

    if avd.get("private_key") is not None:
        saml_config["sp"]["privateKey"] = avd["private_key"]

    return saml_config


def prepare_auth_request(request, saml_config):
    """Helper function to prepare authenitcation request.
    """
    if settings.DEBUG:
        server_port = '5050'
    else:
        server_port = '443'

    saml_request = {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.META['HTTP_HOST'],
        'script_name': request.META['PATH_INFO'],
        'server_port': server_port,
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy()
    }
    return OneLogin_Saml2_Auth(saml_request, saml_config)


class Attributes(object):
    """Mapping attributes for generic SAML2 provider.
    """
    IDENTIFIER = "user_id"
    USER_EMAIL = "user_email"
    FIRST_NAME = "fname"
    LAST_NAME = "lname"

    @classmethod
    def values(self):
        return [
            self.IDENTIFIER,
            self.USER_EMAIL,
            self.FIRST_NAME,
            self.LAST_NAME,
        ]


class SAML2Provider(SSOProvider):
    """docstring for SAML2Provider
    """
    def build_identity(self, raw_attributes):
        """Return a mapping containing the identity information.
        """
        attrs = {}
        mappings = self.attribute_mapping()

        # Map configured provider attributes
        for key, provider_key in mappings.items():
            attrs[key] = raw_attributes.get(provider_key, [""])[0]

        # All attributes MUST be correctly mapped
        invalid_attrs = []
        for attr in Attributes.values():
            if attr not in attrs or not attrs[attr]:
                invalid_attrs.append(attr)

        if len(invalid_attrs):
            raise IdentityNotValid(
                _(
                    "Failed to map SAML attribute: %(attr)s"
                )
                % {"attr": invalid_attrs[0]}
            )

        return {
            "ident": attrs[Attributes.IDENTIFIER],
            "email": attrs[Attributes.USER_EMAIL],
            "fname": attrs[Attributes.FIRST_NAME],
            "lname": attrs[Attributes.LAST_NAME],
            "email_verified": True,
        }

    def attribute_mapping(self):
        """Returns the default Attribute Key -> IdP attribute key mapping.
        """
        return self.connection.extras.get("mappings", {})

    def get_redirect_url(self, request):
        """Build the redirection URL based on the connection and web request.
        """
        saml = build_saml_config(self.connection, request)
        auth = prepare_auth_request(request, saml)
        return auth.login()
