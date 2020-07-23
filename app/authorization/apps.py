# -*- coding: utf-8 -*-
from django.apps import AppConfig


class Config(AppConfig):
    name = 'app.authorization'

    def ready(self):
        import app.authorization.signals as signals  # noqa: F401
