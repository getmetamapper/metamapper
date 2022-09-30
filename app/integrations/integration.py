# -*- coding: utf-8 -*-
from abc import ABC
from rest_framework import serializers


class Tags(object):
    """Structure for holding tags constants.
    """
    ALERTING = "Alerting"


class Integration(ABC):
    """Representation of an integration within Metamapper.
    """
    integration_name = None

    tags = []

    class Meta:
        auth_keys = []
        validator = None
        displayable_key = None

    @classmethod
    def get_fields(cls):
        d = {}
        for k, v in cls.Meta.validator().fields.items():
            if isinstance(v, serializers.Field):
                d[k] = v
        return [(k, v) for k, v in d.items()]

    @classmethod
    def auth_in(cls, *args):
        return ":".join(map(str, args))

    @classmethod
    def displayable_in(cls, *args):
        return "".join(map(str, args))

    @classmethod
    def auth_out(cls, config):
        return config.auth

    @classmethod
    def displayable_out(cls, config):
        return config.displayable
