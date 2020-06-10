# -*- coding: utf-8 -*-
from graphene_django.filter import DjangoFilterConnectionField

from utils.errors import PermissionDeniedError

from graphene.types import String
from graphene.types.field import Field
from graphene.utils.get_unbound_function import get_unbound_function


def wrap_resolver(cls, resolver):
    def wrapped_resolver(root, info, **args):
        try:
            return resolver(root, info, **args)
        except PermissionDeniedError as e:
            return cls(errors=str(e))
    return wrapped_resolver


class AuthConnectionField(DjangoFilterConnectionField):
    """Custom ConnectionField for permission system.
    """
    scope_to_workspace = False

    @classmethod
    def __init_subclass_with_meta__(cls, resolver=None, **options):
        if not resolver:
            mutate = getattr(cls, 'mutate', None)
            assert mutate, 'All mutations must define a mutate method in it'
            resolver = get_unbound_function(mutate)
            resolver = wrap_resolver(cls, resolver)

        super().__init_subclass_with_meta__(resolver, **options)
        cls._meta.fields['errors'] = (Field(String, name='errors'))

    @classmethod
    def has_permission(cls, info, permission_classes):
        return all(
            (perm().has_filter_permission(info) for perm in permission_classes)
        )

    @classmethod
    def resolve_queryset(
        cls, connection, iterable, info, args, filtering_args, filterset_class
    ):
        node = connection._meta.node

        if not cls.has_permission(info, node.permission_classes):
            raise PermissionDeniedError()

        qs = super().resolve_queryset(connection, iterable, info, args, filtering_args, filterset_class)

        if node.scope_to_workspace:
            qs = qs.filter(workspace=info.context.workspace)

        return qs
