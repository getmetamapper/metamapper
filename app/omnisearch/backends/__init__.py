# -*- coding: utf-8 -*-
import importlib
import os

from django.conf import settings


module_name, class_name = os.path.splitext(settings.SEARCH_BACKEND)

SearchBackend = getattr(importlib.import_module(module_name), class_name[1:])


def get_search_backend():
    """BaseSearchBackend: Get the current search backend.
    """
    return SearchBackend()
