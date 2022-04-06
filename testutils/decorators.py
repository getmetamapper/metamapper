# -*- coding: utf-8 -*-
import functools
import testutils.helpers as helpers


def as_someone(user_types):
    """Decorator to mimic different user roles.
    """
    def the_decorator(func):
        @functools.wraps(func)
        def func_wrapper(view, *args, **kwargs):
            cached_user = view.user
            for user_type in user_types:
                view.user_type = user_type
                view.user = view.users[user_type]
                view._client = helpers.graphql_client(view.user, uuid=view.workspace.id)
                func(view, *args, **kwargs)
            view.user = cached_user
            view._client = helpers.graphql_client(view.user)
        return func_wrapper
    return the_decorator
