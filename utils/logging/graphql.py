# -*- coding: utf-8 -*-
import uuid
import json
import importlib
import os

from django.conf import settings
from rest_framework import status

import utils.encoders as encoders
import utils.logging as logging


module_name, class_name = os.path.splitext(settings.GRAPHQL_REQUEST_LOGGER)


def get_request_logger():
    """Get the current Graphql request logger.
    """
    return getattr(importlib.import_module(module_name), class_name[1:])()


class GraphqlRequestLogger(object):
    """Middleware for logging HTTP requests against the Graphql endpoint.
    """
    fields_to_redact = ['extras']

    delimiter = "\n"

    indent = 2

    def __init__(self):
        self.logger = logging.Logger("metamapper.graphql")

    def log(self, request, response, operation_name, duration, **args):
        """Log the HTTP request.
        """
        context = {}

        if hasattr(request, "user") and request.user and request.user.pk is not None:
            context["user"] = request.user.pk

        if hasattr(request, "workspace") and request.workspace:
            context["workspace"] = request.workspace.pk

        log_kwargs = {
            "requestId": str(uuid.uuid4()),
            "resolverName": operation_name,
            "resolverArgs": self.sanitize_variables(args),
            "context": context,
            "elapsedTime": "%s ms" % duration,
        }

        error = self.get_error_type(response)

        if error:
            log_kwargs["error"] = error

        self.logger.info(
            "%s%s" % (self.delimiter, json.dumps(log_kwargs, indent=self.indent, cls=encoders.UUIDEncoder))
        )

    def sanitize_variables(self, variables):
        """Prevents sensitive values from being exposed in the logs.
        """
        variables = variables or {}
        output = {}
        for k, v in variables.items():
            value = v
            if k in self.fields_to_redact or "password" in k.lower():
                value = "*****"
            output[k] = value
        return output

    def get_error_type(self, response):
        """Format the error type, if one exists...
        """
        errors = response.get("errors", [])
        if errors and len(errors) > 0:
            for error in errors:
                code = error.get("status")
                if code == status.HTTP_401_UNAUTHORIZED:
                    return "unauthorized"
                elif code == status.HTTP_403_FORBIDDEN:
                    return "permission_denied"
                elif code == status.HTTP_422_UNPROCESSABLE_ENTITY:
                    return "unprocessible_entity"
                elif code == status.HTTP_404_NOT_FOUND:
                    return "not_found"
            return "bad_request"
        else:
            for operation, body in response["data"].items():
                if not isinstance(body, (dict,)):
                    continue
                errors = body.get("errors", [])
                if errors and len(errors) > 0:
                    return "bad_request"
