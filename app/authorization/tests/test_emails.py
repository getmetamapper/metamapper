# -*- coding: utf-8 -*-
import unittest.mock as mock

import testutils.cases as cases
import testutils.factories as factories

import app.authorization.models as models
import app.authorization.emails as emails


class TestAuthorizationEmails(cases.TestCase):
    """Test cases for outbound emailing capabilities related to authorization.
    """
    @mock.patch('app.notifications.email.Mailer.deliver')
    def test_membership_granted_when_exists(self, mock_deliver):
        """It should call the Mailer.deliver method with the proper template.
        """
        user = factories.UserFactory()
        workspace = factories.WorkspaceFactory(name='Metameta')

        emails.membership_granted(user.email, workspace, models.Membership.READONLY)

        mock_deliver.assert_called_with(
            user.email,
            'You have granted the Readonly role to the Metameta workspace',
            {
                'to_address': user.email,
                'workspace_name': workspace.name,
                'user_exists': True,
                'permissions': 'Readonly',
            },
        )

    @mock.patch('app.notifications.email.Mailer.deliver')
    def test_ownership_membership_granted_when_exists(self, mock_deliver):
        """It should call the Mailer.deliver method with the proper template.
        """
        email = 'nobody@metamapper.io'
        workspace = factories.WorkspaceFactory(name='Metameta')

        emails.membership_granted(email, workspace, models.Membership.OWNER)

        mock_deliver.assert_called_with(
            email,
            'You have granted the Owner role to the Metameta workspace',
            {
                'to_address': email,
                'workspace_name': workspace.name,
                'user_exists': False,
                'permissions': 'Owner',
            },
        )

    @mock.patch('app.notifications.email.Mailer.deliver')
    def test_membership_revoked(self, mock_deliver):
        """It should call the Mailer.deliver method with the proper template.
        """
        email = 'nobody@metamapper.io'
        workspace = factories.WorkspaceFactory(name='Metameta')

        emails.membership_revoked(email, workspace)

        mock_deliver.assert_called_with(
            email,
            'You have been removed from the Metameta workspace',
            {
                'to_address': email,
                'workspace_name': workspace.name,
            },
        )
