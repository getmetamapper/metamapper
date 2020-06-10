# -*- coding: utf-8 -*-
import json

import testutils.cases as cases
import testutils.factories as factories


from utils.encoders import DjangoPartialModelJsonEncoder


class DjangoPartialModelJsonEncoderTests(cases.TestCase):
    """Test that the DjangoPartialModelJsonEncoder can encode Django models.
    """
    def test_encode_string_pk_model(self):
        """It should partially encode a Django model.
        """
        datastore = factories.DatastoreFactory()

        resource = json.dumps(
            datastore,
            cls=DjangoPartialModelJsonEncoder,
        )

        self.assertEqual(
            resource,
            "{\"pk\": \"%s\", \"type\": \"Datastore\"}" % str(datastore.id),
        )

    def test_encode_uuid_model(self):
        """It should partially encode a Django model.
        """
        workspace = factories.WorkspaceFactory()

        resource = json.dumps(
            workspace,
            cls=DjangoPartialModelJsonEncoder,
        )

        self.assertEqual(
            resource,
            "{\"pk\": \"%s\", \"type\": \"Workspace\"}" % str(workspace.id),
        )

    def test_encode_dictionary(self):
        """It should behave like a generic encoder.
        """
        resource = json.dumps(
            {'id': 1, 'name': 'Test'},
            cls=DjangoPartialModelJsonEncoder,
        )

        self.assertEqual(resource, "{\"id\": 1, \"name\": \"Test\"}")
