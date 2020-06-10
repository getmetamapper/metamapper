# -*- coding: utf-8 -*-
import graphene

from django.db import IntegrityError
from django.db.models import ProtectedError
from django.http import Http404

from rest_framework import serializers

from graphene import relay

from app.authorization.mixins import AuthMutation

from utils.graphql.types import ErrorType
from utils.errors import PermissionDeniedError, ValidationError


class GenericMutationMixin(AuthMutation):
    """Generic mutation attributes.
    """
    errors = graphene.List(
        ErrorType,
        description="May contain more than one error for same field."
    )

    ok = graphene.Boolean()

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        serializer_class,
        model_name=None,
        lookup_field=None,
        output=None,
        input_fields=None,
        arguments=None,
        name=None,
        **options
    ):
        model_class = None

        if model_name is None:
            serializer_meta = getattr(serializer_class, "Meta", None)
            if serializer_meta:
                model_class = getattr(serializer_meta, "model", None)
                model_name = str(model_class._meta.model_name)

        if lookup_field is None and model_class:
            lookup_field = model_class._meta.pk.name

        cls.lookup_field = lookup_field
        cls.serializer_class = serializer_class
        cls.model_class = model_class
        cls.model_name = model_name

        cls.resource_name = ''

        if cls.model_class:
            cls.resource_name = cls.model_class.__name__

        super().__init_subclass_with_meta__(
            output=output, input_fields=input_fields, arguments=arguments, name=name, **options
        )

    @classmethod
    def get_serializer_kwargs(cls, root, info, **data):
        instance = None
        return {
            "instance": instance,
            "data": data,
            "context": {
                "request": info.context,
            },
        }

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save()

    @classmethod
    def prepare_response(cls, instance, errors):
        return_kwargs = {
            cls.model_name: instance,
            'errors': errors,
        }
        return cls(**return_kwargs)

    @classmethod
    def tasks_on_success(cls, instance, info):
        """List of tasks to dispatch.
        """
        return []

    @classmethod
    def dispatch_tasks(cls, instance, info):
        """Dispatch task calls after a successful mutation.
        """
        tasks = cls.tasks_on_success(instance, info)
        tasks = tasks or []

        for task in tasks:
            task['function'](**task['arguments'])

    @classmethod
    def get_instance(cls, info, data):
        return relay.Node.get_node_from_global_id(info, data[cls.lookup_field])

    @classmethod
    def before_hook(cls, info, instance, data):
        """Perform an action before the mutation is called.
        """
        pass

    @classmethod
    def perform_mutate(cls, serializer, info, **data):
        errors = None
        instance = None
        try:
            instance = cls.perform_save(serializer, info)
        except IntegrityError as exc:
            if 'unique constraint' in str(exc):
                errors = [
                    ErrorType(code='unique', field='none', resource=cls.resource_name)
                ]
        except serializers.ValidationError as e:
            errors = [
                ErrorType(
                    code=codes[0] if isinstance(codes, (list, set,)) else codes,
                    field=field,
                    resource=cls.resource_name,
                )
                for field, codes in e.get_codes().items()
            ]

        return cls.prepare_response(instance, errors)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        """Perform the mutation and return the payload.
        """
        serializer = cls.serializer_class(
            **cls.get_serializer_kwargs(root, info, **data)
        )

        cls.before_hook(info, serializer.instance, data)

        if serializer.is_valid():
            response = cls.perform_mutate(serializer, info)
        else:
            errors = [
                ErrorType(**error_dict)
                for error_dict in serializer.errors
            ]
            response = cls(ok=False, errors=errors)
        if not response.errors:
            cls.dispatch_tasks(serializer.instance, info)
        return response


class CreateMutationMixin(GenericMutationMixin):
    """Mutation mixin for creating a new resource via a DRF serializer.
    """


class UpdateMutationMixin(GenericMutationMixin):
    """Mutation mixin for updating an existing resource via a DRF serializer.
    """
    nullable_fields = []

    class Input:
        id = graphene.ID(required=True)

    @classmethod
    def get_serializer_kwargs(cls, root, info, **data):
        instance = cls.get_instance(info, data)

        if not instance:
            raise PermissionDeniedError()

        data = {
            k: v for k, v in data.items()
            if v or k in cls.nullable_fields or isinstance(v, (bool, list))
        }

        return {
            "instance": instance,
            "data": data,
            "partial": True,
            "context": {
                "request": info.context,
            },
        }


class DeleteMutationMixin(GenericMutationMixin):
    """Mutation mixin for deleting an existing resource via a DRF serializer.
    """
    class Input:
        id = graphene.ID(required=True)

    @classmethod
    def perform_delete(cls, instance, info, **data):
        instance.delete()

    @classmethod
    def prepare_response(cls, instance, errors):
        return_kwargs = {
            'ok': (errors is None),
            'errors': errors,
        }
        return cls(**return_kwargs)

    @classmethod
    def perform_mutate(cls, instance, info, **data):
        errors = None
        try:
            cls.perform_delete(instance, info, **data)
        except ProtectedError:
            errors = [
                ErrorType(code='protected', field='none', resource=cls.resource_name)
            ]
        except ValidationError:
            errors = [
                ErrorType(code='invalid', field='none', resource=cls.resource_name)
            ]
        return cls.prepare_response(instance, errors)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        """Perform the mutation and return the payload.
        """
        instance = cls.get_instance(info, data)

        cls.before_hook(info, instance, data)

        if instance:
            response = cls.perform_mutate(instance, info, **data)
        else:
            raise Http404("Resource was not found.")

        if not response.errors:
            cls.dispatch_tasks(instance, info)

        return response
