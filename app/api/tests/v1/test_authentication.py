# -*- coding: utf-8 -*-
import testutils.cases as cases
import testutils.factories as factories
import testutils.helpers as helpers


class TestV1ApiAuthentication(cases.ApiTestCase):
    """Test if API can authenticate users.
    """
    def get_api_client(self, secret=None, workspace=None, authenticated=True):
        uuid = None
        wksp = workspace or self.workspace
        if wksp and hasattr(wksp, 'id'):
            uuid = wksp.id
        api_client_kwargs = {
            'secret': secret or self.api_token_secret,
            'uuid': uuid,
            'authenticated': authenticated,
        }
        return helpers.api_client(**api_client_kwargs)

    def test_valid(self):
        client = self.get_api_client()
        result = client.get('/api/v1/datastores')

        self.assertEqual(result.status_code, 200)

    def test_disabled(self):
        self.api_token.is_enabled = False
        self.api_token.save()

        client = self.get_api_client()
        result = client.get('/api/v1/datastores')

        self.assertPermissionDenied(result)

    def test_without_headers(self):
        client = self.get_api_client(authenticated=False)
        result = client.get('/api/v1/datastores')

        self.assertPermissionDenied(result)

    def test_invalid_token(self):
        client = self.get_api_client(secret='meowmeowmeow')
        result = client.get('/api/v1/datastores')

        self.assertPermissionDenied(result)

    def test_invalid_workspace(self):
        client = self.get_api_client(workspace=factories.WorkspaceFactory())
        result = client.get('/api/v1/datastores')

        self.assertPermissionDenied(result)
