# -*- coding: utf-8 -*-
from graphql_jwt.decorators import user_passes_test

from app.authentication.models import Membership

from utils.errors import PermissionDenied

from functools import wraps


login_required = user_passes_test(lambda u: u.is_authenticated, PermissionDenied)


def check_for_permissions(context, permissions_list):
    """Helper function for parsing workspace-level permissions.
    """
    if not (context.user and context.user.is_authenticated):
        return False

    if not hasattr(context, 'workspace') or not context.workspace:
        return False

    return context.user.permissions_for(context.workspace.id) in permissions_list


class AllowAny(object):
    """Default authorization class. Allows any user for any action.
    """
    @staticmethod
    def has_node_permission(info):
        return True

    @staticmethod
    def has_mutation_permission(root, info, input):
        return True

    @staticmethod
    def has_filter_permission(info):
        return True


class AllowAuthenticated(object):
    """Allows performing action only for logged in users.
    """
    @staticmethod
    def has_node_permission(info):
        return info.context.user.is_authenticated

    @staticmethod
    def has_mutation_permission(root, info, input):
        return info.context.user.is_authenticated

    @staticmethod
    def has_filter_permission(info):
        return info.context.user.is_authenticated


class WorkspaceTeamMembersOnly(object):
    """Allows performing action only for logged in users that belong to the provided workspace.
    """
    @staticmethod
    def has_node_permission(info):
        return check_for_permissions(info.context, Membership.PERMISSION_GROUPS)

    @staticmethod
    def has_mutation_permission(root, info, input):
        """Read-only users cannot perform mutations.
        """
        return check_for_permissions(info.context, Membership.PERMISSION_GROUPS)

    @staticmethod
    def has_filter_permission(info):
        return check_for_permissions(info.context, Membership.PERMISSION_GROUPS)


class WorkspaceWriteAccessOnly(object):
    """Allows performing action only for logged in owners that belong to the provided workspace.
    """
    @staticmethod
    def has_node_permission(info):
        return check_for_permissions(info.context, [Membership.MEMBER, Membership.OWNER])

    @staticmethod
    def has_mutation_permission(root, info, input):
        return check_for_permissions(info.context, [Membership.MEMBER, Membership.OWNER])

    @staticmethod
    def has_filter_permission(info):
        return check_for_permissions(info.context, [Membership.MEMBER, Membership.OWNER])


class WorkspaceOwnersOnly(object):
    """Allows performing action only for the owner of a workspace.
    """
    @staticmethod
    def has_node_permission(info):
        return check_for_permissions(info.context, [Membership.OWNER])

    @staticmethod
    def has_mutation_permission(root, info, input):
        return check_for_permissions(info.context, [Membership.OWNER])

    @staticmethod
    def has_filter_permission(info):
        return check_for_permissions(info.context, [Membership.OWNER])


def permissions_required(permission_classes=(AllowAuthenticated,)):
    """Decorator to check if permission classes are met.
    """
    def the_decorator(func):
        @wraps(func)
        def func_wrapper(self, info, *args, **kwargs):
            if not all((perm().has_filter_permission(info) for perm in permission_classes)):
                raise PermissionDenied()
            return func(self, info, *args, **kwargs)
        return func_wrapper
    return the_decorator
