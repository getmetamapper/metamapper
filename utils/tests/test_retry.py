# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock
import logging

import utils.retry as retry


logger = logging.getLogger(__name__)


class UtilsRetryDecoratorTests(unittest.TestCase):
    """Test that the `retry` decorator works properly.
    """
    def test_valid_exceptions(self):
        """It should retry exceptions passed as a list.
        """
        expected = "This is what I want to return"

        side_effect = [
            ValueError('One'),
            ValueError('Two'),
            expected,
        ]

        fcn, mocked_fcn = self.make_fcn((ValueError, TypeError,), side_effect)

        self.assertEqual(fcn(), expected)
        self.assertEqual(mocked_fcn.call_count, len(side_effect))

    def test_ignored_exception(self):
        """It should raise exception classes that aren't whitelisted.
        """
        expected = 'This is what I want to return'

        side_effect = [
            TypeError('One'),
            ValueError('Two'),
            expected,
        ]

        fcn, mocked_fcn = self.make_fcn((TypeError,), side_effect)

        self.assertRaisesRegex(ValueError, 'Two', fcn)
        self.assertEqual(mocked_fcn.call_count, 2)

    def test_more_than_normal_tries(self):
        """It should allow for the number of retries to be configurable.
        """
        expected = 'This is what I want to return'

        side_effect = [
            TypeError(i) for i in range(5)
        ]
        side_effect.append(expected)

        fcn, mocked_fcn = self.make_fcn((TypeError,), side_effect, tries=6)

        self.assertEqual(fcn(), expected)
        self.assertEqual(mocked_fcn.call_count, 6)

    def make_fcn(self, exceptions, side_effect, tries=4):
        """Helper method to create the test function.
        """
        mocked_fcn = mock.Mock()
        mocked_fcn.side_effect = side_effect

        @retry.retry(exceptions, tries=tries, delay=0.1, logger=logger)
        def call():
            """Call the mocked function to simulate exception handling.
            """
            return mocked_fcn()

        return call, mocked_fcn
