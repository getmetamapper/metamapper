# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.authorization.models as models
import app.authorization.serializers as serializers
import app.authorization.permissions as permissions

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
    def prepare_response(cls, instance, errors):
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
    def prepare_response(cls, instance, errors):
        return_kwargs = {
            'ok': (errors is None),
            'errors': errors,
        }
        return cls(**return_kwargs)


class Mutation(graphene.ObjectType):
    grant_membership = GrantMembership.Field()
    revoke_membership = RevokeMembership.Field()
