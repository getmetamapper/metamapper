# -*- coding: utf-8 -*-
import unittest.mock as mock

import testutils.cases as cases

import app.authentication.emails as emails


class TestAuthenticationEmails(cases.TestCase):
    """Test cases for outbound emailing capabilities related to authentication.
    """
    @mock.patch('app.notifications.email.Mailer.deliver')
    def test_reset_password(self, mock_deliver):
        """It should call the Mailer.deliver method with the proper template.
        """
        uid = '1'
        email = 'owner@metamapper.io'
        token = 'meowmeowmeow'

        emails.reset_password(email, uid, token)

        mock_deliver.assert_called_with(
            email,
            'Here\'s a link to reset your password',
            {'email': email, 'token': token, 'uid': uid},
        )

    @mock.patch('app.notifications.email.Mailer.deliver')
    def test_password_was_reset(self, mock_deliver):
        """It should call the Mailer.deliver method with the proper template.
        """
        email = 'owner@metamapper.io'

        emails.password_was_reset(email)

        mock_deliver.assert_called_with(
            email,
            'Your Metamapper password was changed',
            {'to_address': email},
        )
