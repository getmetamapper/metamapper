# -*- coding: utf-8 -*-
import utils.regexp as regexp

from django.utils.encoding import force_text
from django.core.exceptions import ValidationError


class DomainNameValidator(object):
    """Domain name validator adapted from Django's EmailValidator.
    """
    message = 'Enter a valid domain name.'
    code = 'invalid'
    domain_regex = regexp.domain_regex

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        value = force_text(value)

        if not value:
            raise ValidationError(self.message, code=self.code)

        if not self.domain_regex.match(value):
            # Try for possible IDN domain-part
            try:
                value = value.encode('idna').decode('ascii')
                if not self.domain_regex.match(value):
                    raise ValidationError(self.message, code=self.code)
                else:
                    return
            except UnicodeError:
                pass
            raise ValidationError(self.message, code=self.code)
