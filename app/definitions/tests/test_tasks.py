# -*- coding: utf-8 -*-
import testutils.cases as cases
import app.definitions.tasks as tasks


from app.definitions.models import Datastore, Table, AssetOwner
from app.comments.models import Comment


class HardDeleteDatastoreTests(cases.UserFixtureMixin, cases.TestCase):
    """Test cases for background task to delete datastore.
    """
    load_data = ['workspaces.json', 'datastore.json', 'users.json', 'comments.json']
    datastore_id = 's4N8p5g0wjiS'

    def test_execution(self):
        """It should delete all the associated objects.
        """
        comments_count = Comment.objects.count()
        tables_count = Table.objects.count()
        owners_count = AssetOwner.objects.count()

        tasks.hard_delete_datastore(self.datastore_id)

        self.assertTrue(Datastore.objects.filter(id=self.datastore_id).first() is None)
        self.assertTrue(Comment.objects.count() < comments_count)
        self.assertTrue(Table.objects.count() < tables_count)
        self.assertTrue(AssetOwner.objects.count() < owners_count)
