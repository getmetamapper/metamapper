# -*- coding: utf-8 -*-
import base64
import urllib.parse as parse

from django.utils.translation import ugettext_lazy as _

from app.sso.exceptions import RedirectStateInvalid
from app.sso.providers.provider import SSOProvider


SETUP_FLOW_STATE_PARAMS = [
    'uid',
    'wksp',
]

LOGIN_FLOW_STATE_PARAMS = [
    'connection',
]


def _try_int_to_bool(value):
    try:
        return bool(int(value))
    except TypeError:
        return False


def prepare_auth_request(request):
    """Helper function to prepare authentication request.
    """
    oauth2_request = {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.META['HTTP_HOST'],
        'script_name': request.META['PATH_INFO'],
        'server_port': request.META['SERVER_PORT'],
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy()
    }
    return oauth2_request


def decode_raw_state(raw_state):
    """Decode the base64 state parameter.
    """
    decoded_state = base64.b64decode(raw_state)
    decoded_state = decoded_state.decode('utf-8')

    state = {
        k: v[0]
        for k, v in parse.parse_qs(decoded_state).items()
    }

    return state


def is_login_flow(raw_state):
    """Check if this is a login flow.
    """
    state = decode_raw_state(raw_state)
    return _try_int_to_bool(state.get("login", 1))


def build_oauth_config(raw_state):
    """Helper function to decode base64 encoded state parameter.
    """
    state = decode_raw_state(raw_state)
    is_login_flow = _try_int_to_bool(state.get("login", 1))

    expected_params = LOGIN_FLOW_STATE_PARAMS if is_login_flow else SETUP_FLOW_STATE_PARAMS

    for param_key in expected_params:
        item = state.get(param_key)
        if not item:
            raise RedirectStateInvalid(
                _(
                    "State is missing required attribute: %(attr)s"
                )
                % {"attr": param_key}
            )
    return state


class OAuth2Provider(SSOProvider):
    """docstring for OAuth2Provider
    """
