# -*- coding: utf-8 -*-
import json
from urllib.parse import urlparse

from rest_framework.request import Request


__all__ = [
    "ApiError",
    "ApiHostError",
    "ApiTimeoutError",
    "ApiUnauthorizedError",
    "ApiRateLimitedError",
]


class ApiError(Exception):
    """Base error for API integrations.
    """
    def __init__(self, text, code=None, url=None):
        if code is not None:
            self.code = code
        self.text = text
        self.url = url
        if text:
            try:
                self.json = json.loads(text)
            except (json.JSONDecodeError, ValueError):
                self.json = None
        else:
            self.json = None
        super().__init__(text[:1024])

    @classmethod
    def from_response(cls, response, url=None):
        from app.integrations.errors import ApiUnauthorizedError, ApiRateLimitedError
        if response.status_code == 401:
            return ApiUnauthorizedError(response.text)
        elif response.status_code == 429:
            return ApiRateLimitedError(response.text)
        return cls(response.text, response.status_code, url=url)


class ApiHostError(ApiError):
    code = 503

    @classmethod
    def from_exception(cls, exception):
        if getattr(exception, "request"):
            return cls.from_request(exception.request)
        return cls("Unable to reach host")

    @classmethod
    def from_request(cls, request):
        host = urlparse(request.url).netloc
        return cls(f"Unable to reach host: {host}")


class ApiTimeoutError(ApiError):
    code = 504

    @classmethod
    def from_exception(cls, exception):
        if getattr(exception, "request"):
            return cls.from_request(exception.request)
        return cls("Timed out reaching host")

    @classmethod
    def from_request(cls, request: Request):
        host = urlparse(request.url).netloc
        return cls(f"Timed out attempting to reach host: {host}")


class ApiUnauthorizedError(ApiError):
    code = 401


class ApiRateLimitedError(ApiError):
    code = 429
