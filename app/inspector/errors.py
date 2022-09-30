# -*- coding: utf-8 -*-


class OutOfMemoryError(Exception):
    """Thrown when a query returns too many objects.
    """
    def __init__(self, message='Query response was too large to process.'):
        self.message = message
        super().__init__(self.message)
