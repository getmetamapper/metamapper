# -*- coding: utf-8 -*-
from django.core.cache import caches

from rest_framework import throttling


class ApiTokenThrottle(throttling.SimpleRateThrottle):
    cache = caches['api_throttle']
    scope = 'api_token'

    def get_cache_key(self, request, view):
        if request.api_token:
            ident = request.api_token.id
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

    def get_rate(self):
        return '1/min'
