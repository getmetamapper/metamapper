# -*- coding: utf-8 -*-
import unittest
import uuid

import utils.regexp as regexp

from django.utils.crypto import get_random_string


class UtilsRegularExpressionsTests(unittest.TestCase):
    """Test that regex patterns behave as expected.
    """
    def test_ipv4_regex(self):
        """It should correctly match an IP address.
        """
        test_cases = [
            ('127.0.0.1', True),
            ('54.12.44.21', True),
            ('132.124.22.32', True),
            ('localhost', False),
            ('metamapper.com', False),
        ]

        for test_case, assertion in test_cases:
            self.assertEqual(bool(regexp.ipv4_regex.match(test_case)), assertion)

    def test_host(self):
        """It should correctly match a fully-qualified domain name.
        """
        test_cases = [
            ('app.metamapper.io', True),
            ('app.tech.metamapper.dev', True),
            ('www.google.com', True),
            ('google.com', True),
        ]

        for test_case, assertion in test_cases:
            self.assertEqual(bool(regexp.host_regex.match(test_case)), assertion)

    def test_domain(self):
        """It should correctly match a domain name.
        """
        test_cases = [
            ('metamapper.io', True),
            ('google.com', True),
        ]

        for test_case, assertion in test_cases:
            self.assertEqual(bool(regexp.domain_regex.match(test_case)), assertion)

    def test_uuid(self):
        """It should correctly match a UUIDv4 string.
        """
        for i in range(10):
            self.assertTrue(bool(regexp.uuid_regex.match(str(uuid.uuid4()))))

        for i in range(10):
            self.assertFalse(bool(regexp.uuid_regex.match(get_random_string(10))))

    def test_str_pk_regex(self):
        """It should correctly match a surrogate key string.
        """
        test_cases = [
            (12, True),
            (12, True),
            (12, True),
            (20, False),
            (10, False),
            (8, False),
            (6, False),
        ]

        for test_case, assertion in test_cases:
            surrogate = get_random_string(test_case)
            self.assertEqual(
                bool(regexp.str_pk_regex.match(surrogate)),
                assertion,
            )

    def test_domain_verification(self):
        """It should correctly match a JWT.
        """
        test_cases = [
            ("metamapper-domain-verification=%s" % get_random_string(30), True),
            ("metamapper-domain-verification=%s" % get_random_string(40), True),
            ("metamapper-verify=", False),
            ("not-a-valid-match", False),
        ]

        for test_case, assertion in test_cases:
            self.assertEqual(
                bool(regexp.domain_verification_regex.match(test_case)),
                assertion,
            )

    def test_jwt_when_valid(self):
        """It should correctly match a JWT.
        """
        test_case = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey"
            "JzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ikpva"
            "G4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKx"
            "wRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )

        self.assertTrue(bool(regexp.jwt_regex.match(test_case)))

    def test_jwt_when_invalid(self):
        """It should correctly match a JWT.
        """
        self.assertFalse(bool(regexp.jwt_regex.match(str(uuid.uuid4()))))
