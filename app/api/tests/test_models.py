# -*- coding: utf-8 -*-
import re
import app.api.models as models

import testutils.cases as cases
import testutils.factories as factories


class ApiTokenTests(cases.ModelTestCase):
    """Test cases for the ApiToken model class.
    """
    factory = factories.ApiTokenFactory
    model_class = models.ApiToken

    def test_unique_together(self):
        """It should enforce a UNIQUE constraint.
        """
        self.validate_uniqueness_of(('workspace', 'name',))

    def test_get_secret(self):
        """It should return a de-crypted token.
        """
        instance = self.factory()

        self.assertTrue(
            re.match(r'^[a-zA-Z0-9]{60}$', instance.get_secret()))
