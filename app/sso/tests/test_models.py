# -*- coding: utf-8 -*-
import app.sso.models as models
import app.authentication.models as authmodels

import testutils.cases as cases
import testutils.factories as factories

from django.utils.crypto import get_random_string


class SSOConnectionModelTests(cases.ModelTestCase):
    """Test cases for the SSOConnection model class.
    """
    factory = factories.SSOConnectionFactory
    model_class = models.SSOConnection

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()

    def test_workspace_association(self):
        """It has a Workspace association.
        """
        resource = self.factory(workspace=self.workspace)
        self.assertTrue(isinstance(resource.workspace, authmodels.Workspace))


class SSODomainModelTests(cases.ModelTestCase):
    """Test cases for the SSODomain model class.
    """
    factory = factories.SSODomainFactory
    model_class = models.SSODomain

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()

    def test_workspace_association(self):
        """It has a Workspace association.
        """
        resource = self.factory(workspace=self.workspace)
        self.assertTrue(isinstance(resource.workspace, authmodels.Workspace))

    def test_verification_failed(self):
        """Should return False is verification attempted too many times.
        """
        resource = self.factory(workspace=self.workspace)
        self.assertFalse(resource.verification_failed)
        resource.attempts = 20
        resource.save()
        resource.refresh_from_db()
        self.assertTrue(resource.verification_failed)

    def test_verify_TXT_record_valid(self):
        """Should return True when there is a match.
        """
        resource = self.factory(workspace=self.workspace)
        resource.save()

        token = "metamapper-domain-verification=%s" % resource.verification_token

        self.assertTrue(resource.verify_TXT_record(token))

    def test_verify_TXT_record_invalid(self):
        """Should return False when there is NOT a match.
        """
        resource = self.factory(workspace=self.workspace)
        resource.save()

        token = "metamapper-domain-verification=%s" % get_random_string(models.SSODomain.TOKEN_LENGTH)

        self.assertFalse(resource.verify_TXT_record(token))
