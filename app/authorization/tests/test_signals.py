# -*- coding: utf-8 -*-
import testutils.cases as cases
import testutils.factories as factories

import app.authorization.models as models


class TestAuthorizationSignals(cases.TestCase):
    """Test cases for signals triggered via certain actions.
    """
    def test_remove_revoked_user_from_groups(self):
        """It should remove a User from all workspace groups when membership is revoked.
        """
        user = factories.UserFactory()

        workspace = factories.WorkspaceFactory(name='Metameta')
        workspace.grant_membership(user, models.Membership.READONLY)

        group = factories.GroupFactory(workspace_id=workspace.id)
        group.user_set.add(user)

        self.assertTrue(user.groups.filter(name=group.name).exists())

        workspace.revoke_membership(user)

        self.assertFalse(user.groups.filter(name=group.name).exists())
