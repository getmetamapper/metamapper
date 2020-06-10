# -*- coding: utf-8 -*-
from django.db import models

from utils.postgres.managers import PostgresManager


class ActionManager(PostgresManager, models.Manager):
    """Django manager for the `audit.Action` model.
    """
