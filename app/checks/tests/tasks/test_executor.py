# -*- coding: utf-8 -*-
import datetime as dt
import pandas as pd
import unittest.mock as mock

import testutils.assertions as assertions
import testutils.factories as factories

from django import test

from app.checks.models import CheckExecution
from app.checks.tasks.context import CheckContext
from app.checks.tasks.executor import CheckExecutor


class CheckExecutorTests(assertions.InstanceAssertionsMixin, test.TestCase):
    EXPECTATIONS_FIXTURES = [
        {
            'handler_class': 'app.checks.tasks.expectations.AssertRowCountToBe',
            'handler_input': {'op': 'equal to'},
            'pass_value_class': 'app.checks.tasks.pass_values.Constant',
            'pass_value_input': {'value': 0},
        }
    ]

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.datastore = factories.DatastoreFactory(workspace=cls.workspace)
        cls.query = factories.CheckQueryFactory(datastore=cls.datastore)
        cls.check = factories.CheckFactory(datastore=cls.datastore)
        cls.context = CheckContext(1652706000, dt.timedelta(minutes=30))

    def test_execute_without_expectations(self):
        """It should disable the check if no expectations exist.
        """
        execution = factories.CheckExecutionFactory(job=self.check)

        executor = CheckExecutor(execution, upload_archive=False)
        executor.execute(context=self.context)

        self.assertFalse(self.check.is_enabled)
        self.assertInstanceDeleted(CheckExecution, id=execution.id)

    @mock.patch.object(CheckExecutor, 'get_dataframe')
    def test_execute_passed(self, mock_get_dataframe):
        """It should execute the checks as expected.
        """
        mock_get_dataframe.return_value = pd.DataFrame([])

        for expectation in self.EXPECTATIONS_FIXTURES:
            factories.CheckExpectationFactory(job=self.check, **expectation)

        execution = factories.CheckExecutionFactory(job=self.check)

        executor = CheckExecutor(execution, upload_archive=False)
        executor.execute(context=self.context)

        self.assertEqual(
            len(self.EXPECTATIONS_FIXTURES),
            execution.expectation_results.filter(passed=True).count())

    @mock.patch.object(CheckExecutor, 'get_dataframe')
    def test_execute_failed(self, mock_get_dataframe):
        """It should execute the checks as expected.
        """
        mock_get_dataframe.return_value = pd.DataFrame([
            {'id': 1},
            {'id': 2},
            {'id': 3},
        ])

        for expectation in self.EXPECTATIONS_FIXTURES:
            factories.CheckExpectationFactory(job=self.check, **expectation)

        execution = factories.CheckExecutionFactory(job=self.check)

        executor = CheckExecutor(execution, upload_archive=False)
        executor.execute(context=self.context)

        self.assertTrue(mock_get_dataframe.called)
        self.assertEqual(
            len(self.EXPECTATIONS_FIXTURES),
            execution.expectation_results.filter(passed=False).count())
