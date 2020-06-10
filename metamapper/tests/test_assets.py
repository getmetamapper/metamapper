# -*- coding: utf-8 -*-
import os
import glob
import unittest

from django.conf import settings
from metamapper.views import StaticAssetView


class MetamapperStaticAssetsTest(unittest.TestCase):
    """Base test cases for static asset serving.
    """
    def test_public_folder_is_supported(self):
        """It checks if all of the assets in the public folder are discoverable.
        """
        public_dir = os.path.join(settings.REACT_APP_DIR, 'public', '**', '*')
        list_of_assets = glob.glob(public_dir, recursive=True)

        for asset in list_of_assets:
            if os.path.isdir(asset):
                continue
            basename, ext = os.path.splitext(asset)
            self.assertIn(
                ext[1:],
                StaticAssetView.SUPPORTED_EXTENSIONS.keys(),
                asset,
            )
