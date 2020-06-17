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

    def test_get_custom_properties_disabled_field(self):
        """It should not return a disable field,.
        """
        workspace = factories.WorkspaceFactory()

        attributes = {
            'content_type': self.model_class.get_content_type(),
            'workspace': workspace,
        }

        customfield = factories.CustomFieldFactory(
            field_name='Steward',
            **attributes,
        )

        custom_properties = {
            customfield.pk: "Sam Crust",
        }

        resource = self.factory(
            workspace=workspace,
            disabled_datastore_properties=[customfield.pk],
            custom_properties=custom_properties,
        )

        self.assertEqual(resource.custom_properties, custom_properties)
        self.assertEqual(resource.get_custom_properties(), {})


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
