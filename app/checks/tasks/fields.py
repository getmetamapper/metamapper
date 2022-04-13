# -*- coding: utf-8 -*-
from rest_framework import serializers


class CharField(serializers.CharField):
    def get_options(self):
        return dict(maxLength=self.max_length)


class ChoiceField(serializers.ChoiceField):
    def get_options(self):
        return dict(choices=list(self.choices))


class IntegerField(serializers.IntegerField):
    def get_options(self):
        return None


class ColumnField(CharField):
    def get_options(self):
        return None


class BooleanField(serializers.BooleanField):
    def get_options(self):
        return None
