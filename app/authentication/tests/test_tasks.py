# -*- coding: utf-8 -*-
import testutils.cases as cases
import app.authentication.tasks as tasks

from app.authentication.models import Workspace
from app.definitions.models import Datastore, Table, AssetOwner
from app.comments.models import Comment


class HardDeleteWorkspaceTests(cases.UserFixtureMixin, cases.TestCase):
    """Test cases for background task to delete workspace.
    """
    load_data = ['workspaces.json', 'datastore.json', 'users.json', 'comments.json']
    workspace_id = 'f4bb0aabc51d458a9eab58ed80fa2d6c'

    def test_execution(self):
        """It should delete all the associated objects.
        """
        datastore_count = Datastore.objects.count()
        comments_count = Comment.objects.count()
        tables_count = Table.objects.count()
        owners_count = AssetOwner.objects.count()

        tasks.hard_delete_workspace(self.workspace_id)

        self.assertTrue(Workspace.objects.filter(id=self.workspace_id).first() is None)
        self.assertTrue(Datastore.objects.count() < datastore_count)
        self.assertTrue(Comment.objects.count() < comments_count)
        self.assertTrue(Table.objects.count() < tables_count)
        self.assertTrue(AssetOwner.objects.count() < owners_count)
