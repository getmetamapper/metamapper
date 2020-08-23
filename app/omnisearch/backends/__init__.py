# -*- coding: utf-8 -*-
import importlib
import os

from django.conf import settings


module_name, class_name = os.path.splitext(settings.SEARCH_BACKEND)


def get_search_backend(workspace, user):
    """BaseSearchBackend: Get the current search backend.
    """
    return getattr(importlib.import_module(module_name), class_name[1:])(workspace, user)
