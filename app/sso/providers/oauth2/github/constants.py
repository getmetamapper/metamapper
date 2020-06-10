# -*- coding: utf-8 -*-
from django.conf import settings

CLIENT_ID = getattr(settings, "GITHUB_CLIENT_ID", None)

CLIENT_SECRET = getattr(settings, "GITHUB_CLIENT_SECRET", None)

SCOPE = "user:email,read:org,repo"

BASE_DOMAIN = getattr(settings, "GITHUB_BASE_DOMAIN", "github.com")

API_DOMAIN = getattr(settings, "GITHUB_API_DOMAIN", "api.github.com")

ACCESS_TOKEN_URL = "https://{0}/login/oauth/access_token".format(BASE_DOMAIN)

AUTHORIZE_URL = "https://{0}/login/oauth/authorize".format(BASE_DOMAIN)
