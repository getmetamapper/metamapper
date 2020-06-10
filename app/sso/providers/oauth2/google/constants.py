# -*- coding: utf-8 -*-
from django.conf import settings

CLIENT_ID = getattr(settings, "GOOGLE_CLIENT_ID", None)

CLIENT_SECRET = getattr(settings, "GOOGLE_CLIENT_SECRET", None)

SCOPE = "openid email profile"

BASE_DOMAIN = getattr(settings, "GOOGLE_BASE_DOMAIN", "google.com")

API_DOMAIN = getattr(settings, "GOOGLE_API_DOMAIN", "googleapis.com")

DOMAIN_BLOCKLIST = frozenset(getattr(settings, "GOOGLE_DOMAIN_BLOCKLIST", ["gmail.com"]) or [])

ACCESS_TOKEN_URL = "https://www.{0}/oauth2/v4/token".format(API_DOMAIN)

REFRESH_TOKEN_URL = "https://oauth2.{0}/token".format(API_DOMAIN)

AUTHORIZE_URL = "https://accounts.{0}/o/oauth2/auth".format(BASE_DOMAIN)

ERR_INVALID_DOMAIN = (
    "The domain for your Google account ({domain}) is not allowed to authenticate with this provider."
)

ERR_INVALID_RESPONSE = (
    "Unable to fetch user information from Google. Please contact support for assistance."
)
