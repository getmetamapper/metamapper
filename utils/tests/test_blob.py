# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock
import json

import utils.blob as blob
import utils.gzip as gzip

from django.core.files.base import ContentFile


class UtilsBlobTests(unittest.TestCase):
    """Tests interactions with blob storage like S3 or GCP.
    """
    data = [
        {'id': 1, 'name': 'Shaun Spencer'},
        {'id': 2, 'name': 'Burton Guster'},
        {'id': 3, 'name': 'Henry Spencer'},
    ]

    @mock.patch('django.core.files.storage.default_storage.open')
    def test_get_object_raw(self, mock_open):
        """It should find and decode plaintext files.
        """
        path = "/path/to/object"
        file = mock.MagicMock()
        file.read.return_value = json.dumps(self.data).encode()
        mock_open.return_value.__enter__.return_value = file

        result = blob.get_object(path)

        self.assertEqual(result, self.data)
        self.assertTrue(mock_open.called_with(path))

    @mock.patch('django.core.files.storage.default_storage.open')
    def test_get_object_gzipped(self, mock_open):
        """It should find and decode gzip files.
        """
        path = "/path/to/object"
        file = mock.MagicMock()
        file.read.return_value = gzip.gzip_bytes(json.dumps(self.data)).getvalue()
        mock_open.return_value.__enter__.return_value = file

        result = blob.get_object(path)

        self.assertEqual(result, self.data)
        self.assertTrue(mock_open.called_with(path))

    @mock.patch('django.core.files.storage.default_storage.save')
    @mock.patch('django.core.files.storage.default_storage.exists')
    @mock.patch('django.core.files.storage.default_storage.delete')
    def test_put_object_raw(self, mock_save, mock_exists, mock_delete):
        """It should take the raw content and upload it.
        """
        mock_exists.return_value = True

        f_path = "/path/to/file"
        blob.put_object(f_path, self.data, gzipped=False)

        file = ContentFile(json.dumps(self.data))

        self.assertTrue(mock_save.called_with(f_path, file))
        self.assertTrue(mock_delete.called_with(f_path))
