# -*- coding: utf-8 -*-
import unittest

from django.core.exceptions import ValidationError
from utils.validators import DomainNameValidator


class UtilsDomainNameValidatorTests(unittest.TestCase):
    """Test that the `DomainNameValidator` class works as expected.
    """
    def test_valid(self):
        """It should not raise any error if the domain is valid.
        """
        test_cases = [
            'metamapper.io',
            'google.com',
            'psych.dev',
            'close.info',
        ]

        validate = DomainNameValidator()

        for test_case in test_cases:
            validate(test_case)

    def test_invalid(self):
        """It should raise a ValidationError if not a domain.
        """
        test_cases = [
            '127.0.0.1',
            'bogus',
            'not a domain',
            'close.',
        ]

        validate = DomainNameValidator()

        for test_case in test_cases:
            self.assertRaises(ValidationError, lambda: validate(test_case))
