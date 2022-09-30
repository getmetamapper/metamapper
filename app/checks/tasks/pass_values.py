# -*- coding: utf-8 -*-
import metamapper.fields as fields

from django.db.models import Avg, Max, Min, Sum

from app.checks.tasks.base import PassValue

from utils.shortcuts import epoch_now, get_module_class_validator, load_class


__all__ = ['Constant', 'Rollup']


AGGREGATOR_MAPPING = {
    'average': Avg,
    'maximum': Max,
    'minimum': Min,
    'sum': Sum,
}

AGGREGATOR_CHOICES = [k for k in AGGREGATOR_MAPPING.keys()]


validator = get_module_class_validator(__name__, __all__)


def get_handler_configuration_options():
    """Return the configuration options for each handler.
    """
    output = []
    for handler_class in __all__:
        handler = load_class(__name__, handler_class)
        handler_fields = handler.get_fields()
        handler_kwargs = {
            'name': getattr(handler.Meta, 'name', None),
            'info': getattr(handler.Meta, 'info', None),
            'handler': '.'.join([__name__, handler_class]),
            'details': [
                {
                    'name': name,
                    'type': field.__class__.__name__,
                    'label': field.label,
                    'options': field.get_options(),
                    'help_text': field.help_text,
                }
                for name, field in handler_fields
            ],
        }
        output.append(handler_kwargs)
    return output


class Constant(PassValue):
    """Pass with a constant value.
    """
    class Input:
        value = fields.IntegerField(label='Value')

    class Meta:
        info = 'a constant value'
        desc = '{{ value }}'

    def get(self):
        return self.inputs['value']


class Rollup(PassValue):
    """Pass with an aggregation of past run outputs.
    """
    class Input:
        interval = fields.IntegerField(
            label='Interval',
            help_text='Time (in seconds) of past observed values to consider.')
        aggregator = fields.ChoiceField(
            label='Aggregator',
            choices=AGGREGATOR_CHOICES,
            help_text='Defines how observed values are aggregated within a given time interval.')

    class Meta:
        info = 'a rollup of previously observed values'
        desc = '{{ aggregator }} observed value over the past {{ interval }} seconds'

    @property
    def aggregator(self):
        return AGGREGATOR_MAPPING[self.inputs['aggregator']]

    def get(self):
        within = epoch_now() - self.inputs['interval']
        result = self.expectation.past_results.filter(epoch__gte=within)
        result = result.aggregate(result=self.aggregator('observed_value'))
        return result['result']
