# -*- coding: utf-8 -*-
from unittest import mock

from django.db.utils import OperationalError
from django.test import TestCase, Client
from django.urls import reverse

from app.healthchecks.models import Heartbeat


class HealthcheckViewTests(TestCase):
    """Test cases for `healthcheck` endpoint.
    """
    def setUp(self):
        self.client = Client(HTTP_HOST='example.com')
        self.heartbeat = Heartbeat.objects.beat()

    def test_when_valid(self):
        response = self.client.get(reverse('healthcheck'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'metastore': {
                'status': 'healthy',
            },
            'scheduler': {
                'status': 'healthy',
                'latest_scheduler_heartbeat': self.heartbeat.ts,
            },
            'worker': {
                'status': 'healthy',
            },
        })

    def test_scheduler_fails(self):
        Heartbeat.objects.all().delete()

        response = self.client.get(reverse('healthcheck'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'metastore': {
                'status': 'healthy',
            },
            'scheduler': {
                'status': 'unhealthy',
                'latest_scheduler_heartbeat': None,
            },
            'worker': {
                'status': 'healthy',
            },
        })

    @mock.patch('app.healthchecks.tasks.add.apply_async')
    def test_worker_fails(self, mock_task):
        mock_task.return_value.get.return_value = None

        response = self.client.get(reverse('healthcheck'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'metastore': {
                'status': 'healthy',
            },
            'scheduler': {
                'status': 'healthy',
                'latest_scheduler_heartbeat': self.heartbeat.ts,
            },
            'worker': {
                'status': 'unhealthy',
            },
        })

    @mock.patch('app.healthchecks.tasks.add.apply_async')
    @mock.patch('django.contrib.contenttypes.models.ContentType.objects.first')
    def test_metastore_fails(self, mock_first, mock_task):
        mock_first.side_effect = OperationalError()
        mock_task.return_value.get.return_value = None

        response = self.client.get(reverse('healthcheck'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'metastore': {
                'status': 'unhealthy',
            },
            'scheduler': {
                'status': 'healthy',
                'latest_scheduler_heartbeat': self.heartbeat.ts,
            },
            'worker': {
                'status': 'unhealthy',
            },
        })
