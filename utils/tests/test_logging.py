# -*- coding: utf-8 -*-
import unittest
import logging as pylogging

import utils.logging as logging


class UtilsLoggingTests(unittest.TestCase):
    """Documentatoion coming soon.
    """
    @classmethod
    def setUpClass(cls):
        pylogging.disable(pylogging.NOTSET)

    @classmethod
    def tearDownClass(cls):
        pylogging.disable(pylogging.CRITICAL)

    def test_with_extras(self):
        """It should append the `extras` dictionary to the logger.
        """
        logger = logging.Logger('app.testing', {'user': '12345'})

        with self.assertLogs(logger.name, level=pylogging.INFO) as cm:
            logger.info('This is the first log.')
            logger.info('This is the second log.')
            logger.warning('This is the third log.')

        self.assertEqual(cm.output, [
            'INFO:app.testing:(user: 12345) This is the first log.',
            'INFO:app.testing:(user: 12345) This is the second log.',
            'WARNING:app.testing:(user: 12345) This is the third log.',
        ])

    def test_with_fields(self):
        """It should append the `extras` dictionary to the logger.
        """
        logger = logging.Logger('app.testing', {'user': '12345'})
        logger.with_fields(pid=10)

        with self.assertLogs(logger.name, level=pylogging.INFO) as cm:
            logger.info('This is the first log.')
            logger.info('This is the second log.')

        self.assertEqual(cm.output, [
            'INFO:app.testing:(user: 12345) (pid: 10) This is the first log.',
            'INFO:app.testing:(user: 12345) (pid: 10) This is the second log.',
        ])
