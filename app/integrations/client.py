# -*- coding: utf-8 -*-
import abc
import requests

from requests.exceptions import ConnectionError, HTTPError, Timeout
from app.integrations.errors import ApiError, ApiHostError, ApiTimeoutError


class ApiClient(abc.ABC):
    """docstring for ApiClient
    """
    base_url = None

    allow_redirects = None

    def __init__(self, timeout=30, verify_ssl=True):
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    def __enter__(self):
        return self

    def __exit__(self):
        pass

    def build_url(self, path):
        if path.startswith("/"):
            if not self.base_url:
                raise ValueError(f"Invalid URL: {path}")
            return f"{self.base_url}{path}"
        return path

    def _request(self, method, path, headers=None, **kwargs):
        req_url = self.build_url(path)
        request = requests.Request(method, req_url, headers=headers, **kwargs)
        session = requests.Session()

        prepared_request = session.prepare_request(request)

        try:
            resp = session.send(
                prepared_request,
                verify=self.verify_ssl,
                timeout=self.timeout,
                allow_redirects=self.allow_redirects,
            )
            resp.raise_for_status()
        except ConnectionError as e:
            raise ApiHostError.from_exception(e)
        except Timeout as e:
            raise ApiTimeoutError.from_exception(e)
        except HTTPError as e:
            raise ApiError("API error occurred: %s" % str(e))

        if resp.status_code == 204:
            return {}

        return resp.json()

    @abc.abstractmethod
    def request(self, method, path, headers=None, **kwargs):
        pass

    def get(self, *args, **kwargs):
        return self.request("GET", *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.request("PATCH", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request("POST", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.request("PUT", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.request("DELETE", *args, **kwargs)

    def head(self, *args, **kwargs):
        return self.request("HEAD", *args, **kwargs)
