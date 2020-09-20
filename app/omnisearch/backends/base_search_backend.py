# -*- coding: utf-8 -*-
import abc


class BaseSearchBackend(metaclass=abc.ABCMeta):
    """ Base interface for a search backend. It only implements one method, `search`, which
        needs to return a list of dictionaries or similar iterable of objects that support __getitem__.
    """

    def __init__(self, workspace, user):
        self.workspace = workspace
        self.user = user

    @abc.abstractmethod
    def search(self, search_query_string, **extra_filters):
        """ Search the backend with a given query string. This needs to return the following signature:

        [
            {'pk': '...', 'model_name': '...', 'score': '...', 'datastore_id': '...'},
            ...
        ]

        We then use those dictionaries to re-build the database objects to return via GraphQL.
        """
        pass
