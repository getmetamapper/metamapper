# -*- coding: utf-8 -*-
import collections
import unittest.mock as mock

import testutils.cases as cases
import testutils.factories as factories

import app.checks.alerts.email as alerter


class EmailAlertConfigValidatorTests(cases.SerializerTestCase):
    """Test cases for the EmailAlertConfigValidator class.
    """
    serializer_class = alerter.EmailAlertConfigValidator

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.request = collections.namedtuple('Request', ['workspace'])(workspace=cls.workspace)

    def test_when_valid(self):
        attributes = {'emails': ['scott@metamapper.io', 'alerts@metamapper.io']}
        serializer = self.serializer_class(data=attributes, context={'request': self.request})

        self.assertTrue(serializer.is_valid())

    def test_when_invalid(self):
        attributes = {'emails': ['scott@metamapper.io', 'alerts']}
        serializer = self.serializer_class(data=attributes, context={'request': self.request})

        self.assertFalse(serializer.is_valid())


class EmailAlertTests(cases.TestCase):
    """Test cases for the EmailAlert class.
    """
    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.datastore = factories.DatastoreFactory(workspace=cls.workspace)
        cls.integration_id = 'EMAIL'
        cls.channel_config = {'emails': ['test1@metamapper.io', 'test2@metamapper.io']}
        cls.check = factories.CheckFactory(datastore=cls.datastore)
        cls.check_execution = factories.CheckExecutionFactory(job=cls.check)
        cls.check_alert_rule = factories.CheckAlertRuleFactory(
            job=cls.check,
            channel=cls.integration_id,
            channel_config=cls.channel_config)

    @mock.patch('app.notifications.tasks.deliver.delay')
    def test_send(self, mock_deliver):
        alert_kwargs = {
            'check': self.check,
            'check_execution': self.check_execution,
            'check_error': 'An error has occured.',
        }

        alert = alerter.EmailAlert(self.check_alert_rule, **alert_kwargs)
        alert.send()

        self.assertEqual(mock_deliver.call_count, len(self.channel_config['emails']))
