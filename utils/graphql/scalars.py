# -*- coding: utf-8 -*-
import graphene


class Upload(graphene.types.Scalar):
    """Create scalar that ignores normal serialization/deserialization, since
    that will be handled by the multipart request spec"""

    @staticmethod
    def serialize(value):
        return value

    @staticmethod
    def parse_literal(node):
        return node

    @staticmethod
    def parse_value(value):
        return value


class JSONObject(graphene.types.Scalar):
    """Handle serialization/deserialization of a JSON object.
    """
    @staticmethod
    def serialize(value):
        return value

    @staticmethod
    def parse_literal(node):
        return node

    @staticmethod
    def parse_value(value):
        return value
