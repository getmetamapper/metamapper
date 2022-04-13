# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from django import test

from app.checks.tasks.context import CheckContext


class CheckContextTests(test.TestCase):
    def test_to_dict(self):
        """Test context dictionary contains expected values.
        """
        epoch = 1652706000
        interval = timedelta(minutes=30)
        context = CheckContext(epoch, interval)

        self.assertEqual(context.to_dict(), {
            'ds': date(2022, 5, 16),
            'tomorrow_ds': date(2022, 5, 17),
            'yesterday_ds': date(2022, 5, 15),
            'execution_date': datetime(2022, 5, 16, 13, 0),
            'next_execution_date': datetime(2022, 5, 16, 13, 30),
            'prev_execution_date': datetime(2022, 5, 16, 12, 30),
        })
