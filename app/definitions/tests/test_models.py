# -*- coding: utf-8 -*-
import app.definitions.models as models

import testutils.cases as cases
import testutils.factories as factories

from app.comments.tests.test_models import CommentableTestsMixin
from app.customfields.tests.test_models import CustomPropertiesTestsMixin


class DatastoreTests(CustomPropertiesTestsMixin, cases.ModelTestCase):
    """Test cases for the Datastore model class.
    """
    factory = factories.DatastoreFactory
    model_class = models.Datastore


class TableTests(CommentableTestsMixin, CustomPropertiesTestsMixin, cases.ModelTestCase):
    """Test cases for the Table model class.
    """
    factory = factories.TableFactory
    model_class = models.Table


class ColumnTests(CommentableTestsMixin, cases.ModelTestCase):
    """Test cases for the Column model class.
    """
    factory = factories.ColumnFactory
    model_class = models.Column
