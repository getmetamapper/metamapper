# -*- coding: utf-8 -*-
import functools

import app.comments.models as comments
import app.definitions.models as models

import utils.errors as errors
import utils.shortcuts as shortcuts

from guardian.shortcuts import get_objects_for_user


def request_can_view_datastore(info, datastore, check_if_owner=True):
    """Check to see if a GraphQL context can view a datastore.
    """
    if check_if_owner and info.context.user.is_owner(info.context.workspace.id):
        return True
    # If the datastore does not have object permissions enabled, we can just return it.
    if not datastore.object_permissions_enabled:
        return True
    # Otherwise, we need to check if the specific user has access to the datastore.
    return info.context.user.has_perm('definitions.view_datastore', datastore)


def can_view_datastore_objects(wrapper_fcn=None):
    """Decorator to check if datastore permission check passes.
    """
    def the_decorator(func):
        @functools.wraps(func)
        def func_wrapper(self, info, *args, **kwargs):
            # We should not proceed if the user isn't authenticated.
            if not info.context.user.is_authenticated:
                raise errors.PermissionDenied()
            instance = func(self, info, *args, **kwargs)
            # Owners have super user power within a workspace.
            if info.context.user.is_owner(info.context.workspace.id):
                return instance
            # We grab the datastore with the helper function if needed. Example would
            # be when we return a table definition and need to get the related datastore.
            if callable(wrapper_fcn):
                datastore = wrapper_fcn(instance)
            else:
                datastore = instance
            # Use helper function to conduct datastore permission check.
            if not request_can_view_datastore(info, datastore, check_if_owner=False):
                raise errors.PermissionDenied()
            return instance
        return func_wrapper
    return the_decorator


def get_datastores_for_user(queryset, user):
    """Filters the datastores that the current user can view based on object-level permissions.
    """
    guardian_kwargs = {
        'user': user,
        'perms': ['definitions.view_datastore'],
        'klass': queryset,
        'use_groups': True,
        'any_perm': True,
        'with_superuser': False,
        'accept_global_perms': False,
    }
    return (get_objects_for_user(**guardian_kwargs) | queryset.filter(object_permissions_enabled=False)).distinct()


def get_datastore_from_global_id(attributes, attribute_lookup_field):
    """Retrieve the datastore for the permission check.
    """
    nodetype, pk = shortcuts.from_global_id(attributes[attribute_lookup_field])
    lookup_field = 'pk'
    if nodetype == 'SchemaType':
        lookup_field = 'schemas__pk'
    elif nodetype == 'TableType':
        lookup_field = 'schemas__tables__pk'
    elif nodetype == 'ColumnType':
        lookup_field = 'schemas__tables__columns__pk'
    elif nodetype == 'CheckType':
        lookup_field = 'checks__pk'
    elif nodetype == 'CheckAlertRuleType':
        lookup_field = 'checks__alert_rules__pk'
    elif nodetype == 'CheckExpectationType':
        lookup_field = 'checks__expectations__pk'
    elif nodetype == 'AssetOwnerType':
        asset_owner = models.AssetOwner.objects.filter(pk=pk).first()
        if not asset_owner:
            return None
        pk = asset_owner.content_object.datastore_id
    elif nodetype == 'CommentType':
        comment = comments.Comment.objects.filter(pk=pk).first()
        if not comment:
            return None
        pk = comment.content_object.datastore_id
    return models.Datastore.objects.filter(**{lookup_field: pk}).first()


def CanPerformDatastoreMutation(perm, lookup_field='id', ignore_limited_access_check=False):
    """Allows performing action if user has permission in database.
    """
    class InnerObjectPermissionChecker(object):
        @staticmethod
        def has_mutation_permission(root, info, input):
            datastore = get_datastore_from_global_id(input, lookup_field)
            if datastore is None:
                return False
            if not ignore_limited_access_check and not datastore.object_permissions_enabled:
                return True
            if info.context.user.is_owner(info.context.workspace.id):
                return True
            return info.context.user.has_perm('definitions.%s' % perm, datastore)
    return InnerObjectPermissionChecker


CanUpdateDatastoreMetadata = CanPerformDatastoreMutation('change_datastore_metadata')

CanUpdateDatastoreSettings = CanPerformDatastoreMutation('change_datastore_settings')

CanUpdateDatastoreConnection = CanPerformDatastoreMutation('change_datastore_connection')

CanUpdateDatastoreAccess = CanPerformDatastoreMutation('change_datastore_access', ignore_limited_access_check=True)

CanCreateDatastoreChecks = CanPerformDatastoreMutation('change_datastore_checks', 'datastore_id')

CanManageDatastoreChecks = CanPerformDatastoreMutation('change_datastore_checks')

CanDeleteDatastore = CanPerformDatastoreMutation('change_datastore_connection')

CanUpdateCustomProperties = CanPerformDatastoreMutation('change_datastore_metadata', 'object_id')

CanCreateCommentOnDatastore = CanPerformDatastoreMutation('comment_on_datastore', 'object_id')

CanModifyCommentOnDatastore = CanPerformDatastoreMutation('comment_on_datastore', 'id')

CanCreateAssetOwner = CanPerformDatastoreMutation('change_datastore_metadata', 'object_id')
