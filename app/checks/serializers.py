# -*- coding: utf-8 -*-
from datetime import timedelta
from hashlib import md5
from jinja2 import Template

from django.db import transaction
from rest_framework import serializers

from app.checks.models import Check, CheckAlertRule, CheckExpectation, CheckQuery
from app.checks.tasks import expectations, pass_values
from app.checks.tasks.context import CheckContext

from app.inspector import service as inspector

from utils.mixins.serializers import MetamapperSerializer
from utils.shortcuts import epoch_now, from_global_id


class CheckExpectationSerializer(MetamapperSerializer, serializers.ModelSerializer):
    class Meta:
        model = CheckExpectation
        fields = (
            'handler_class',
            'handler_input',
            'pass_value_class',
            'pass_value_input',)

    def validate_handler_class(self, handler_class):
        """Test to see if the `handler` class is supported.
        """
        if expectations.validator.is_valid_class(handler_class):
            return handler_class
        raise serializers.ValidationError('Assertion handler is invalid.')

    def validate_pass_value_class(self, pass_value_class):
        """Test to see if the `pass_value` class is supported.
        """
        if pass_values.validator.is_valid_class(pass_value_class):
            return pass_value_class
        raise serializers.ValidationError('Pass value handler is invalid.')

    def run_field_validation(self, field, name, value):
        """Run validators for the provided field.
        """
        try:
            field.run_validation(value)
        except serializers.ValidationError as error:
            raise serializers.ValidationError(
                {name: error.detail}, error.detail[0].code)

    def validate(self, data):
        """Test to see if the input values are valid.
        """
        handler_class = expectations.validator.get_class(data['handler_class'])
        handler_input = data.get('handler_input', {})
        for name, field in handler_class.get_fields():
            self.run_field_validation(field, name, handler_input.get(name))

        pass_value_class = pass_values.validator.get_class(data['pass_value_class'])
        pass_value_input = data.get('pass_value_input', {})
        for name, field in pass_value_class.get_fields():
            self.run_field_validation(field, name, pass_value_input.get(name))

        return data

    def initialize(self, **extras):
        return CheckExpectation(**{**extras, **self.validated_data})

    def create(self, validated_data):
        return CheckExpectation.objects.create(job=self.context['check'], **validated_data)


class CheckQuerySerializer(MetamapperSerializer, serializers.ModelSerializer):
    sql_text = serializers.CharField(required=True, max_length=None)
    interval = serializers.DurationField(min_value=timedelta(minutes=30))

    class Meta:
        model = CheckQuery
        fields = ('sql_text', 'interval',)

    def validate_sql_text(self, sql_text):
        if sql_text.split()[0].upper() not in ('SELECT', 'WITH'):
            raise serializers.ValidationError('SQL is not valid.', 'select_only')
        return sql_text

    def validate_interval(self, interval):
        if interval not in Check.INTERVAL_CHOICES:
            raise serializers.ValidationError('Interval is not valid.')
        return interval

    def create(self, validated_data):
        validated_data.pop('interval', None)
        key = md5(validated_data['sql_text'].encode()).hexdigest()
        try:
            instance = CheckQuery.objects.get(key=key)
        except CheckQuery.DoesNotExist:
            instance = CheckQuery(key=key, datastore=self.context['datastore'], **validated_data)
            instance.save()
        return instance

    def update(self, instance, validated_data):
        raise NotImplementedError('CheckQuerySerializer.update() cannot be performed.')

    def get_catchable_errors(self):
        return inspector.get_engine(self.context['datastore']).catchable_errors

    def get_dataframe(self):
        context = CheckContext(epoch_now(), self.validated_data['interval'])
        sql_template = Template(self.validated_data['sql_text'])
        sql = sql_template.render(**context.to_dict())
        get_kwargs = {
            'datastore': self.context['datastore'],
            'sql': sql,
            'record_limit': 50,
        }
        dataframe = inspector.get_dataframe(**get_kwargs)
        for x in dataframe.select_dtypes(exclude=['number']).columns.tolist():
            dataframe[x] = dataframe[x].astype(str)
        return dataframe


