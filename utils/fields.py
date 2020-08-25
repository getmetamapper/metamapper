# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import ip_address_validators

from django.utils.ipv6 import clean_ipv6_address
from django.utils.translation import gettext_lazy as _

from rest_framework import fields as drf_fields
from utils.regexp import host_regex


class HostnameField(drf_fields.CharField):
    """Support a valid DNS hostname.
    """
    allowed_protocols = ('both', 'ipv4', 'ipv6')

    default_error_messages = {
        'invalid': _('Enter a valid hostname.'),
    }

    def __init__(self, protocol=None, **kwargs):
        self.protocol = protocol.lower() if protocol else None
        self.unpack_ipv4 = (self.protocol == 'both')

        if self.protocol and self.protocol not in self.allowed_protocols:
            raise ValueError('Protocol is not supported: %s' % self.protocol)

        super().__init__(**kwargs)

        if self.protocol:
            validators, error_message = ip_address_validators(protocol, self.unpack_ipv4)
            self.validators.extend(validators)

    def to_internal_value(self, data):
        """Validate the value coming in to be saved on the instance.
        """
        if not isinstance(data, str):
            self.fail('invalid', value=data)

        if ':' in data:
            try:
                if self.protocol in ('both', 'ipv6'):
                    return clean_ipv6_address(data, self.unpack_ipv4)
            except DjangoValidationError:
                self.fail('invalid', value=data)
        else:
            if not host_regex.match(data):
                self.fail('invalid', value=data)

        return super().to_internal_value(data)


class SysnameField(drf_fields.RegexField):
    """Support a valid system name (e.g., username, database name, etc.)
    """
    default_error_messages = {
        'invalid': _('The provided value does not match the required pattern.')
    }

    def __init__(self, *args, **kwargs):
        super().__init__(regex=r'^[0-9a-zA-Z$_-]+$', *args, **kwargs)


class PortField(drf_fields.IntegerField):
    """Support a valid port between 0 and 65535.
    """
    default_error_messages = {
        'max_value': _('Port value must be between 0 and 65535.'),
        'min_value': _('Port value must be between 0 and 65535.'),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(min_value=0, max_value=65535, *args, **kwargs)


class RelatedObjectField(drf_fields.Field):
    """Pass in a related model instance.
    """
    default_error_messages = {
        'invalid': _('The field is not of a valid type.'),
        'null': _('This field cannot be null.'),
    }

    def __init__(self, allowed_models, allow_null=False, **kwargs):
        super().__init__(**kwargs)
        self.allowed_models = allowed_models
        self.allow_null = allow_null

    def to_internal_value(self, value):
        """Validate the value coming in to be saved on the instance.
        """
        if self.allow_null and value is None:
            return value

        if not isinstance(value, self.allowed_models):
            self.fail('invalid', value=value)

        if not self.allow_null and not value:
            self.fail('null', value=value)

        return value
