# -*- coding: utf-8 -*-
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException


class PermissionDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('You do not have permission to perform this action.')
    default_code = 'forbidden'


class NotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Resource could not be found.')
    default_code = 'not_found'


class ParameterValidationFailed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Parameter validation failed.')
    default_code = 'parameter_validation'