class CheckSerializer(MetamapperSerializer, serializers.ModelSerializer):
    name = serializers.CharField(max_length=50, trim_whitespace=True)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=30, trim_whitespace=True),
        max_length=10,
        allow_empty=True,
        allow_null=True,
        required=False,
    )

    is_enabled = serializers.BooleanField(default=True)
    short_desc = serializers.CharField(
        max_length=140,
        allow_null=True,
        allow_blank=True,
        trim_whitespace=True,
        required=False,
    )

    interval = serializers.DurationField(min_value=timedelta(minutes=30))
    query_id = serializers.CharField(max_length=None)

    expectations = CheckExpectationSerializer(required=True, many=True)

    class Meta:
        model = Check
        fields = (
            'name',
            'tags',
            'is_enabled',
            'short_desc',
            'interval',
            'query_id',
            'expectations',)

    def validate_query_id(self, query_id):
        """We should verify that the provided query exists and is scoped to the workspace.
        """
        query_id = from_global_id(query_id, id_only=True)
        queryset = CheckQuery.objects.filter(id=query_id, workspace=self.context['request'].workspace)
        if not queryset.exists():
            raise serializers.ValidationError('Query is not valid.', 'exists')
        return query_id

    def validate_interval(self, interval):
        """We should ensure that the interval is supported by our processing engine.
        """
        if interval not in Check.INTERVAL_CHOICES:
            raise serializers.ValidationError('Interval is not valid.')
        return interval

    def validate_short_desc(self, short_desc):
        """We should convert null descriptions to blank.
        """
        return '' if short_desc is None else short_desc

    def validate_tags(self, tags):
        """We should remove any duplicate tags that exist.
        """
        return list(set(tags)) if isinstance(tags, (list,)) else []

    def validate_expectations(self, expectations):
        """We should have at least one expectation provided.
        """
        if not len(expectations):
            raise serializers.ValidationError('Check must have at least one expectation.', 'empty')
        return expectations

    def create(self, validated_data):
        """Create a brand new Check instance.
        """
        expectations = validated_data.pop('expectations', [])
        with transaction.atomic():
            check = Check.objects.create(datastore=self.context['datastore'], **validated_data)
            if check.id:
                expectations = [
                    CheckExpectation(
                        job_id=check.id,
                        workspace_id=check.workspace_id,
                        **expectation,
                    )
                    for expectation in expectations
                ]
                CheckExpectation.objects.bulk_create(expectations, ignore_conflicts=True)
        return check

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.is_enabled = validated_data.get('is_enabled', instance.is_enabled)
        instance.short_desc = validated_data.get('short_desc', instance.short_desc)
        instance.interval = validated_data.get('interval', instance.interval)
        instance.query_id = validated_data.get('query_id', instance.query_id)
        instance.save()
        return instance


class EmailAlertConfigValidator(serializers.Serializer):
    """Validate the configuration struct for an email alert channel.
    """
    emails = serializers.ListField(child=serializers.EmailField(), allow_empty=False)


class CheckAlertRuleSerializer(MetamapperSerializer, serializers.ModelSerializer):
    name = serializers.CharField(max_length=50, trim_whitespace=True)
    interval = serializers.DurationField(min_value=timedelta(minutes=30))
    channel = serializers.ChoiceField(required=True, choices=[c[0] for c in CheckAlertRule.CHANNEL_CHOICES])
    channel_config = serializers.JSONField(required=True)

    class Meta:
        model = CheckAlertRule
        fields = ('name', 'interval', 'channel', 'channel_config',)

    def validate_interval(self, interval):
        if interval not in Check.INTERVAL_CHOICES:
            raise serializers.ValidationError('Interval is not valid.')
        return interval

    def validate_email(self, data):
        """Validators for EMAIL type.
        """
        validator = EmailAlertConfigValidator(data=data)
        validator.is_valid(raise_exception=True)
        return validator.data

    def validate(self, data):
        """Handle custom validation based on the `channel_config` value.
        """
        field_type = self.instance.channel if self.instance else data['channel']
        validators = {
            CheckAlertRule.EMAIL: self.validate_email,
        }
        data['channel_config'] = validators[field_type](data.get('channel_config', {}))
        return data

    def create(self, validated_data):
        """Create a brand new CheckAlertRule instance.
        """
        return CheckAlertRule.objects.create(job=self.context['check'], **validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.interval = validated_data.get('interval', instance.interval)
        instance.channel_config = validated_data.get('channel_config', instance.channel_config)
        instance.save()
        return instance
