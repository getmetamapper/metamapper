# -*- coding: utf-8 -*-
from itertools import chain

from django.db import connection, models
from django.contrib.auth import get_user_model
from django.shortcuts import _get_queryset
from django.utils.text import slugify

from graphql_relay import to_global_id, from_global_id as _from_global_id  # noqa: F401

from utils.errors import NotFound


def get_object_or_404(klass, message=None, exception_class=NotFound, *args, **kwargs):
    """
    Use get() to return an object, or raise a Http404 exception if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Like with QuerySet.get(), MultipleObjectsReturned is raised if more than
    one object is found.
    """
    queryset = _get_queryset(klass)
    if not hasattr(queryset, 'get'):
        klass__name = klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_object_or_404() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        if not message:
            message = 'Resource was not found.'
        raise exception_class(message)


def run_raw_sql(sql, params=None):
    """Execute raw SQL against the Postgres database.
    """
    with connection.cursor() as cursor:
        if params is not None:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)


def generate_unique_slug(klass, field):
    """
    return unique slug if origin slug is exist.
    eg: `foo-bar` => `foo-bar-1`

    :param `klass` is Class model.
    :param `field` is specific field for title.
    """
    origin_slug = slugify(field)
    unique_slug = origin_slug
    numb = 1
    while klass.objects.filter(slug__iexact=unique_slug).exists():
        unique_slug = '%s-%d' % (origin_slug, numb)
        numb += 1
    return unique_slug


def get_user_id(user):
    """Return the user ID from User model.
    """
    if isinstance(user, (get_user_model(),)):
        return user.id
    return user


def model_to_dict(instance, fields=None, exclude=None):
    """
    Return a dict containing the data in ``instance`` suitable for passing as
    a Form's ``initial`` keyword argument.

    ``fields`` is an optional list of field names. If provided, return only the
    named.

    ``exclude`` is an optional list of field names. If provided, exclude the
    named from the returned dict, even if they are listed in the ``fields``
    argument.
    """
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if not getattr(f, 'editable', False):
            continue
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        field_name = f.name
        if isinstance(f, models.ForeignKey):
            field_name += '_id'
        data[field_name] = f.value_from_object(instance)
    return data


def dict_list_eq(l1, l2):
    """Compare to lists of dictionaries for equality.
    """
    sorted_l1 = sorted(sorted(d.items()) for d in l1)
    sorted_l2 = sorted(sorted(d.items()) for d in l2)
    return sorted_l1 == sorted_l2


def camel_case(st):
    output = ''.join(x for x in st.title() if x.isalnum())
    return output[0].lower() + output[1:]


def from_global_id(global_id, id_only=False):
    type_, id_ = _from_global_id(global_id)

    if id_only:
        return id_

    return type_, id_
