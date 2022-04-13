# -*- coding: utf-8 -*-
import datetime as dt
import pandas as pd
import unittest.mock as mock

from django.utils import timezone
from jinja2 import Template

import app.checks.models as models
import app.checks.tasks.expectations as expectations
import app.checks.tasks.pass_values as pass_values

import testutils.cases as cases
import testutils.factories as factories


class CheckQueryTests(cases.ModelTestCase):
    """Test cases for the CheckQuery model class.
    """
    factory = factories.CheckQueryFactory
    model_class = models.CheckQuery

    def test_unique_together(self):
        """It should enforce a UNIQUE constraint.
        """
        self.validate_uniqueness_of(('workspace', 'key',))

    def test_to_template(self):
        """It should enforce a UNIQUE constraint.
        """
        instance = self.factory()
        template = instance.to_template()

        self.assertTrue(isinstance(template, Template))
        self.assertEqual(template.render(), instance.sql_text)


class CheckExpectationTests(cases.ModelTestCase):
    """Test cases for the CheckQuery model class.
    """
    factory = factories.CheckExpectationFactory
    model_class = models.CheckExpectation

    @classmethod
    def setUpTestData(cls):
        cls.instance = factories.CheckExpectationFactory(
            handler_class="app.checks.tasks.expectations.AssertRowCountToBe",
            handler_input={"op": "equal to"},
            pass_value_class="app.checks.tasks.pass_values.Constant",
            pass_value_input={"value": 0})

    def test_description(self):
        """It should render a human-readable description.
        """
        self.assertEqual(
            self.instance.description,
            "Expect the row count to be equal to 0.")

    def test_get_pass_value_class(self):
        """It should return the PassValue class object.
        """
        self.assertEqual(
            self.instance.get_pass_value_class(),
            pass_values.Constant)

    def test_get_handler_class(self):
        """It should return the Handler class object.
        """
        self.assertEqual(
            self.instance.get_handler_class(),
            expectations.AssertRowCountToBe)

    @mock.patch("app.checks.models.CheckExpectation.get_handler_class")
    def test_do_check(self, get_mock):
        """Test the `do_check` method executes.
        """
        handler_class = mock.MagicMock(passed=False, observed_value=42, expected_value=10)
        get_handler_class = lambda *a, **k: handler_class
        get_mock.return_value = get_handler_class

        result = self.instance.do_check(pd.DataFrame([]))

        self.assertTrue(isinstance(result, models.CheckExpectationResult))
        self.assertTrue(handler_class.do_check.called)
        self.assertEqual(result.passed, False)
        self.assertEqual(result.observed_value, 42)
        self.assertEqual(result.expected_value, 10)


class CheckExecutionTests(cases.ModelTestCase):
    """Test cases for the CheckExecution model class.
    """
    factory = factories.CheckExecutionFactory
    model_class = models.CheckExecution

    def test_unique_together(self):
        """It should enforce a UNIQUE constraint.
        """
        self.validate_uniqueness_of(('job', 'epoch',))

    def test_when_completed(self):
        """Test some properties of a completed CheckExecution.
        """
        timestamp = timezone.now()
        execution = self.factory(
            started_at=timestamp - dt.timedelta(seconds=30),
            finished_at=timestamp,
        )

        self.assertEqual(execution.completed, True)
        self.assertEqual(execution.duration, 30)
        self.assertEqual(execution.status, 'SUCCESS')

    def test_when_in_progress(self):
        """Test some properties of a completed CheckExecution.
        """
        timestamp = timezone.now()
        execution = self.factory(
            started_at=timestamp - dt.timedelta(seconds=30),
            finished_at=None,
        )

        self.assertEqual(execution.completed, False)
        self.assertEqual(execution.duration, None)
        self.assertEqual(execution.status, 'PENDING')

    def test_mark_as_started(self):
        """It should set the `started_at` property of the execution.
        """
        execution = self.factory()
        self.assertEqual(execution.started_at, None)

        execution.mark_as_started()
        self.assertTrue(isinstance(execution.started_at, dt.datetime))

    def test_mark_as_finished(self):
        """It should set the `finished_at` property of the execution.
        """
        timestamp = timezone.now()
        execution = self.factory(started_at=timestamp)
        expectations = [
            factories.CheckExpectationFactory(job=execution.job),
            factories.CheckExpectationFactory(job=execution.job),
            factories.CheckExpectationFactory(job=execution.job),
        ]

        execution.mark_as_finished(fails_count=1)

        self.assertEqual(execution.fails_count, 1)
        self.assertEqual(execution.tasks_count, len(expectations))
        self.assertEqual(execution.job.last_execution_id, execution.id)
        self.assertTrue(execution.started_at < execution.finished_at)
