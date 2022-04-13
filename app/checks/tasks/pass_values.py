# -*- coding: utf-8 -*-
from app.checks.tasks.base import PassValue
from app.checks.tasks import fields

from utils.shortcuts import get_module_class_validator, load_class


__all__ = ['Constant']


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
