# -*- coding: utf-8 -*-
import graphene

from graphene_django.filter import DjangoFilterConnectionField

from app.authorization.permissions import AllowAuthenticated
from utils.errors import PermissionDeniedError


class AuthNode(object):
    """Permission mixin for queries.
    """
    permission_classes = (AllowAuthenticated,)
    scope_to_workspace = False

    pk = graphene.String()

    @classmethod
    def query_for_node(cls, info, id):
        qs = cls._meta.model.objects
        if cls.scope_to_workspace:
            qs = qs.filter(workspace=info.context.workspace)
        return qs.get(id=id)

    @classmethod
    def get_node(cls, info, id):
        if all((perm().has_node_permission(info) for perm in cls.permission_classes)):
            try:
                object_instance = cls.query_for_node(info, id)
            except cls._meta.model.DoesNotExist:
                object_instance = None
            return object_instance
        else:
            raise PermissionDeniedError()

    def resolve_pk(instance, info):
        if isinstance(instance.pk, (float, int)):
            return None
        return instance.pk


class AuthMutation(object):
    """Permission mixin for ClientIdMutation.
    """
    permission_classes = (AllowAuthenticated,)

    @classmethod
    def mutate(cls, root, info, input):
        if not cls.has_permission(root, info, input):
            raise PermissionDeniedError()
        return super().mutate(root, info, input)

    @classmethod
    def has_permission(cls, root, info, input):
        return all(
            (perm().has_mutation_permission(root, info, input) for perm in cls.permission_classes)
        )


class AuthConnectionField(DjangoFilterConnectionField):
    """Custom ConnectionField for permission system.
    """
    scope_to_workspace = False

    @classmethod
    def has_permission(cls, info, permission_classes):
        return all(
            (perm().has_filter_permission(info) for perm in permission_classes)
        )

    @classmethod
    def connection_resolver(
        cls,
        resolver,
        connection,
        default_manager,
        max_limit,
        enforce_first_or_last,
        filterset_class,
        filtering_args,
        root,
        info,
        **args
    ):
        filter_kwargs = {k: v for k, v in args.items() if k in filtering_args}
        qs = filterset_class(
            data=filter_kwargs,
            queryset=default_manager.get_queryset(),
            request=info.context,
        ).qs

        node = connection._meta.node

        if node.scope_to_workspace:
            qs = qs.filter(workspace=info.context.workspace)

        if not cls.has_permission(info, node.permission_classes):
            raise PermissionDeniedError()

        return super(DjangoFilterConnectionField, cls).connection_resolver(
            resolver,
            connection,
            qs,
            max_limit,
            enforce_first_or_last,
            root,
            info,
            **args
        )
