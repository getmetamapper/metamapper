# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.authorization.models as models
import app.authorization.schema as schema
import app.authorization.serializers as serializers
import app.authorization.permissions as permissions

import utils.shortcuts as shortcuts
import utils.mixins.mutations as mixins
import utils.errors as errors


class GrantMembership(mixins.CreateMutationMixin, relay.ClientIDMutation):
    permission_classes = (permissions.WorkspaceOwnersOnly,)

    class Meta:
        serializer_class = serializers.GrantMembershipSerializer

    class Input:
        email = graphene.String(required=True)
        permissions = graphene.String(required=True)

    ok = graphene.Boolean()

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(workspace=info.context.workspace)

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            'ok': (errors is None),
            'errors': errors,
        }
        return cls(**return_kwargs)


class RevokeMembership(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    permission_classes = (permissions.WorkspaceTeamMembersOnly,)

    class Meta:
        serializer_class = serializers.RevokeMembershipSerializer

    class Input:
        email = graphene.String(required=True)

    ok = graphene.Boolean()

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(workspace=info.context.workspace)

    @classmethod
    def get_instance(cls, info, data):
        """It should check permissions as applicable.
        """
        is_owner = info.context.user.is_owner(info.context.workspace.pk)

        if not is_owner and not info.context.user.check_email(data['email']):
            raise errors.PermissionDenied()

        return models.Membership.objects.get(
            user_id=data['email'],
            workspace=info.context.workspace,
        )

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            'ok': (errors is None),
            'errors': errors,
        }
        return cls(**return_kwargs)


class CreateGroup(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Mutation for creating a new Group.
    """
    permission_classes = (permissions.WorkspaceOwnersOnly,)

    class Meta:
        serializer_class = serializers.GroupSerializer

    class Input:
        name = graphene.String(required=True)
        description = graphene.String(required=False)

    group = graphene.Field(schema.GroupType)

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(workspace=info.context.workspace)


class UpdateGroup(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Mutation for updating an existing Group.
    """
    permission_classes = (permissions.WorkspaceOwnersOnly,)

    nullable_fields = ['name', 'description']

    class Meta:
        serializer_class = serializers.GroupSerializer

    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False)

    group = graphene.Field(schema.GroupType)


class DeleteGroup(mixins.DeleteMutationMixin, relay.ClientIDMutation):
    """Permanently remove an existing Group.
    """
    permission_classes = (permissions.WorkspaceOwnersOnly,)

    class Meta:
        serializer_class = serializers.GroupSerializer


class GroupMembershipMixin(mixins.UpdateMutationMixin):
    """Helper mixin for common functionality when interacting with group memberships.
    """
    class Input:
        id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def get_serializer_kwargs(cls, root, info, **data):
        instance = cls.get_instance(info, data)

        if not instance:
            raise errors.PermissionDenied()

        user = shortcuts.from_global_id(data['user_id'], id_only=True)

        return {
            'instance': instance,
            'data': {
                'user': user,
            },
            'context': {
                'request': info.context,
            },
        }

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            'ok': (errors is None),
            'errors': errors,
        }
        return cls(**return_kwargs)


class AddUserToGroup(GroupMembershipMixin, relay.ClientIDMutation):
    """Add the User from a Group.
    """
    permission_classes = (permissions.WorkspaceOwnersOnly,)

    class Meta:
        serializer_class = serializers.AddUserToGroupSerializer


class RemoveUserFromGroup(GroupMembershipMixin, relay.ClientIDMutation):
    """Permanently remove the User from a Group.
    """
    permission_classes = (permissions.WorkspaceOwnersOnly,)

    class Meta:
        serializer_class = serializers.RemoveUserFromGroupSerializer


class Mutation(graphene.ObjectType):
    grant_membership = GrantMembership.Field()
    revoke_membership = RevokeMembership.Field()

    create_group = CreateGroup.Field()
    update_group = UpdateGroup.Field()
    delete_group = DeleteGroup.Field()

    add_user_to_group = AddUserToGroup.Field()
    remove_user_from_group = RemoveUserFromGroup.Field()
