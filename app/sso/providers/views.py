# -*- coding: utf-8 -*-
from base64 import b64encode
from logging import getLogger

from django.conf import settings
from django.http import HttpResponseRedirect

from app.sso.models import SSOConnection
from app.sso.exceptions import IdentityNotValid
from app.sso.providers.constants import ERR_SSO_GENERIC


logger = getLogger(__name__)


def get_connection(connection_id):
    """Retrieve the single sign-on connection from the database.
    """
    try:
        connection = SSOConnection.objects.get(id=connection_id)
    except SSOConnection.DoesNotExist:
        return None

    if not connection.is_enabled:
        return None

    return connection


class SSOViewMixin(object):
    """Mixin to add SSO functionality to view.
    """
    @property
    def log(self):
        return logger

    def build_state_from_request(self, request, client):
        """Create state for the request. Override in each subclass.
        """
        raise NotImplementedError

    def get_sso_connection(self, connection_id):
        """Retrieve the SSO Connection from the Request object.
        """
        return get_connection(connection_id)

    def get_provider(self, *args, **kwargs):
        """Helper function for grabbing the provider class.
        """
        return NotImplementedError

    def error(self, message):
        """Redirect to the Login screen on error.
        """
        if isinstance(message, Exception):
            message = str(message)

        encoded_message = b64encode(message.encode()).decode('utf-8')

        # Attach the encoded message as a URL parameter.
        redirect_to = '{origin}/login/?error={error}'.format(
            origin=settings.WEBSERVER_ORIGIN,
            error=encoded_message,
        )

        return HttpResponseRedirect(redirect_to)

    def success(self, provider, user):
        """Redirect to single-use token sign in page on success.
        """
        redirect_to = '{origin}/{wksp}/sso/{uid}/{token}'.format(
            origin=settings.WEBSERVER_ORIGIN,
            wksp=provider.workspace.slug,
            uid=user.id,
            token=user.sso_access_token,
        )

        return HttpResponseRedirect(redirect_to)

    def login_pipeline(self, request, client, *args, **kwargs):
        """Dispatch the SSO authentication request.
        """
        connection, state, error = self.build_state_from_request(request, client)

        # If there is an error, we should redirect and display the flash message.
        if error:
            return self.error(error)

        provider = self.get_provider(connection=connection, client=client)

        try:
            user = provider.authenticate(state)
        except IdentityNotValid as e:
            return self.error(e)

        if not user:
            return self.error(ERR_SSO_GENERIC)

        # Reset the SSO token so that the user can use it to log in.
        user.set_sso_access_token()
        user.save()

        return self.success(provider, user)
