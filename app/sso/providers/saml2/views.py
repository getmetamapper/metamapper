# -*- coding: utf-8 -*-
from rest_framework.views import APIView

from app.sso.providers.constants import ERR_SSO_NOT_ENABLED
from app.sso.providers.views import SSOViewMixin
from app.sso.providers.saml2.provider import SAML2Provider
from app.sso.providers.saml2.provider import prepare_auth_request, build_saml_config


class SAML2AcceptACSView(SSOViewMixin, APIView):
    """Process SAML2.0 authentication request via callback function.
    """
    def dispatch(self, request, *args, **kwargs):
        """The SAML2.0 request should immediately attempt to login.
        """
        return self.login_pipeline(request, client=None)

    def get_provider(self, *args, **kwargs):
        """Helper function for grabbing the provider class.
        """
        return SAML2Provider(*args, **kwargs)

    def build_state_from_request(self, request, client=None):
        """Create state for the request.
        """
        state = {}
        error = None

        connection = self.get_sso_connection(request.GET.get('connection'))

        if not connection:
            return (connection, state, ERR_SSO_NOT_ENABLED)

        saml = build_saml_config(connection, request)
        auth = prepare_auth_request(request, saml)
        auth.process_response()

        if auth.get_errors():
            error = auth.get_last_error_reason()
        else:
            state = auth.get_attributes()

        return (connection, state, error)
