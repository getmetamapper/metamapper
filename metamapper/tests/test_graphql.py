# -*- coding: utf-8 -*-
from django.test import override_settings


import testutils.cases as cases
import testutils.factories as factories


class TestBeaconActivated(cases.GraphQLTestCase):
    """
    """
    factory = factories.WorkspaceFactory
    operation = 'beaconActivated'
    statement = '''
    query {
      beaconActivated
    }
    '''

    @override_settings(METAMAPPER_BEACON_ACTIVATED=True)
    def test_beacon_activated_truthy(self):
        """It should return True when the beacon setting is activated.
        """
        results = self.execute(self.statement)
        results = results['data'][self.operation]

        self.assertTrue(results)

    @override_settings(METAMAPPER_BEACON_ACTIVATED=False)
    def test_beacon_activated_falsey(self):
        """It should return False when the beacon setting is deactivated.
        """
        results = self.execute(self.statement)
        results = results['data'][self.operation]

        self.assertFalse(results)
