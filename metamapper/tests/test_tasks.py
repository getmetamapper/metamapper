# -*- coding: utf-8 -*-
import unittest.mock as mock

from django.test import override_settings

import testutils.cases as cases
import testutils.factories as factories

from metamapper import tasks, __version__


class BeaconUsageTaskTests(cases.UserFixtureMixin, cases.TestCase):
    """Test cases for sending usage to the beacon.
    """
    load_data = ['workspaces.json', 'users.json', 'comments.json', 'customfields.json']

    @mock.patch('requests.post')
    def test_execution(self, mock_http_request):
        """It should only ping the beacon if enabled on the workspace.
        """
        workspaces = factories.WorkspaceFactory.create_batch(5, beacon_consent=True)
        mock_http_request.return_value = mock.MagicMock(status_code=200)

        tasks.send_beacon()

        self.assertEqual(mock_http_request.call_count, len(workspaces))

    @mock.patch('requests.post')
    @override_settings(SECRET_KEY='meowmeowmeow')
    def test_execution_content(self, mock_http_request):
        """It should provide the correct data.
        """
        self.workspace.beacon_consent = True
        self.workspace.save()

        mock_http_request.return_value = mock.MagicMock(status_code=200)

        tasks.send_beacon()

        mock_http_request.assert_called()
        mock_http_request.assert_called_with(
            headers={'Content-Type': 'application/json'},
            json={
                'docker': False,
                'version': 'v%s' % __version__,
                'install_id': '29eda88ef0cff1bf5ced0821a6ed82eab16721a2',
                'workspace_id': str(self.workspace.pk),
                'usage': {
                    'team': 5,
                    'datastores': 1,
                    'groups': 2,
                    'comments': 5,
                    'customfields': 5,
                    'customproperties': 1,
                },
            },
            timeout=5,
            url='https://beacon.metamapper.cloud/usage',
        )

    @mock.patch('requests.post')
    @override_settings(METAMAPPER_BEACON_ACTIVATED=False)
    def test_when_globally_disabled(self, mock_http_request):
        """It should never call any beacon if it is globally disabled.
        """
        self.workspace.beacon_consent = True
        self.workspace.save()

        tasks.send_beacon()

        self.assertEqual(mock_http_request.call_count, 0)
