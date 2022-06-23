# -*- coding: utf-8 -*-
from django.apps import apps
from rest_framework import serializers


class FieldMixin(object):
    def get_options(self, *args, **kwargs):
        return None


class CharField(FieldMixin, serializers.CharField):
    def get_options(self, *args, **kwargs):
        return dict(maxLength=self.max_length)


class ChoiceField(FieldMixin, serializers.ChoiceField):
    def get_options(self, *args, **kwargs):
        return dict(choices=list(self.choices))


class IntegerField(FieldMixin, serializers.IntegerField):
    pass


class ColumnField(FieldMixin, serializers.CharField):
    pass


class ColumnsField(FieldMixin, serializers.ListField):
    pass


class BooleanField(FieldMixin, serializers.BooleanField):
    pass


class EmailsField(FieldMixin, serializers.ListField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, child=serializers.EmailField(), **kwargs)


class IntegrationField(FieldMixin, serializers.CharField):
    def get_options(self, integration, workspace):
        """Return list of integrations associated with this request.
        """
        IntegrationConfig = apps.get_model(
            app_label='integrations',
            model_name='IntegrationConfig',
        )
        integrations = IntegrationConfig.objects.filter(
            integration=integration,
            workspace=workspace,
        ).values('id', 'displayable')
        options = []
        for integration in integrations:
            options.append({'label': integration['displayable'], 'value': integration['id']})
        return options
