# -*- coding: utf-8 -*-
import collections
import unittest.mock as mock

import testutils.cases as cases
import testutils.factories as factories

import app.checks.alerts.pagerduty as alerter


class PagerDutyAlertConfigValidatorTests(cases.SerializerTestCase):
    """Test cases for the PagerDutyAlertConfigValidator class.
    """
    serializer_class = alerter.PagerDutyAlertConfigValidator

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.request = collections.namedtuple('Request', ['workspace'])(workspace=cls.workspace)
        cls.integration = factories.IntegrationConfigFactory(workspace=cls.workspace, integration='PAGERDUTY')

    def test_when_valid(self):
        attributes = {'integration_id': self.integration.id, 'severity': 'info'}
        serializer = self.serializer_class(data=attributes, context={'request': self.request})

        self.assertTrue(serializer.is_valid())

    def test_when_invalid(self):
        attributes = {'integration_id': 'nope', 'severity': 'info'}
        serializer = self.serializer_class(data=attributes, context={'request': self.request})

        self.assertFalse(serializer.is_valid())


class PagerDutyAlertTests(cases.TestCase):
    """Test cases for the PagerDutyAlert class.
    """
    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.datastore = factories.DatastoreFactory(workspace=cls.workspace)
        cls.integration_id = 'PAGERDUTY'
        cls.integration = factories.IntegrationConfigFactory(workspace=cls.workspace, integration=cls.integration_id)
        cls.channel_config = {'integration_id': cls.integration.id, 'severity': 'error'}
        cls.check = factories.CheckFactory(datastore=cls.datastore)
        cls.check_execution = factories.CheckExecutionFactory(job=cls.check)
        cls.check_alert_rule = factories.CheckAlertRuleFactory(
            job=cls.check,
            channel=cls.integration_id,
            channel_config=cls.channel_config)

    @mock.patch('app.integrations.pagerduty.client.PagerDutyClient.send_trigger')
    def test_send(self, mock_deliver):
        alert_kwargs = {
            'check': self.check,
            'check_execution': self.check_execution,
            'check_error': 'An error has occured.',
        }

        alert = alerter.PagerDutyAlert(self.check_alert_rule, **alert_kwargs)
        alert.send()

        self.assertEqual(mock_deliver.call_count, 1)
