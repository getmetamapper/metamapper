# -*- coding: utf-8 -*-
import importlib

from django.conf import settings
from utils.shortcuts import load_class


def get_search_backend(workspace, user):
    """BaseSearchBackend: Get the current search backend.
    """
    return load_class(*os.path.splitext(settings.SEARCH_BACKEND))(workspace, user)
