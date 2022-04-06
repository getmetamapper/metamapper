# -*- coding: utf-8 -*-
from django.utils.translation import gettext_lazy as _

from rest_framework import status, views
from rest_framework.exceptions import APIException


class PermissionDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('You do not have permission to perform this action.')
    default_code = 'forbidden'


class NotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Resource could not be found.')
    default_code = 'notFound'


class ParameterValidationFailed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Parameter validation failed.')
    default_code = 'parameterValidation'


def exception_handler(exc, context):
    response = views.exception_handler(exc, context)

    if response is not None:
        response.data['success'] = False
        response.data['error'] = {
            'code': response.status_code,
            'message': response.data.pop('detail', 'Sorry, an error occurred.'),
        }

    return response
