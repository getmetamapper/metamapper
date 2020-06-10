# -*- coding: utf-8 -*-
import datetime as dt
import unittest.mock as mock

import app.sso.models as models
import app.sso.tasks as tasks

import testutils.cases as cases
import testutils.factories as factories

from django.utils import timezone


class QueueDomainVerificationsTaskTests(cases.TestCase):
    """Test cases for queueing SSO domains for verification.
    """
    factory = factories.SSODomainFactory

    @classmethod
    def setUpTestData(cls):
        cls.count = 4
        cls.workspace = factories.WorkspaceFactory()
        cls.domains = cls.factory.create_batch(cls.count, workspace=cls.workspace)

    @mock.patch('app.sso.tasks.verify_domain.apply_async')
    def test_execution(self, mock_verify_domain):
        """It should queue domains that have not been processed recently.
        """
        domain = self.domains[0]
        domain.last_attempted_at = timezone.now()
        domain.save()

        tasks.queue_domain_verifications()

        mock_verify_domain.call_count = self.count + 1


class VerifyDomainTaskTests(cases.TestCase):
    """Test cases for verifying an SSO domain.
    """
    factory = factories.SSODomainFactory

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()

    @mock.patch('dns.resolver.query')
    def test_when_record_exists(self, mock_dns_query):
        domain = self.factory(workspace=self.workspace)

        mock_1 = mock.MagicMock()
        mock_1.to_text.return_value = 'metamapper-domain-verification=%s' % domain.verification_token

        mock_2 = mock.MagicMock()
        mock_2.to_text.return_value = 'cname=123214123123'

        mock_dns_query.return_value = [
            mock_1,
            mock_2,
        ]

        tasks.verify_domain(domain.domain)
        domain.refresh_from_db()

        self.assertTrue(domain.verified)

    @mock.patch('dns.resolver.query')
    def test_when_record_does_not_exist(self, mock_dns_query):
        domain = self.factory(workspace=self.workspace)

        mock_1 = mock.MagicMock()
        mock_1.to_text.return_value = 'metamapper-domain-verification=asdf12m1231laMk441023a'

        mock_2 = mock.MagicMock()
        mock_2.to_text.return_value = 'cname=123214123123'

        mock_dns_query.return_value = [
            mock_1,
            mock_2,
        ]

        tasks.verify_domain(domain.domain)
        domain.refresh_from_db()

        self.assertFalse(domain.verified)


class DeleteFailedDomainsTaskTests(cases.TestCase):
    """Test cases for cleaning up failed domains.
    """
    factory = factories.SSODomainFactory

    @classmethod
    def setUpTestData(cls):
        cls.count = 4
        cls.workspace = factories.WorkspaceFactory()
        cls.domains = cls.factory.create_batch(cls.count, workspace=cls.workspace)

    def test_execution(self):
        """It should delete any domains that have reached the attempt limit.
        """
        domain = self.domains[0]
        domain.attempts = models.SSODomain.MAX_ATTEMPTS + 5
        domain.last_attempted_at = timezone.now() - dt.timedelta(days=7)
        domain.save()

        tasks.delete_failed_domains()

        self.workspace.refresh_from_db()

        self.assertEqual(
            self.workspace.sso_domains.count(),
            self.count - 1,
        )
