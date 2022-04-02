# -*- coding: utf-8 -*-
from rest_framework import serializers


class ApiSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        for field_name, field in fields.items():
            field.read_only = field_name not in self.Meta.writable_fields
        return fields
