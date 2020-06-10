# -*- coding: utf-8 -*-
import os

import unittest
import unittest.mock as mock

from metamapper.celery import app


class MetamapperCeleryTest(unittest.TestCase):
    """Base test cases for Celery and Metamapper.
    """
    def test_defaults(self):
        """It preloads some default parameters.
        """
        self.assertEqual(app.conf.broker_url, os.getenv('METAMAPPER_CELERY_BROKER_URL'))
        self.assertEqual(app.conf.task_serializer, 'json')
        self.assertEqual(app.conf.result_serializer, 'json')
        self.assertEqual(app.conf.task_default_queue, 'celery')

    @mock.patch.dict(os.environ, {'METAMAPPER_CELERY_CONFIG_MODULE': 'testutils.config.override_celery'})
    def test_overrides(self):
        """It can overload the Celery configuration using the `METAMAPPER_CELERY_CONFIG_MODULE` env var.
        """
        app.config_from_envvar('METAMAPPER_CELERY_CONFIG_MODULE')

        self.assertEqual(app.conf.broker_url, 'amqp://guest:guest@localhost:5672//')
        self.assertEqual(app.conf.task_serializer, 'pickle')
        self.assertEqual(app.conf.result_serializer, 'pickle')
        self.assertEqual(app.conf.task_default_queue, 'default')
