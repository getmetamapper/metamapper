# -*- coding: utf-8 -*-
import app.customfields.models as models

import testutils.cases as cases
import testutils.factories as factories


class CustomFieldTests(cases.ModelTestCase):
    """Test cases for the CustomField model class.
    """
    factory = factories.CustomFieldFactory
    model_class = models.CustomField

    def test_unique_together(self):
        """It should enforce a UNIQUE constraint.
        """
        self.validate_uniqueness_of(('workspace', 'content_type', 'field_name',))


class CustomPropertiesTestsMixin(object):
    """Test cases for a class that has commenting abilities.
    """

    def test_custom_properties(self):
        """It should have the custom_properties attribute.
        """
        self.assertTrue(hasattr(self.factory(), 'custom_properties'))

    def test_get_custom_properties(self):
        """It should return NULL for non-existent fields.
        """
        user = factories.UserFactory()
        workspace = factories.WorkspaceFactory()
        workspace.grant_membership(user, 'OWNER')

        attributes = {
            'content_type': self.model_class.get_content_type(),
            'workspace': workspace,
        }

        customfields = [
            factories.CustomFieldFactory(field_name='Steward', field_type=models.CustomField.USER, **attributes),
            factories.CustomFieldFactory(field_name='Product Area', field_type=models.CustomField.TEXT, **attributes),
            factories.CustomFieldFactory(field_name='Team', field_type=models.CustomField.TEXT, **attributes),
        ]

        resource = self.factory(
            workspace=workspace,
            custom_properties={
                customfields[0].pk: user.pk,
                customfields[2].pk: 'Data Engineering',
            },
        )

        custom_properties = resource.get_custom_properties()
        for customfield in customfields:
            self.assertTrue(customfield.pk in custom_properties)

        self.assertEqual(custom_properties[customfields[0].pk], {
            'label': 'Steward', 'value': user
        })

        self.assertEqual(custom_properties[customfields[2].pk], {
            'label': 'Team', 'value': 'Data Engineering'
        })

    def test_get_custom_properties_deleted_choice(self):
        """It should return NULL for a deleted choice.
        """
        workspace = factories.WorkspaceFactory()

        attributes = {
            'content_type': self.model_class.get_content_type(),
            'workspace': workspace,
        }

        customfield = factories.CustomFieldFactory(
            field_name='Steward',
            field_type=models.CustomField.ENUM,
            validators={'choices': ['red', 'yellow', 'blue']},
            **attributes,
        )

        resource = self.factory(
            workspace=workspace,
            custom_properties={
                customfield.pk: 'blue',
            },
        )

        self.assertEqual(resource.get_custom_properties()[customfield.pk], {
            'label': 'Steward', 'value': 'blue'
        })

        customfield.validators = {'choices': ['red', 'yellow', 'green']}
        customfield.save()

        self.assertEqual(resource.get_custom_properties()[customfield.pk], {
            'label': 'Steward', 'value': None
        })

    def test_get_custom_properties_deleted_user(self):
        """It should return NULL for a deleted choice.
        """
        user = factories.UserFactory()
        workspace = factories.WorkspaceFactory()
        workspace.grant_membership(user, 'OWNER')

        attributes = {
            'content_type': self.model_class.get_content_type(),
            'workspace': workspace,
        }

        customfield = factories.CustomFieldFactory(
            field_name='Steward',
            field_type=models.CustomField.USER,
            **attributes,
        )

        resource = self.factory(
            workspace=workspace,
            custom_properties={
                customfield.pk: user.pk,
            },
        )

        self.assertEqual(resource.get_custom_properties()[customfield.pk], {
            'label': 'Steward', 'value': user
        })

        workspace.revoke_membership(user)

        self.assertEqual(resource.get_custom_properties()[customfield.pk], {
            'label': 'Steward', 'value': None
        })
