# -*- coding: utf-8 -*-
from enum import Enum


class ConflictAction(Enum):
    """Possible actions to take on a conflict.
    """
    NOTHING = "NOTHING"
    UPDATE = "UPDATE"

    @classmethod
    def all(cls):
        return [choice for choice in cls]
